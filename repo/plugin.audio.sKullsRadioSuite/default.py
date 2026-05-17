import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmcvfs
import urllib.parse
import os
import json
import datetime
import requests
import zipfile
import shutil
import re
import hashlib
import tempfile
import traceback

# --- Konstanten für Dateinamen/Endungen ---
HISTORY_LOG_FILE = "backup_history.log"
AUTO_BACKUP_MARK_FILE = "auto_backup_last.txt"
ZIP_TAG_EXTENSION = ".tag"
BROKEN_JSON_PREFIX = ".broken_"
BACKUP_SUFFIX = ".bak_"
ENCRYPTED_EXTENSION = ".enc"

# Initialisierung
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_ID = ADDON.getAddonInfo("id")  # Für korrekte Plugin-URLs
BASE_URL = f"plugin://{ADDON_ID}/"  # WICHTIG: Muss mit addon.xml ID übereinstimmen

# Debug-Logging
xbmc.log(f"[{ADDON_NAME}] Addon gestartet von: {sys.argv}", xbmc.LOGINFO)

# Verschlüsselung (erst nach Konstanten initialisieren)
AES_Cipher = None
PBKDF2 = None
try:
    from Cryptodome.Cipher import AES as AES_Cipher
    from Cryptodome.Random import get_random_bytes
    from Cryptodome.Util.Padding import pad, unpad
    from Cryptodome.Protocol.KDF import PBKDF2

    xbmc.log(f"[{ADDON_NAME}] PyCryptodomex erfolgreich geladen", xbmc.LOGINFO)
except ImportError:
    try:
        from Crypto.Cipher import AES as AES_Cipher  # Fallback für alte Installationen
        from Crypto.Protocol.KDF import PBKDF2

        xbmc.log(f"[{ADDON_NAME}] PyCryptodome gefunden", xbmc.LOGINFO)
    except ImportError:
        xbmc.log(
            f"[{ADDON_NAME}] Keine Verschlüsselungsbibliothek gefunden", xbmc.LOGWARNING
        )

# Backup-Manager importieren (nach allen anderen Definitionen)
try:
    from backup_manager import BackupManager
except ImportError as e:
    xbmc.log(
        f"[{ADDON_NAME}] BackupManager konnte nicht geladen werden: {str(e)}",
        xbmc.LOGERROR,
    )
    BackupManager = None  # Fallback definieren


# --- Basis: Addon-Umgebung ---
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
# For general UI icons (zip.png, log.png etc.)
MEDIA_ICON_PATH = "special://home/addons/plugin.audio.sKullsRadioSuite/resources/media"

# Pfade für Stream- und Kategoriebilder
IMAGES_BASE_DIR = os.path.join(ADDON_DIR, "resources", "images")
IMAGES_CATEGORIES_DIR = os.path.join(IMAGES_BASE_DIR, "kategorien")
IMAGES_STREAMS_DIR = os.path.join(IMAGES_BASE_DIR, "streams")

HISTORY_LOG = os.path.join(ADDON_DIR, HISTORY_LOG_FILE)
AUTO_BACKUP_MARK = os.path.join(ADDON_DIR, AUTO_BACKUP_MARK_FILE)

STREAMS_JSON = os.path.join(ADDON_DIR, "streams.json")
RECENT_DAYS = 10

# NEU: Mapping für Debug-Logging-Stufen
LOG_LEVEL_MAP = {
    # Schwellenwert: INFO (DEBUG-Meldungen werden gefiltert)
    "Aus": xbmc.LOGINFO,
    # Schwellenwert: INFO (DEBUG-Meldungen werden gefiltert)
    "Basis": xbmc.LOGINFO,
    # Schwellenwert: DEBUG (alle Meldungen werden geloggt)
    "Detailliert": xbmc.LOGDEBUG,
}

# NEU: Wrapper für xbmc.log


def _log(message, level=xbmc.LOGINFO):
    try:
        addon = xbmcaddon.Addon()
        try:
            debug_level = addon.getSetting("debug_logging_level")  # Universal
        except:
            debug_level = "0"  # Default fallback

        threshold = LOG_LEVEL_MAP.get(debug_level, xbmc.LOGINFO)
        if level >= threshold:
            xbmc.log(f"[sKullsRadioSuite] {message}", level)
    except Exception as e:
        xbmc.log(f"[sKullsRadioSuite] Logging Error: {str(e)}", xbmc.LOGERROR)


# --- Hilfsfunktionen für Addon-Einstellungen ---
def get_addon_settings():
    return xbmcaddon.Addon()


def get_params():
    """Sicheres Parsen der URL-Parameter"""
    paramstring = sys.argv[2][1:] if len(sys.argv) > 2 else ""
    params = dict(urllib.parse.parse_qsl(paramstring))
    xbmc.log(f"[{ADDON_NAME}] Parameter: {params}", xbmc.LOGDEBUG)  # Jetzt korrekt
    return params


def is_encryption_supported():
    return all([AES_Cipher, PBKDF2])


def get_cloud_credentials():
    addon = get_addon_settings()
    url_base = addon.getSettingString("cloud_url").rstrip("/")
    user = addon.getSettingString("cloud_user")
    password = addon.getSettingString("cloud_password")
    return url_base, user, password


def get_global_feature_settings():
    addon = xbmcaddon.Addon()
    settings = {}
    try:
        # Hier verwenden wir unsere neue get_setting()-Funktion
        cloud_str = get_setting(
            "enable_cloud_features", "false"
        )  # "false" ist Standardwert
        github_str = get_setting("enable_github_features", "false")

        # Wandelt "true"/"false" Strings in echte True/False Werte um
        settings["enable_cloud_features"] = cloud_str.lower() == "true"
        settings["enable_github_features"] = github_str.lower() == "true"

    except Exception as e:
        # Falls etwas schiefgeht: Standardwerte (False) verwenden
        settings = {"enable_cloud_features": False, "enable_github_features": False}
    return settings


def get_setting(setting_id, default=""):
    addon = xbmcaddon.Addon()
    try:
        # Versuche zuerst String, dann Int, dann Bool
        value = addon.getSettingString(setting_id)
        if not value:
            value = str(addon.getSettingInt(setting_id))
        return value or default
    except:
        try:
            return str(addon.getSettingInt(setting_id))
        except:
            try:
                return "true" if addon.getSettingBool(setting_id) else "false"
            except:
                return default


# Hilfsfunktion zur Normalisierung von Dateinamen
def _normalize_filename(name):
    """Konvertiert einen String in einen dateisystemfreundlichen Dateinamen (Kleinbuchstaben, Unterstriche)."""
    name = name.lower()
    # Entfernt alle Zeichen außer a-z, 0-9, _, -, Leerzeichen
    name = re.sub(r"[^a-z0-9_ -]", "", name)
    # Ersetzt Leerzeichen durch Unterstriche
    name = name.replace(" ", "_")
    # Ersetzt Bindestriche durch Unterstriche
    name = name.replace("-", "_")
    # Ersetzt mehrfache Unterstriche durch einen einzigen
    name = re.sub(r"_+", "_", name)
    # Entfernt führende/nachfolgende Unterstriche
    return name.strip("_")


# --- Multiuser Funktionen ---


# --- Einfache JSON Pfade (ohne Multi-User) ---
def FAVORITES_JSON_PATH():
    return os.path.join(ADDON_DIR, "favorites.json")

def HISTORY_JSON_PATH():
    return os.path.join(ADDON_DIR, "history.json")

def PLAYCOUNT_JSON_PATH():
    return os.path.join(ADDON_DIR, "playcounts.json")

def get_user_config(user=None):
    """Stub - returns default sync hours"""
    return {"sync_hours": 24}

def set_user_config(user, key, val):
    """Stub - does nothing"""
    pass


# --- JSON Robust Loader ---
def load_json(path: str, default: dict) -> dict:
    """
    Safely load JSON file with fallback to default.

    Args:
        path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Loaded data or default value
    """
    _log(f"Lade JSON-Datei: {path}.", xbmc.LOGDEBUG)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    _log(
                        f"Leere JSON-Datei {path}. Es wird Default verwendet.",
                        xbmc.LOGWARNING,
                    )
                    return default
                try:
                    data = json.loads(content)
                    _log(f"JSON-Datei {path} erfolgreich geladen.", xbmc.LOGDEBUG)
                    return data
                except json.JSONDecodeError as err:
                    bad_backup = (
                        path
                        + BROKEN_JSON_PREFIX
                        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    )
                    shutil.copy2(path, bad_backup)
                    xbmcgui.Dialog().notification(
                        "Dateifehler",
                        f"{os.path.basename(path)} ungültig, als .broken gesichert!",
                        xbmcgui.NOTIFICATION_ERROR,
                    )
                    _log(
                        f"JSON-Decode-Fehler {path}: {err}. Datei als .broken gesichert.",
                        xbmc.LOGERROR,
                    )
                    return default
        _log(f"JSON-Datei {path} existiert nicht. Verwende Default.", xbmc.LOGDEBUG)
        return default
    except Exception as e:
        _log(f"JSON-Loader Fehler {path}: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Dateifehler",
            f"{os.path.basename(path)} Fehler beim Laden!",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return default


def save_json(path, d):
    _log(f"Speichere JSON-Datei: {path}.", xbmc.LOGDEBUG)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        _log(f"JSON-Datei {path} erfolgreich gespeichert.", xbmc.LOGDEBUG)
    except Exception as e:
        _log(f"save_json Fehler {path}: {e}", xbmc.LOGERROR)


# --- AES ENCRYPTION/DECRYPTION ---
def _derive_key(password, salt=None, key_bytes=32):
    _log("Schlüsselableitung gestartet.", xbmc.LOGDEBUG)
    if PBKDF2:
        if salt is None:
            salt = get_random_bytes(16)
        key = PBKDF2(password.encode("utf-8"), salt, dkLen=key_bytes, count=100000)
        _log("Schlüssel mit PBKDF2 abgeleitet.", xbmc.LOGDEBUG)
        return key, salt
    else:
        _log(
            "PBKDF2 nicht verfügbar, verwende einfache Schlüsselableitung.",
            xbmc.LOGWARNING,
        )
        key = password.encode("utf-8").ljust(key_bytes, b"\0")[:key_bytes]
        return key, salt  # Salt is not used in this fallback method


def encrypt_file(filepath, password):
    _log(f"Verschlüssle Datei: {filepath}.", xbmc.LOGINFO)
    if AES is None:
        xbmcgui.Dialog().notification(
            "Crypto fehlt",
            "Verschlüsselung nicht verfügbar.",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return None

    BS = 16  # Block size for AES
    key, salt = _derive_key(password, key_bytes=32)
    iv = get_random_bytes(BS)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(filepath, "rb") as f:
        data = f.read()
    ct_bytes = cipher.encrypt(pad(data, BS))

    out_path = filepath + ENCRYPTED_EXTENSION
    with open(out_path, "wb") as f:
        if PBKDF2:
            f.write(salt + iv + ct_bytes)
        else:
            f.write(iv + ct_bytes)

    _log(f"Datei erfolgreich verschlüsselt: {out_path}.", xbmc.LOGINFO)
    return out_path


def decrypt_file(enc_path, password):
    _log(f"Entschlüssle Datei: {enc_path}.", xbmc.LOGINFO)
    if AES is None:
        xbmcgui.Dialog().notification(
            "Crypto fehlt",
            "Entschlüsselung nicht verfügbar.",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return None

    BS = 16
    try:
        with open(enc_path, "rb") as f:
            if PBKDF2:
                salt = f.read(16)
                iv = f.read(16)
            else:
                salt = None  # Not used
                iv = f.read(16)
            ct = f.read()

        key, _ = _derive_key(password, salt=salt, key_bytes=32)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        data = unpad(cipher.decrypt(ct), BS)

        # Assume original was a zip
        dec_path = enc_path.replace(ENCRYPTED_EXTENSION, ".zip")
        with open(dec_path, "wb") as f:
            f.write(data)
        _log(f"Datei erfolgreich entschlüsselt: {dec_path}.", xbmc.LOGINFO)
        return dec_path
    except ValueError as e:  # Catch incorrect padding / wrong key
        _log(f"Entschlüsselungsfehler (Padding/Key) für {enc_path}: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Entschlüsselungsfehler",
            "Falsches Passwort oder beschädigte Datei!",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return None
    except Exception as e:
        _log(f"Allgemeiner Entschlüsselungsfehler für {enc_path}: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Entschlüsselungsfehler",
            f"Allgemeiner Fehler: {e}",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return None


# --- Language Helper ---
def _lang(id):
    return get_addon_settings().getLocalizedString(id)


# --- Badge/Listen-Helpers ---
def apply_color(label, color):
    if color == "badge":
        return f"[B][COLOR orange]{label}[/COLOR][/B]"
    if color == "fav":
        return f"[COLOR gold]{label}[/COLOR]"
    if color == "offline":
        return f"[COLOR red]{label}[/COLOR]"
    if color == "updated":
        return f"[COLOR lime]{label}[/COLOR]"
    return label


def is_recent(entry):
    try:
        if "added" in entry:
            diff_days = (
                datetime.datetime.now()
                - datetime.datetime.fromisoformat(entry["added"])
            ).days
            _log(
                f"Eintrag '{entry.get('name')}' ist {diff_days} Tage alt.",
                xbmc.LOGDEBUG,
            )
            return diff_days < RECENT_DAYS
        return False
    except Exception as e:
        _log(
            f"Fehler bei is_recent für Eintrag '{entry.get('name')}': {e}",
            xbmc.LOGDEBUG,
        )
        return False


def is_updated(entry):
    try:
        if "updated" in entry:
            diff_days = (
                datetime.datetime.now()
                - datetime.datetime.fromisoformat(entry["updated"])
            ).days
            _log(
                f"Eintrag '{entry.get('name')}' wurde vor {diff_days} Tagen aktualisiert.",
                xbmc.LOGDEBUG,
            )
            return diff_days < RECENT_DAYS
        return False
    except Exception as e:
        _log(
            f"Fehler bei is_updated für Eintrag '{entry.get('name')}': {e}",
            xbmc.LOGDEBUG,
        )
        return False


# --- Health Check ---
def check_url_online(url):
    _log(f"Prüfe URL-Online-Status: {url}", xbmc.LOGDEBUG)
    try:
        # HEAD funktioniert oft nicht bei Streaming-URLs - probiere GET mit kleinem timeout
        resp = requests.get(url, timeout=5, stream=True, allow_redirects=True)
        is_online = 200 <= resp.status_code < 400
        resp.close()
        _log(f"URL {url} Status: {resp.status_code}, Online: {is_online}", xbmc.LOGDEBUG)
        return is_online
    except requests.exceptions.RequestException as e:
        _log(f"URL check failed for {url}: {e}", xbmc.LOGDEBUG)
        return False


def health_check():
    _log("Starte Stream-Health-Check.", xbmc.LOGINFO)
    streams = load_json(STREAMS_JSON, {})
    if not streams:
        xbmcgui.Dialog().ok("Stream-Health", "Keine Streams konfiguriert.")
        return

    results = []
    txt_lines = []
    txt_lines.append("=" * 60)
    txt_lines.append("sKulls Radio Suite - Stream Health Check")
    txt_lines.append(f"Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    txt_lines.append("=" * 60)
    txt_lines.append("")

    for k, lst in streams.items():
        for s in lst:
            url = s.get("url", "")
            name = s.get("name", "")
            if not is_valid_url(url):
                label = f"[{k}] {name}: [UNGÜLTIGE URL]"
                txt_line = f"[{k}] {name}: UNGÜLTIGE URL"
                _log(f"Ungültige URL gefunden: {url} in {k} / {name}", xbmc.LOGWARNING)
            else:
                up = check_url_online(url)
                label = f"[{k}] {name}"
                txt_line = f"[{k}] {name}"
                if up:
                    label += " [OK]"
                    txt_line += " [OK]"
                else:
                    label += " [OFFLINE]"
                    txt_line += " [OFFLINE]"
                    _log(f"Stream {name} ({url}) ist OFFLINE.", xbmc.LOGINFO)
            results.append(label)
            txt_lines.append(txt_line)

    # Speichere TXT-Datei in userdata/addon_data
    profile_dir = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
    txt_file = os.path.join(profile_dir, "health_check_report.txt")
    try:
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(txt_lines))
        _log(f"Health-Check Bericht gespeichert: {txt_file}", xbmc.LOGINFO)
    except Exception as e:
        _log(f"Konnte TXT nicht speichern: {e}", xbmc.LOGWARNING)

    xbmcgui.Dialog().textviewer(
        "Stream-Health", "\n".join(results) or "Keine Streams gefunden."
    )
    _log("Stream-Health-Check abgeschlossen.", xbmc.LOGINFO)


# --- Favoriten/History/Playcount ---
def list_streams(domain):
    _log(f"Liste Streams für Domain: {domain}.", xbmc.LOGINFO)
    streams = load_json(STREAMS_JSON, {})

    # Einmaliges Laden der Favoriten für bessere Performance
    favs = load_json(FAVORITES_JSON_PATH(), [])
    fav_urls = {f["url"] for f in favs}  # Set für schnelleren Zugriff

    playcounts = load_json(PLAYCOUNT_JSON_PATH(), {})

    domain_streams = streams.get(domain, [])
    if not domain_streams:
        xbmcgui.Dialog().notification(
            "Info", f"Keine Streams für Domain '{domain}'.", xbmc.NOTIFICATION_INFO
        )
        _log(f"Keine Streams in Domain '{domain}' gefunden.", xbmc.LOGINFO)
        return

    for entry in domain_streams:
        try:
            label_parts = []
            url = entry.get("url", "").strip()
            url = urllib.parse.unquote_plus(url)
            _log(
                f"Verarbeite Stream: {entry.get('name')}", xbmc.LOGDEBUG
            )  # Reduziertes Logging

            # URL Validierung
            if not is_valid_url(url):
                li = xbmcgui.ListItem(label=f"[UNGÜLTIG] {entry.get('name', '')}")
                xbmcplugin.addDirectoryItem(
                    handle=ADDON_HANDLE, url="", listitem=li, isFolder=False
                )
                _log(f"Ungültige URL für '{entry.get('name')}'", xbmc.LOGWARNING)
                continue

            # Badges/Statistik
            if url in fav_urls:
                label_parts.append(apply_color("★", "fav", night))
            pc = playcounts.get(url, 0)
            if pc > 0:
                label_parts.append(apply_color(f"({pc})", "badge", night))
            if not check_url_online(url):
                label_parts.append(apply_color("OFFLINE", "offline", night))
            if is_recent(entry):
                label_parts.append(apply_color("NEU", "updated", night))
            elif is_updated(entry):
                label_parts.append(apply_color("aktualisiert", "updated", night))

            label = " ".join(label_parts) + " " + entry.get("name", "")
            li = xbmcgui.ListItem(label=label.strip())

            # Metadaten setzen
            info = li.getMusicInfoTag()
            info.setTitle(entry.get("name", ""))
            if entry.get("artist"):
                info.setArtist(entry.get("artist"))
            if entry.get("album"):
                info.setAlbum(entry.get("album"))
            if entry.get("genre"):
                info.setGenre(entry.get("genre"))

            # Icon-Logik
            stream_icon_path = None
            if entry.get("icon"):
                full_path = os.path.join(ADDON_DIR, entry["icon"])
                if os.path.exists(full_path):
                    stream_icon_path = full_path

            if not stream_icon_path:
                normalized_name = _normalize_filename(entry.get("name", ""))
                if normalized_name:
                    test_path = os.path.join(
                        IMAGES_STREAMS_DIR, f"{normalized_name}.png"
                    )
                    if os.path.exists(test_path):
                        stream_icon_path = test_path

            if not stream_icon_path:
                normalized_domain = _normalize_filename(domain)
                test_path = os.path.join(
                    IMAGES_CATEGORIES_DIR, f"{normalized_domain}.png"
                )
                if os.path.exists(test_path):
                    stream_icon_path = test_path

            if stream_icon_path:
                li.setArt({"icon": stream_icon_path, "thumb": stream_icon_path})

            # Context-Menü für Favoriten
            context_menu = []
            is_favorite = url in fav_urls

            action_url = (
                f"{BASE_URL}?action=toggle_favorite&"
                f"name={urllib.parse.quote_plus(entry['name'])}&"
                f"url={urllib.parse.quote_plus(url)}&"
                f"domain={urllib.parse.quote_plus(domain)}"
            )

            context_menu.append(
                (
                    (
                        "Aus Favoriten entfernen"
                        if is_favorite
                        else "Zu Favoriten hinzufügen"
                    ),
                    f"RunPlugin({action_url})",
                )
            )

            li.addContextMenuItems(context_menu)
            li.setProperty("IsPlayable", "true")

            xbmcplugin.addDirectoryItem(
                handle=ADDON_HANDLE,
                url=f"{BASE_URL}?action=play_stream&domain={urllib.parse.quote_plus(domain)}"
                f"&name={urllib.parse.quote_plus(entry.get('name',''))}"
                f"&url={urllib.parse.quote_plus(url)}",
                listitem=li,
                isFolder=False,
            )

        except Exception as e:
            _log(f"Fehler bei Stream {entry.get('name')}: {str(e)}", xbmc.LOGERROR)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    _log(f"Streams für '{domain}' erfolgreich geladen", xbmc.LOGINFO)


def is_valid_url(url):
    _log(f"Validiere URL: {url[:50]}...", xbmc.LOGDEBUG)
    if not isinstance(url, str) or not url:
        _log("URL ist leer oder kein String.", xbmc.LOGDEBUG)
        return False
    if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", url):
        _log(f"URL entspricht nicht dem http(s) Muster: {url}", xbmc.LOGDEBUG)
        return False
    # Check for common invalid chars
    if any(x in url for x in [" ", "\n", "\r", "None"]):
        _log(
            f"URL enthält ungültige Zeichen (Leerzeichen, Newline, 'None'): {url}",
            xbmc.LOGDEBUG,
        )
        return False
    _log("URL-Validierung erfolgreich.", xbmc.LOGDEBUG)
    return True


def play_stream(domain, name, url):
    _log(
        f"Spiele Stream ab: '{name}' aus Domain '{domain}' (URL: {url[:50]}...).",
        xbmc.LOGINFO,
    )
    url = urllib.parse.unquote_plus(url)

    if not is_valid_url(url):
        xbmcgui.Dialog().notification(
            "Fehler", "Ungültige URL!", xbmcgui.NOTIFICATION_ERROR
        )
        xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem())
        _log(f"Wiedergabe abgebrochen: Ungültige URL {url}.", xbmc.LOGERROR)
        return

    playcounts = load_json(PLAYCOUNT_JSON_PATH(), {})
    playcounts[url] = playcounts.get(url, 0) + 1
    save_json(PLAYCOUNT_JSON_PATH(), playcounts)

    history = load_json(HISTORY_JSON_PATH(), [])
    history = [h for h in history if h.get("url") != url]

    history_entry = {
        "domain": domain,
        "name": name,
        "url": url,
        "played": datetime.datetime.now().isoformat(),
    }
    history.append(history_entry)
    save_json(HISTORY_JSON_PATH(), history)

    item = xbmcgui.ListItem(path=url)
    item.setProperty("IsPlayable", "true")

    streams = load_json(STREAMS_JSON, {})
    stream_data = {}
    for d, streams_list in streams.items():
        for s in streams_list:
            if s.get("url") == url:
                stream_data = s
                break

    icon_path = None
    custom_icon = stream_data.get("icon")
    if custom_icon:
        icon_path = os.path.join(ADDON_DIR, custom_icon)
        if os.path.exists(icon_path):
            item.setArt({"thumb": icon_path, "icon": icon_path})

    info = {
        "title": name,
        "artist": domain,
        "album": f"sKulls Radio - {domain}",
    }
    item.setInfo("music", info)

    _log(f"DEBUG: Kodi Player startet Stream: {url}", xbmc.LOGINFO)
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, item)


def log_history(action, filepath, details=""):
    """Log backup/restore history"""
    _log(f"Protokolliere Verlauf: {action} | {filepath} | {details}", xbmc.LOGINFO)
    try:
        with open(HISTORY_LOG, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Original format
            f.write(f"{timestamp} | {action} | {filepath} | {details}\n")
    except Exception as e:
        _log(f"History log error: {e}", xbmc.LOGERROR)


def cloud_auto_upload(zipfile_path):
    """Auto-upload backup to cloud if enabled"""
    _log(f"Starte Cloud-Auto-Upload für {zipfile_path}.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        _log(
            "Cloud features disabled by user settings. Auto-upload skipped.",
            xbmc.LOGDEBUG,
        )
        return False  # Indicate not uploaded due to settings

    addon = get_addon_settings()

    if not addon.getSettingBool("cloud_auto_upload"):
        _log("Automatische Cloud-Upload-Einstellung ist deaktiviert.", xbmc.LOGDEBUG)
        return False

    url_base, user, password = get_cloud_credentials()

    if not url_base:
        _log(
            "Cloud URL nicht konfiguriert für Auto-Upload. Upload übersprungen.",
            xbmc.LOGWARNING,
        )
        return False

    try:
        with open(zipfile_path, "rb") as f:
            _log(
                f"Versuche Upload zu: {url_base}/{os.path.basename(zipfile_path)}",
                xbmc.LOGDEBUG,
            )
            resp = requests.put(
                f"{url_base}/{os.path.basename(zipfile_path)}",
                data=f,
                auth=(user, password) if user and password else None,
                timeout=60,
            )
        if 200 <= resp.status_code < 400:
            xbmcgui.Dialog().notification(
                "Cloud Upload",
                "Backup automatisch hochgeladen",
                xbmcgui.NOTIFICATION_INFO,
            )
            log_history("CLOUD_UPLOAD", zipfile_path, f"Status: {resp.status_code}")
            _log(
                f"Cloud-Auto-Upload erfolgreich: {zipfile_path}, Status {resp.status_code}",
                xbmc.LOGINFO,
            )
            return True
        else:
            xbmcgui.Dialog().notification(
                "Cloud Upload Fehler",
                f"Auto-Upload fehlgeschlagen: Status {resp.status_code}",
                xbmcgui.NOTIFICATION_ERROR,
            )
            _log(
                f"Cloud-Auto-Upload fehlgeschlagen für {zipfile_path}: Status {resp.status_code}",
                xbmc.LOGERROR,
            )
            return False
    except requests.exceptions.RequestException as e:
        _log(f"Cloud-Auto-Upload Netzwerkfehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Cloud Upload Fehler", f"Netzwerkfehler: {e}", xbmcgui.NOTIFICATION_ERROR
        )
        return False


def set_sync_interval_menu():
    _log("Starte Menü für Sync-Intervall-Einstellung.", xbmc.LOGINFO)
    user = "default"
    current = get_user_config(user).get("sync_hours", 24)

    options = ["6 Stunden", "12 Stunden", "24 Stunden", "48 Stunden", "1 Woche (168h)"]
    values = [6, 12, 24, 48, 168]

    sel = xbmcgui.Dialog().select(
        f"Sync-Intervall für {user} (aktuell: {current}h)", options
    )
    if sel >= 0:
        set_user_config(user, "sync_hours", values[sel])
        xbmcgui.Dialog().ok(
            "Sync-Intervall", f"Intervall auf {values[sel]} Stunden gesetzt."
        )
        _log(
            f"Sync-Intervall für {user} auf {values[sel]} Stunden gesetzt.",
            xbmc.LOGINFO,
        )
    else:
        _log("Einstellung des Sync-Intervalls abgebrochen.", xbmc.LOGINFO)


# --- Suchvorschläge (Autocomplete, Einfach) ---
def search_menu():
    _log("Starte Suchmenü.", xbmc.LOGINFO)
    options = ["Rock", "Pop", "Deutscher HipHop", "Club", "Chillout"]
    key = xbmcgui.Dialog().select("Suchvorschläge", options + ["Eigene Eingabe..."])
    streams = load_json(STREAMS_JSON, {})

    term = ""
    if 0 <= key < len(options):
        term = options[key]
    elif key == len(options):  # Eigene Eingabe...
        term = xbmcgui.Dialog().input("Suchbegriff")
    else:  # Abgebrochen
        _log("Suchvorgang abgebrochen.", xbmc.LOGINFO)
        return

    if not term or not term.strip():
        xbmcgui.Dialog().ok("Suche", "Kein Suchbegriff eingegeben.")
        _log("Kein Suchbegriff eingegeben.", xbmc.LOGWARNING)
        return

    _log(f"Suche nach Begriff: '{term}'.", xbmc.LOGINFO)
    term_lower = term.lower()
    result = {}
    for domain, lst in streams.items():
        hits = [
            e
            for e in lst
            if term_lower
            in (
                e.get("name", "") + " " + e.get("genre", "") + " " + e.get("artist", "")
            ).lower()
        ]
        if hits:
            result[domain] = hits

    if not result:
        xbmcgui.Dialog().ok("Suchergebnis", f"Nichts gefunden für '{term}'.")
        _log(f"Nichts gefunden für Suchbegriff '{term}'.", xbmc.LOGINFO)
        return

    msg_lines = []
    for domain, found_streams in result.items():
        msg_lines.append(f"Domain: {domain}")
        for s in found_streams:
            msg_lines.append(
                f"  - {s.get('name', 'Unbekannt')} (Genre: {s.get('genre', 'N/A')})"
            )

    xbmcgui.Dialog().textviewer("Suchergebnis", "\n".join(msg_lines))
    _log("Suchergebnis angezeigt.", xbmc.LOGINFO)


# --- Release-Save / VIP-Snapshot (vor Restore/Backup oder manuell) ---
def create_release_save(reason="Manuell"):
    _log(f"Erstelle VIP-Snapshot (Grund: {reason}).", xbmc.LOGINFO)

    backup_folder = ADDON.getSetting("backup_folder")
    if not backup_folder:
        backup_folder = "special://profile/addon_data/plugin.audio.sKullsRadioSuite/Backups"
    backup_dir = xbmcvfs.translatePath(backup_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rel_zip = f"VIP_SNAPSHOT_{now}_default.zip"
    rel_path = os.path.join(backup_dir, rel_zip)
    important_files = [
        FAVORITES_JSON_PATH(),
        HISTORY_JSON_PATH(),
        PLAYCOUNT_JSON_PATH(),
    ]
    _log(f"Wichtige Dateien für Snapshot: {important_files}.", xbmc.LOGDEBUG)
    try:
        with zipfile.ZipFile(rel_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fpath in important_files:
                if os.path.exists(fpath):
                    zf.write(fpath, os.path.basename(fpath))
                    _log(
                        f"'{os.path.basename(fpath)}' zum Snapshot hinzugefügt.",
                        xbmc.LOGDEBUG,
                    )
                else:
                    _log(
                        f"Datei '{os.path.basename(fpath)}' nicht gefunden, überspringe.",
                        xbmc.LOGDEBUG,
                    )
            tagfile = rel_path + ZIP_TAG_EXTENSION
            with open(tagfile, "w", encoding="utf-8") as tf:
                tf.write("VIP-Release")
            log_history("SNAPSHOT", rel_path, reason)
            xbmcgui.Dialog().notification(
                "VIP-Snapshot",
                f"Snapshot '{os.path.basename(rel_zip)}' erstellt.",
                xbmcgui.NOTIFICATION_INFO,
            )
            _log(f"VIP-Snapshot '{rel_zip}' erfolgreich erstellt.", xbmc.LOGINFO)
    except Exception as e:
        _log(f"Release-Save Fehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Release-Save Fehler", str(e), xbmcgui.NOTIFICATION_ERROR
        )


def backup_delete():
    """Delete backup file from context menu"""
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    filepath = urllib.parse.unquote_plus(params.get("file", ""))
    _log(f"Versuche Backup-Datei zu löschen: {filepath}.", xbmc.LOGINFO)

    if not os.path.exists(filepath):
        xbmcgui.Dialog().notification(
            "Fehler", "Datei nicht gefunden.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            f"Löschen fehlgeschlagen: Datei existiert nicht: {filepath}.",
            xbmc.LOGWARNING,
        )
        return

    # Check if VIP-Release
    tagfile = filepath + ZIP_TAG_EXTENSION
    is_vip = False
    if os.path.exists(tagfile):
        with open(tagfile, "r", encoding="utf-8") as f:
            tag = f.read().strip()
        if tag == "VIP-Release":
            is_vip = True
            if not xbmcgui.Dialog().yesno(
                "VIP-Release löschen?",
                "Dies ist ein wichtiges VIP-Release Backup!\nWirklich löschen?",
            ):
                _log(
                    "Löschen eines VIP-Release Backups vom Benutzer abgebrochen.",
                    xbmc.LOGINFO,
                )
                return

    if xbmcgui.Dialog().yesno(
        "Löschen", f"Wirklich löschen?\n{os.path.basename(filepath)}"
    ):
        try:
            os.remove(filepath)
            if os.path.exists(tagfile):
                os.remove(tagfile)
                _log(
                    f"Zugehörige Tag-Datei '{tagfile}' ebenfalls gelöscht.",
                    xbmc.LOGDEBUG,
                )
            xbmcgui.Dialog().notification(
                "Gelöscht", os.path.basename(filepath), xbmcgui.NOTIFICATION_INFO
            )
            log_history("DELETE", filepath, "VIP-Release" if is_vip else "Manuell")
            _log(f"Backup '{filepath}' erfolgreich gelöscht.", xbmc.LOGINFO)
            # Refresh directory listing
            xbmcplugin.endOfDirectory(
                ADDON_HANDLE, updateListing=True, cacheToDisc=True
            )
        except Exception as e:
            _log(f"Backup Löschfehler für {filepath}: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler", f"Löschen fehlgeschlagen: {e}", xbmcgui.NOTIFICATION_ERROR
            )


# --- Backup Galerie, Tagging ---
def backup_gallery():
    _log("Lade Backup-Galerie.", xbmc.LOGINFO)

    backup_folder = ADDON.getSetting("backup_folder")
    if not backup_folder:
        backup_folder = "special://profile/addon_data/plugin.audio.sKullsRadioSuite/Backups"
    backup_dir = xbmcvfs.translatePath(backup_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    files = []
    for fname in sorted(os.listdir(backup_dir)):
        full_path = os.path.join(backup_dir, fname)
        if fname.endswith(".zip"):
            tagfile = full_path + ZIP_TAG_EXTENSION
            tag = ""
            if os.path.exists(tagfile):
                with open(tagfile, "r", encoding="utf-8") as tf:
                    tag = tf.read().strip()
            files.append((fname, tag, "zip"))
            _log(f"ZIP-Datei '{fname}' gefunden (Tag: '{tag}').", xbmc.LOGDEBUG)
        elif BACKUP_SUFFIX in fname and fname.endswith(".json"):
            files.append((fname, "", "json_bak"))
            _log(f"JSON-Backup-Datei '{fname}' gefunden.", xbmc.LOGDEBUG)

    if not files:
        xbmcgui.Dialog().ok(
            "Backup-Galerie", "Keine ZIP- oder Backup-Dateien gefunden."
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Keine Backup-Dateien in der Galerie gefunden.", xbmc.LOGINFO)
        return

    for f_name, tag, f_type in files:
        full_path = os.path.join(backup_dir, f_name)
        display = f_name
        if tag:
            if tag == "VIP-Release":
                display = f"{f_name} [COLOR gold]({tag})[/COLOR]"
            else:
                display = f"{f_name} [COLOR lime]({tag})[/COLOR]"

        li = xbmcgui.ListItem(label=display)

        context = []
        if f_type == "zip":
            li.setArt({"icon": os.path.join(MEDIA_ICON_PATH, "zip.png")})
            context.append(
                (
                    "ZIP wiederherstellen",
                    f"RunPlugin({BASE_URL}?action=zip_restore_file&file={urllib.parse.quote_plus(full_path)})",
                )
            )
            context.append(
                (
                    "Tag/Kategorie ändern",
                    f"RunPlugin({BASE_URL}?action=backup_tag_edit&file={urllib.parse.quote_plus(full_path)})",
                )
            )
            context.append(
                (
                    "Datei löschen",
                    f"RunPlugin({BASE_URL}?action=backup_delete&file={urllib.parse.quote_plus(full_path)})",
                )
            )
            if tag == "VIP-Release":
                context[-1] = (  # Overwrite delete entry
                    "Löschen (nicht empfohlen!)",
                    f"RunPlugin({BASE_URL}?action=backup_delete&file={urllib.parse.quote_plus(full_path)})",
                )
        elif f_type == "json_bak":
            li.setArt({"icon": os.path.join(MEDIA_ICON_PATH, "log.png")})
            context.append(
                (
                    "Backup einspielen",
                    f"RunPlugin({BASE_URL}?action=bak_restore_file&file={urllib.parse.quote_plus(full_path)})",
                )
            )
            context.append(
                (
                    "Datei löschen",
                    f"RunPlugin({BASE_URL}?action=backup_delete&file={urllib.parse.quote_plus(full_path)})",
                )
            )
        li.addContextMenuItems(context)
        item_url = f"{BASE_URL}?action=play_backup&file={urllib.parse.quote_plus(full_path)}"
        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE, url=item_url, listitem=li, isFolder=False
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    _log("Backup-Galerie erfolgreich geladen.", xbmc.LOGINFO)


def backup_tag_edit():
    _log("Starte Backup-Tag-Bearbeitung.", xbmc.LOGINFO)
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    zipfile_path = urllib.parse.unquote_plus(params.get("file", ""))
    if not os.path.exists(zipfile_path):
        xbmcgui.Dialog().notification(
            "Fehler", "Datei nicht gefunden.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            f"Tag-Bearbeitung fehlgeschlagen: Datei existiert nicht: {zipfile_path}.",
            xbmc.LOGWARNING,
        )
        return

    tagfile = zipfile_path + ZIP_TAG_EXTENSION
    old_tag = ""
    if os.path.exists(tagfile):
        with open(tagfile, "r", encoding="utf-8") as f:
            old_tag = f.read().strip()
            _log(
                f"Bestehender Tag für {os.path.basename(zipfile_path)}: '{old_tag}'.",
                xbmc.LOGDEBUG,
            )

    tag = xbmcgui.Dialog().input("Neuer Tag/Kategorie:", defaultt=old_tag or "Manuell")
    if tag:
        with open(tagfile, "w", encoding="utf-8") as f:
            f.write(tag.strip())
        xbmcgui.Dialog().ok(
            "Backup-Tag geändert",
            f"{os.path.basename(zipfile_path)} ist jetzt '{tag}'.",
        )
        _log(
            f"Tag für '{os.path.basename(zipfile_path)}' auf '{tag}' geändert.",
            xbmc.LOGINFO,
        )
    else:
        _log("Tag-Bearbeitung abgebrochen oder leerer Tag eingegeben.", xbmc.LOGINFO)
    # Refresh the gallery
    xbmcplugin.endOfDirectory(ADDON_HANDLE, updateListing=True, cacheToDisc=True)


def backup_tag_filter():
    _log("Starte Backup-Tag-Filter.", xbmc.LOGINFO)
    tags = set()
    for fname in os.listdir(ADDON_DIR):
        if fname.endswith(".zip"):
            tagfile_path = os.path.join(ADDON_DIR, f"{fname}{ZIP_TAG_EXTENSION}")
            if os.path.exists(tagfile_path):
                with open(tagfile_path, "r", encoding="utf-8") as tf:
                    t = tf.read().strip()
                    if t:
                        tags.add(t)
    tags = sorted(list(tags))
    _log(f"Gefundene Tags für Filter: {', '.join(tags)}.", xbmc.LOGDEBUG)

    if not tags:
        xbmcgui.Dialog().ok("Tag-Filter", "Noch keine Tags vorhanden!")
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Keine Tags zum Filtern gefunden.", xbmc.LOGINFO)
        return

    key = xbmcgui.Dialog().select("Backups filtern nach Tag", tags)
    if key == -1:  # Abgebrochen
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Tag-Filter abgebrochen.", xbmc.LOGINFO)
        return

    selected_tag = tags[key]
    _log(f"Filtere Backups nach Tag: '{selected_tag}'.", xbmc.LOGINFO)
    files_to_display = []
    for fname in sorted(os.listdir(ADDON_DIR)):
        if fname.endswith(".zip"):
            tagfile_path = os.path.join(ADDON_DIR, f"{fname}{ZIP_TAG_EXTENSION}")
            tag = ""
            if os.path.exists(tagfile_path):
                with open(tagfile_path, "r", encoding="utf-8") as tf:
                    tag = tf.read().strip()
            if tag == selected_tag:
                files_to_display.append((fname, tag))
                _log(f"Datei '{fname}' entspricht Filter-Tag.", xbmc.LOGDEBUG)

    if not files_to_display:
        xbmcgui.Dialog().ok(
            "Gefilterte Backups", f"Keine Backups mit Tag '{selected_tag}' gefunden."
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log(f"Keine Backups mit Tag '{selected_tag}' gefunden.", xbmc.LOGINFO)
        return

    for f, tag in files_to_display:
        full_path = os.path.join(ADDON_DIR, f)
        display = f"{f} [COLOR lime]({tag})[/COLOR]"
        li = xbmcgui.ListItem(label=display)
        li.setArt({"icon": os.path.join(MEDIA_ICON_PATH, "zip.png")})
        context = [
            (
                "ZIP wiederherstellen",
                f"RunPlugin({BASE_URL}?action=zip_restore_file&file={urllib.parse.quote_plus(full_path)})",
            ),
            (
                "Tag/Kategorie ändern",
                f"RunPlugin({BASE_URL}?action=backup_tag_edit&file={urllib.parse.quote_plus(full_path)})",
            ),
            (
                "Datei löschen",
                f"RunPlugin({BASE_URL}?action=backup_delete&file={urllib.parse.quote_plus(full_path)})",
            ),
        ]
        li.addContextMenuItems(context)
        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE, url=full_path, listitem=li, isFolder=False
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    _log("Gefilterte Backups erfolgreich angezeigt.", xbmc.LOGINFO)


# --- Undo/Restore kaputter JSONs ---
def gui_undo_restore():
    _log("Starte GUI für Undo-Restore.", xbmc.LOGINFO)

    backup_folder = ADDON.getSetting("backup_folder")
    if not backup_folder:
        backup_folder = "special://profile/addon_data/plugin.audio.sKullsRadioSuite/Backups"
    backup_dir = xbmcvfs.translatePath(backup_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    baks = []
    for fname in sorted(
        os.listdir(backup_dir),
        key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)),
        reverse=True,
    ):
        if BACKUP_SUFFIX in fname and fname.endswith(".json"):
            parts = fname.split(BACKUP_SUFFIX)
            if len(parts) > 1:
                orig = parts[0]
                baks.append((fname, orig))
                _log(f"Gefundenes .bak_ File: {fname} -> {orig}", xbmc.LOGDEBUG)

    if not baks:
        xbmcgui.Dialog().ok(
            "Restore Undo", "Keine Backup-Dateien (.bak_*) im Backup-Ordner gefunden!"
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Keine .bak_ Dateien für Undo-Restore gefunden.", xbmc.LOGINFO)
        return

    disp = [f"{f} → {o}" for f, o in baks]
    idx = xbmcgui.Dialog().select(
        "Zuletzt gesicherte Original-Datei zurückspielen", disp
    )
    if idx == -1:  # Abgebrochen
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Undo-Restore abgebrochen.", xbmc.LOGINFO)
        return

    bak, orig = baks[idx]
    f_bak = os.path.join(backup_dir, bak)
    f_orig = os.path.join(backup_dir, orig)

    ok = xbmcgui.Dialog().yesno(
        "Wiederherstellen",
        f"Backup: {bak}\nWirklich zurück auf → {os.path.basename(orig)}?",
    )
    if ok and os.path.exists(f_bak):
        try:
            shutil.copy2(f_bak, f_orig)
            log_history("UNDO", f_bak, f"restored to {f_orig}")
            xbmcgui.Dialog().ok(
                "Undo abgeschlossen",
                f"{os.path.basename(orig)} wiederhergestellt.\nDas Backup bleibt erhalten.",
            )
            _log(f"Undo-Restore erfolgreich: {f_bak} auf {f_orig}.", xbmc.LOGINFO)
        except Exception as e:
            _log(f"Fehler beim Undo-Restore: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler",
                f"Wiederherstellung fehlgeschlagen: {e}",
                xbmcgui.NOTIFICATION_ERROR,
            )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# --- Diagnose/Restore kaputter JSONs ---
def broken_json_diagnose():
    _log("Starte Diagnose für kaputte JSON-Dateien.", xbmc.LOGINFO)
    broken_files = []
    for fname in sorted(os.listdir(ADDON_DIR)):
        if BROKEN_JSON_PREFIX in fname and fname.endswith(".json"):
            parts = fname.split(BROKEN_JSON_PREFIX)
            if len(parts) > 1:
                orig = parts[0] + ".json"
                broken_files.append((fname, orig))
                _log(
                    f"Gefundene kaputte JSON: {fname} (Original: {orig}).",
                    xbmc.LOGDEBUG,
                )

    if not broken_files:
        xbmcgui.Dialog().ok(
            "Diagnose JSON", "Keine kaputten JSON-Backup-Dateien gefunden!"
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Keine kaputten JSON-Dateien gefunden.", xbmc.LOGINFO)
        return

    disp = [f"{f} (Original: {o})" for f, o in broken_files]
    idx = xbmcgui.Dialog().select(
        "Kaputtes JSON inspizieren und wiederherstellen", disp
    )
    if idx == -1:  # Abgebrochen
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Diagnose für kaputte JSON-Dateien abgebrochen.", xbmc.LOGINFO)
        return

    fname, orig = broken_files[idx]
    f_broken = os.path.join(ADDON_DIR, fname)
    f_orig = os.path.join(ADDON_DIR, orig)

    actions = ["Inhalt ansehen", "Als aktuelle JSON wiederherstellen", "Abbrechen"]
    choice = xbmcgui.Dialog().select("Aktion", actions)

    if choice == 0:  # Inhalt ansehen
        _log(f"Zeige Inhalt von kaputter JSON: {f_broken}.", xbmc.LOGINFO)
        try:
            with open(f_broken, "r", encoding="utf-8") as f:
                content = f.read() or "(leer)"
            xbmcgui.Dialog().textviewer(f_broken, content)
        except Exception as e:
            _log(f"Fehler beim Lesen der kaputten JSON: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler", f"Kann Datei nicht lesen: {e}", xbmcgui.NOTIFICATION_ERROR
            )
    elif choice == 1:  # Als aktuelle JSON wiederherstellen
        _log(f"Wiederherstellung von {f_broken} auf {f_orig}.", xbmc.LOGINFO)
        try:
            shutil.copy2(f_broken, f_orig)
            xbmcgui.Dialog().ok(
                "JSON wiederhergestellt",
                f"{os.path.basename(orig)} wurde aus {os.path.basename(fname)} zurückkopiert!\nAdd-on-Neustart empfohlen.",
            )
            log_history("RESTORE_BROKEN_JSON", f_broken, f"restored to {f_orig}")
            _log(f"Kaputte JSON erfolgreich wiederhergestellt: {f_orig}.", xbmc.LOGINFO)
        except Exception as e:
            _log(f"Fehler beim Wiederherstellen der kaputten JSON: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler",
                f"Wiederherstellung fehlgeschlagen: {e}",
                xbmcgui.NOTIFICATION_ERROR,
            )

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# --- ZIP Backup ---
def zip_backup():
    _log("Starte ZIP-Backup.", xbmc.LOGINFO)

    backup_folder = ADDON.getSetting("backup_folder")
    if not backup_folder:
        backup_folder = "special://profile/addon_data/plugin.audio.sKullsRadioSuite/Backups"
    backup_dir = xbmcvfs.translatePath(backup_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    _log(f"Backup-Ordner: {backup_dir}", xbmc.LOGDEBUG)

    addon_files = []
    for f in os.listdir(ADDON_DIR):
        if (
            f.endswith(".json")
            or f.endswith(".log")
        ):
            addon_files.append(os.path.join(ADDON_DIR, f))
            _log(f"Backup-fähige Datei gefunden: {f}", xbmc.LOGDEBUG)

    if not addon_files:
        xbmcgui.Dialog().ok("ZIP Backup", "Keine Addon-Daten für Backup gefunden.")
        _log("Keine Addon-Daten für ZIP-Backup gefunden.", xbmc.LOGINFO)
        return

    selected_indices = xbmcgui.Dialog().multiselect(
        "Dateien für Backup wählen", [os.path.basename(f) for f in addon_files]
    )
    if selected_indices is None or not selected_indices:
        xbmcgui.Dialog().ok("ZIP Backup", "Keine Datei gewählt oder abgebrochen.")
        _log("ZIP-Backup abgebrochen oder keine Dateien ausgewählt.", xbmc.LOGINFO)
        return

    selected_paths = [addon_files[i] for i in selected_indices]
    _log(f"Ausgewählte Dateien für Backup: {selected_paths}.", xbmc.LOGDEBUG)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_zip_name = f"backup_{now}_default.zip"

    zipname = xbmcgui.Dialog().input(
        "Name fürs ZIP (mit .zip)", defaultt=default_zip_name
    )

    if not zipname or not zipname.strip() or not zipname.lower().endswith(".zip"):
        xbmcgui.Dialog().ok(
            "ZIP Backup", "Abgebrochen oder kein gültiger .zip-Name angegeben."
        )
        _log("Ungültiger ZIP-Dateiname oder Backup abgebrochen.", xbmc.LOGWARNING)
        return

    if not os.path.isabs(zipname):
        zipname = os.path.join(backup_dir, zipname)
    _log(f"ZIP-Zielpfad: {zipname}.", xbmc.LOGDEBUG)

    tag = xbmcgui.Dialog().input(
        "Tag/Kategorie dieses Backups (z.B. Automatik, Manuell, Wichtig):",
        defaultt="Manuell",
    )
    _log(f"Backup-Tag: '{tag}'.", xbmc.LOGDEBUG)

    meta_path = zipname + ZIP_TAG_EXTENSION

    try:
        with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in selected_paths:
                if os.path.exists(f):
                    zf.write(f, os.path.basename(f))
                    _log(
                        f"Datei '{os.path.basename(f)}' zum ZIP hinzugefügt.",
                        xbmc.LOGDEBUG,
                    )
                else:
                    _log(
                        f"Datei '{os.path.basename(f)}' existiert nicht, kann nicht zum ZIP hinzugefügt werden.",
                        xbmc.LOGWARNING,
                    )
            with open(meta_path, "w", encoding="utf-8") as tf:
                tf.write(tag.strip() or "Manuell")
                _log(f"Tag-Datei für ZIP erstellt: {meta_path}.", xbmc.LOGDEBUG)

            xbmcgui.Dialog().ok(
                "ZIP Backup",
                f"Backup '{os.path.basename(zipname)}' mit Tag '{tag}' gespeichert.",
            )
            log_history("BACKUP_ZIP", zipname, tag)
            _log(f"ZIP-Backup '{zipname}' erfolgreich erstellt.", xbmc.LOGINFO)
            # cloud_auto_upload returns boolean, not used here for direct check
            cloud_auto_upload(zipname)
    except Exception as e:
        _log(f"ZIP Backup Fehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification("ZIP Fehler", str(e), xbmcgui.NOTIFICATION_ERROR)


def zip_restore_file():
    _log("Starte ZIP-Wiederherstellung.", xbmc.LOGINFO)
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    zip_path = urllib.parse.unquote_plus(params.get("file", ""))
    _log(f"ZIP-Datei für Wiederherstellung: {zip_path}.", xbmc.LOGDEBUG)

    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        xbmcgui.Dialog().ok("ZIP Restore", "Datei nicht gefunden oder keine ZIP-Datei.")
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log(
            f"Wiederherstellung abgebrochen: {zip_path} ist keine gültige ZIP-Datei.",
            xbmc.LOGWARNING,
        )
        return

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            namelist = [name for name in zf.namelist() if not name.endswith("/")]
            _log(f"Inhalt des ZIP-Archivs: {namelist}.", xbmc.LOGDEBUG)

            if not namelist:
                xbmcgui.Dialog().ok("ZIP Restore", "ZIP-Archiv ist leer.")
                xbmcplugin.endOfDirectory(ADDON_HANDLE)
                _log("ZIP-Archiv ist leer.", xbmc.LOGINFO)
                return

            sel_indices = xbmcgui.Dialog().multiselect(
                "Wiederherstellen: Dateien wählen", namelist
            )
            if (
                sel_indices is None or not sel_indices
            ):  # None if cancelled, empty list if nothing selected
                xbmcgui.Dialog().ok(
                    "ZIP Restore",
                    "Keine Datei zur Wiederherstellung ausgewählt oder abgebrochen.",
                )
                xbmcplugin.endOfDirectory(ADDON_HANDLE)
                _log(
                    "Keine Dateien zur Wiederherstellung ausgewählt oder abgebrochen.",
                    xbmc.LOGINFO,
                )
                return

            for i in sel_indices:
                fname = namelist[i]
                target_path = os.path.join(ADDON_DIR, fname)
                _log(f"Wiederherstelle '{fname}' nach '{target_path}'.", xbmc.LOGDEBUG)

                backup_folder = ADDON.getSetting("backup_folder")
                if not backup_folder:
                    backup_folder = "special://profile/addon_data/plugin.audio.sKullsRadioSuite/Backups"
                backup_dir = xbmcvfs.translatePath(backup_folder)
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)

                if os.path.exists(target_path):
                    timestr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = os.path.join(backup_dir, f"{fname}{BACKUP_SUFFIX}{timestr}")
                    shutil.copy2(target_path, backup_path)
                    _log(
                        f"Bestehende Datei gesichert: {os.path.basename(target_path)} nach {os.path.basename(backup_path)}",
                        xbmc.LOGINFO,
                    )

                with open(target_path, "wb") as f:
                    f.write(zf.read(fname))
                log_history("RESTORE", fname, f"from {os.path.basename(zip_path)}")

        xbmcgui.Dialog().ok(
            "ZIP Restore",
            "Wiederherstellung abgeschlossen!\nVorige Versionen als .bak_<datum> gesichert.",
        )
        _log(
            f"ZIP-Wiederherstellung von '{zip_path}' erfolgreich abgeschlossen.",
            xbmc.LOGINFO,
        )
    except Exception as e:
        _log(f"ZIP Restore Fehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Fehler",
            f"Wiederherstellung fehlgeschlagen: {e}",
            xbmcgui.NOTIFICATION_ERROR,
        )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)  # Ensure directory ends


def bak_restore_file():
    _log("Starte .bak_ Datei-Wiederherstellung.", xbmc.LOGINFO)
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    bak_path = urllib.parse.unquote_plus(params.get("file", ""))
    _log(f".bak_ Pfad: {bak_path}.", xbmc.LOGDEBUG)

    if not os.path.exists(bak_path) or not (
        BACKUP_SUFFIX in os.path.basename(bak_path) and bak_path.endswith(".json")
    ):
        xbmcgui.Dialog().ok(
            "Backup Restore", "Datei nicht gefunden oder keine .bak_ Datei."
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log(
            f"Wiederherstellung abgebrochen: {bak_path} ist keine gültige .bak_ Datei.",
            xbmc.LOGWARNING,
        )
        return

    original_file_name = os.path.basename(bak_path).split(BACKUP_SUFFIX)[0]
    original_path = os.path.join(ADDON_DIR, original_file_name)
    _log(f"Originalpfad für Wiederherstellung: {original_path}.", xbmc.LOGDEBUG)

    if xbmcgui.Dialog().yesno(
        "Wiederherstellen?",
        f"'{os.path.basename(bak_path)}'\nWirklich wiederherstellen auf '{original_file_name}'?",
    ):
        try:
            shutil.copy2(bak_path, original_path)
            log_history("RESTORE_BAK", bak_path, f"restored to {original_path}")
            xbmcgui.Dialog().ok(
                "Backup wiederhergestellt",
                f"'{os.path.basename(original_path)}' wurde aus '{os.path.basename(bak_path)}' wiederhergestellt.\nAdd-on-Neustart empfohlen.",
            )
            _log(
                f".bak_ Wiederherstellung erfolgreich: {bak_path} auf {original_path}.",
                xbmc.LOGINFO,
            )
        except Exception as e:
            _log(f"BAK restore Fehler: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler",
                f"Wiederherstellung fehlgeschlagen: {e}",
                xbmcgui.NOTIFICATION_ERROR,
            )
    else:
        _log(".bak_ Wiederherstellung vom Benutzer abgebrochen.", xbmc.LOGINFO)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# --- Diagnose/Restore kaputter ZIPs ---
def broken_zip_diagnose():
    _log("Starte Diagnose für kaputte ZIPs.", xbmc.LOGINFO)
    broken_zips = []
    for fname in sorted(os.listdir(ADDON_DIR)):
        if fname.endswith(".zip"):
            zip_path = os.path.join(ADDON_DIR, fname)
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    test_result = zf.testzip()
                    if test_result:  # None = OK, sonst defekte Datei im Archiv
                        broken_zips.append((fname, test_result))
                        _log(
                            f"Defekte ZIP gefunden: {fname} (Fehler: {test_result}).",
                            xbmc.LOGWARNING,
                        )
            except Exception as e:
                broken_zips.append((fname, str(e)))
                _log(f"Fehler beim Öffnen/Testen von ZIP {fname}: {e}", xbmc.LOGERROR)

    if not broken_zips:
        xbmcgui.Dialog().ok("ZIP-Diagnose", "Keine kaputten ZIP-Backups gefunden!")
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Keine kaputten ZIP-Dateien gefunden.", xbmc.LOGINFO)
        return

    disp = [f"{f} [Defekt: {err}]" for f, err in broken_zips]
    idx = xbmcgui.Dialog().select(
        "Kaputtes Backup inspizieren, löschen, neu laden", disp
    )
    if idx == -1:  # Abgebrochen
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("ZIP-Diagnose abgebrochen.", xbmc.LOGINFO)
        return

    fname, errinfo = broken_zips[idx]
    file_path = os.path.join(ADDON_DIR, fname)
    _log(f"Ausgewählte defekte ZIP: {fname}.", xbmc.LOGDEBUG)

    actions = ["ZIP löschen", "ZIP ins Cloud-Verzeichnis erneut laden", "Abbrechen"]
    choice = xbmcgui.Dialog().select("Aktion", actions)

    if choice == 0:  # Löschen
        _log(f"Lösche defekte ZIP: {file_path}.", xbmc.LOGINFO)
        try:
            os.remove(file_path)
            # Also remove the tag file if it exists
            tagfile_path = file_path + ZIP_TAG_EXTENSION
            if os.path.exists(tagfile_path):
                os.remove(tagfile_path)
                _log(
                    f"Zugehörige Tag-Datei '{tagfile_path}' ebenfalls gelöscht.",
                    xbmc.LOGDEBUG,
                )
            xbmcgui.Dialog().ok("ZIP gelöscht", f"{fname} wurde entfernt.")
            log_history("DELETE_BROKEN_ZIP", file_path)
            _log(f"Defekte ZIP '{fname}' erfolgreich gelöscht.", xbmc.LOGINFO)
        except Exception as e:
            _log(f"Fehler beim Löschen defekter ZIP {file_path}: {e}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                "Fehler", f"Löschen fehlgeschlagen: {e}", xbmcgui.NOTIFICATION_ERROR
            )
    elif choice == 1:  # Neu laden
        _log(f"Versuche defekte ZIP aus Cloud neu zu laden: {fname}.", xbmc.LOGINFO)
        cloud_reload_zip(fname)
    else:
        _log("Aktion für defekte ZIP abgebrochen.", xbmc.LOGINFO)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def cloud_reload_zip(zip_name):
    _log(f"Starte Cloud-Reload für ZIP: {zip_name}.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log("Cloud-Reload übersprungen: Cloud-Funktionen deaktiviert.", xbmc.LOGINFO)
        return

    url_base, user, password = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "Cloud-Reload übersprungen: Cloud URL nicht konfiguriert.", xbmc.LOGWARNING
        )
        return

    remote_url = f"{url_base}/{zip_name}"
    target = os.path.join(ADDON_DIR, zip_name)
    _log(f"Downloade von: {remote_url} nach {target}.", xbmc.LOGDEBUG)
    try:
        resp = requests.get(
            remote_url, auth=(user, password) if user and password else None, timeout=60
        )
        if resp.status_code == 200:
            with open(target, "wb") as f:
                f.write(resp.content)
            xbmcgui.Dialog().ok(
                "Neu geladen", f"ZIP {zip_name} aus der Cloud neu geladen."
            )
            log_history("CLOUD_RELOAD_ZIP", target, f"from {remote_url}")
            _log(f"Cloud-Reload erfolgreich für {zip_name}.", xbmc.LOGINFO)
        else:
            _log(
                f"Cloud-Reload fehlgeschlagen: Status {resp.status_code} für {remote_url}",
                xbmc.LOGERROR,
            )
            xbmcgui.Dialog().notification(
                "Cloud-Reload Fehler",
                f"Status {resp.status_code} - Datei nicht gefunden oder Zugriff verweigert.",
                xbmcgui.NOTIFICATION_ERROR,
            )
    except requests.exceptions.RequestException as e:
        _log(f"Cloud-Reload Netzwerkfehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Cloud-Reload Fehler", f"Netzwerkfehler: {e}", xbmcgui.NOTIFICATION_ERROR
        )


# --- Hash/Integrity-Check ---
def file_hash(path, algo="sha256", chunk_size=8192):
    _log(f"Berechne Hash für: {path} (Algorithmus: {algo}).", xbmc.LOGDEBUG)
    h = hashlib.new(algo)
    try:
        # If path is a file object (from zipfile.open), read directly
        if hasattr(path, "read") and hasattr(path, "seek"):
            original_pos = path.tell()
            path.seek(0)
            while True:
                data = path.read(chunk_size)
                if not data:
                    break
                h.update(data)
            path.seek(original_pos)  # Restore original position
            _log(
                f"Hash für Dateiobjekt berechnet: {h.hexdigest()[:10]}...",
                xbmc.LOGDEBUG,
            )
        else:  # Assume it's a file path
            with open(path, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    h.update(data)
            _log(
                f"Hash für Datei {path} berechnet: {h.hexdigest()[:10]}...",
                xbmc.LOGDEBUG,
            )
        return h.hexdigest()
    except Exception as e:
        _log(f"Fehler beim Berechnen des Hashes für {path}: {e}", xbmc.LOGERROR)
        return None


def zip_hash_overview():
    _log("Starte Übersicht über lokale ZIP-Hashes.", xbmc.LOGINFO)
    zip_files = sorted([f for f in os.listdir(ADDON_DIR) if f.endswith(".zip")])

    if not zip_files:
        xbmcgui.Dialog().ok("ZIP HASH Übersicht", "Keine ZIP-Backups gefunden.")
        _log("Keine lokalen ZIP-Backups für Übersicht gefunden.", xbmc.LOGINFO)
        return

    report = []
    for fname in zip_files:
        full_path = os.path.join(ADDON_DIR, fname)
        h = file_hash(full_path)
        if h:
            report.append(f"{fname}\n  Hash: {h}")
            _log(f"Hash für {fname} gefunden.", xbmc.LOGDEBUG)
        else:
            report.append(f"{fname}\n  [COLOR red]Hash Fehler[/COLOR]")
            _log(f"Fehler beim Berechnen des Hashes für {fname}.", xbmc.LOGERROR)

    xbmcgui.Dialog().textviewer("ZIP HASH Übersicht", "\n\n".join(report))
    _log("Übersicht über lokale ZIP-Hashes angezeigt.", xbmc.LOGINFO)


# --- Encrypted Cloud Upload/Download ---
def backup_cloud_upload_enc():
    _log("Starte verschlüsselten Cloud-Upload.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Verschlüsselter Cloud-Upload übersprungen: Cloud-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        return

    zip_path = xbmcgui.Dialog().browse(
        1, "Backup-ZIP auswählen", "files", ".zip", False, False, ADDON_DIR
    )
    if not zip_path or not os.path.exists(zip_path):
        xbmcgui.Dialog().notification(
            "Cloud Upload", "Kein ZIP ausgewählt oder abgebrochen."
        )
        _log(
            "Verschlüsselter Cloud-Upload abgebrochen oder keine ZIP-Datei ausgewählt.",
            xbmc.LOGINFO,
        )
        return

    password = xbmcgui.Dialog().input(
        "Passwort für Verschlüsselung", type=xbmcgui.INPUT_ALPHANUM
    )
    if not password or not password.strip():
        xbmcgui.Dialog().notification(
            "Abbruch", "Kein Passwort eingegeben.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Verschlüsselter Cloud-Upload abgebrochen: Kein Passwort eingegeben.",
            xbmc.LOGINFO,
        )
        return

    enc_path = encrypt_file(zip_path, password)
    if not enc_path:
        _log("Verschlüsselung der Datei vor dem Upload fehlgeschlagen.", xbmc.LOGERROR)
        return  # Error already handled in encrypt_file

    url_base, user, pw = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "Verschlüsselter Cloud-Upload übersprungen: Cloud URL nicht konfiguriert.",
            xbmc.LOGWARNING,
        )
        if os.path.exists(enc_path):
            os.remove(enc_path)  # Clean up encrypted temp file
        return

    dest_url = f"{url_base}/{os.path.basename(enc_path)}"
    _log(f"Versuche verschlüsselte Datei hochzuladen zu: {dest_url}", xbmc.LOGDEBUG)

    try:
        with open(enc_path, "rb") as f:
            resp = requests.put(
                # Longer timeout for upload
                dest_url,
                data=f,
                auth=(user, pw) if user and pw else None,
                timeout=120,
            )
        if 200 <= resp.status_code < 400:
            xbmcgui.Dialog().notification(
                "Cloud-Upload",
                f"Backup verschlüsselt hochgeladen:\n{os.path.basename(dest_url)}",
            )
            log_history("CLOUD_UPLOAD_ENC", zip_path, f"to {dest_url}")
            _log(f"Verschlüsselter Cloud-Upload erfolgreich: {dest_url}.", xbmc.LOGINFO)
        else:
            _log(
                f"Verschlüsselter Cloud-Upload fehlgeschlagen: Status {resp.status_code} für {dest_url}",
                xbmc.LOGERROR,
            )
            xbmcgui.Dialog().notification(
                "Cloud-Upload Fehler",
                f"Status {resp.status_code} - Upload fehlgeschlagen.",
                xbmcgui.NOTIFICATION_ERROR,
            )
    except requests.exceptions.RequestException as e:
        _log(f"Verschlüsselter Cloud-Upload Netzwerkfehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Cloud-Upload Fehler", f"Netzwerkfehler: {e}", xbmcgui.NOTIFICATION_ERROR
        )
    finally:
        if os.path.exists(enc_path):
            os.remove(enc_path)
            _log(
                f"Temporäre verschlüsselte Datei '{enc_path}' gelöscht.", xbmc.LOGDEBUG
            )


def backup_cloud_download_enc():
    _log("Starte verschlüsselten Cloud-Download.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Verschlüsselter Cloud-Download übersprungen: Cloud-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        return

    # Provide suggestions for typical filenames
    current_user = "default"
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    suggestions = [
        f"backup_{now_str}_{current_user}.zip{ENCRYPTED_EXTENSION}",
        f"VIP_SNAPSHOT_{now_str}_{current_user}.zip{ENCRYPTED_EXTENSION}",
    ]

    # Let user input, possibly prefilled
    zip_name = xbmcgui.Dialog().input(
        "Name der .enc-Datei (z.B. backup_YYYMMDD_HHMMSS.zip.enc)",
        defaultt=suggestions[0],  # Default to a common format
    )

    if not zip_name or not zip_name.strip():
        xbmcgui.Dialog().ok(
            "Cloud Download", "Kein Dateiname eingegeben oder abgebrochen."
        )
        _log(
            "Verschlüsselter Cloud-Download abgebrochen: Kein Dateiname eingegeben.",
            xbmc.LOGINFO,
        )
        return

    if not zip_name.endswith(ENCRYPTED_EXTENSION):
        zip_name += ENCRYPTED_EXTENSION
        _log(f"Dateiname um .enc erweitert: {zip_name}", xbmc.LOGDEBUG)

    password = xbmcgui.Dialog().input(
        "Passwort zum Entschlüsseln", type=xbmcgui.INPUT_ALPHANUM
    )
    if not password or not password.strip():
        xbmcgui.Dialog().notification(
            "Abbruch", "Kein Passwort eingegeben.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Verschlüsselter Cloud-Download abgebrochen: Kein Passwort eingegeben.",
            xbmc.LOGINFO,
        )
        return

    url_base, user, pw = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "Verschlüsselter Cloud-Download übersprungen: Cloud URL nicht konfiguriert.",
            xbmc.LOGWARNING,
        )
        return

    remote_url = f"{url_base}/{zip_name}"
    # Temp path to save encrypted file
    target = os.path.join(ADDON_DIR, zip_name)
    _log(f"Downloade von: {remote_url} nach {target}", xbmc.LOGDEBUG)

    try:
        resp = requests.get(
            remote_url, auth=(user, pw) if user and pw else None, timeout=60
        )
        if resp.status_code == 200:
            with open(target, "wb") as f:
                f.write(resp.content)
            _log(f"Verschlüsselte Datei heruntergeladen: {target}", xbmc.LOGDEBUG)

            dec_path = decrypt_file(target, password)
            if dec_path:
                xbmcgui.Dialog().ok(
                    "Download & Entschlüsselung",
                    f"Entschlüsselt gespeichert als:\n{os.path.basename(dec_path)}",
                )
                log_history("CLOUD_DOWNLOAD_ENC", dec_path, f"from {remote_url}")
                _log(
                    f"Verschlüsselter Cloud-Download und Entschlüsselung erfolgreich: {dec_path}.",
                    xbmc.LOGINFO,
                )
            else:
                xbmcgui.Dialog().notification(
                    "Fehler",
                    "Entschlüsselung fehlgeschlagen.",
                    xbmcgui.NOTIFICATION_ERROR,
                )
                _log("Entschlüsselung nach Download fehlgeschlagen.", xbmc.LOGERROR)
        else:
            _log(
                f"Cloud-Download fehlgeschlagen: Status {resp.status_code} für {remote_url}",
                xbmc.LOGERROR,
            )
            xbmcgui.Dialog().notification(
                "Cloud-Download Fehler",
                f"Status {resp.status_code} - Datei nicht gefunden oder Zugriff verweigert.",
                xbmcgui.NOTIFICATION_ERROR,
            )
    except requests.exceptions.RequestException as e:
        _log(f"Cloud-Download Netzwerkfehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Cloud-Download Fehler", f"Netzwerkfehler: {e}", xbmcgui.NOTIFICATION_ERROR
        )
    finally:
        if os.path.exists(target):
            os.remove(target)
            _log(f"Temporäre verschlüsselte Datei '{target}' gelöscht.", xbmc.LOGDEBUG)


# --- Cloud-ZIP-Hash-Report für alle Backups ---
def cloud_zip_hash_report():
    _log("Starte Cloud-ZIP-Hash-Report.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Cloud-ZIP-Hash-Report übersprungen: Cloud-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        return

    url_base, user, password = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "Cloud-ZIP-Hash-Report übersprungen: Cloud URL nicht konfiguriert.",
            xbmc.LOGWARNING,
        )
        return

    zips = [f for f in sorted(os.listdir(ADDON_DIR)) if f.endswith(".zip")]
    if not zips:
        xbmcgui.Dialog().ok("Cloud-Hash", "Keine lokalen ZIP-Backups gefunden.")
        _log("Keine lokalen ZIP-Backups für Cloud-Hash-Report gefunden.", xbmc.LOGINFO)
        return

    report_lines = []
    for fname in zips:
        _log(f"Verarbeite lokale ZIP-Datei: {fname}.", xbmc.LOGDEBUG)
        local_path = os.path.join(ADDON_DIR, fname)
        local_hash = file_hash(local_path)

        if local_hash is None:
            report_lines.append(
                f"{fname}: [COLOR red]Lokal defekt oder Hash Fehler[/COLOR]"
            )
            _log(
                f"Lokaler Hash für {fname} konnte nicht berechnet werden (defekt).",
                xbmc.LOGERROR,
            )
            continue

        remote_url = f"{url_base}/{fname}"
        try:
            _log(
                f"Versuche Cloud-Version von {fname} abzurufen: {remote_url}",
                xbmc.LOGDEBUG,
            )
            resp = requests.get(
                remote_url,
                auth=(user, password) if user and password else None,
                timeout=60,
            )
            if resp.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(resp.content)
                    tmp_path = tmp.name  # Korrektur: tmp.name statt tmp.File
                remote_hash = file_hash(tmp_path)
                os.remove(tmp_path)

                if remote_hash is None:
                    report_lines.append(
                        f"{fname}: [COLOR red]Cloud-Datei defekt oder Hash Fehler[/COLOR]"
                    )
                    _log(
                        f"Hash für Cloud-Datei {remote_url} konnte nicht berechnet werden (defekt).",
                        xbmc.LOGERROR,
                    )
                    continue

                if local_hash == remote_hash:
                    status = "[COLOR lime]identisch[/COLOR]"
                    _log(f"Datei {fname}: Lokal und Cloud identisch.", xbmc.LOGDEBUG)
                else:
                    status = "[COLOR orange]Hash unterschiedlich![/COLOR]"
                    _log(
                        f"Datei {fname}: Lokal und Cloud unterschiedlich.",
                        xbmc.LOGWARNING,
                    )
                report_lines.append(
                    f"{fname}:\nLokal:  {local_hash}\nCloud:  {remote_hash}\nStatus: {status}"
                )
            else:
                report_lines.append(
                    f"{fname}: [COLOR yellow]Nicht in Cloud gefunden! (Status: {resp.status_code})[/COLOR]"
                )
                _log(
                    f"Datei {fname} nicht in Cloud gefunden (Status: {resp.status_code}).",
                    xbmc.LOGINFO,
                )
        except requests.exceptions.RequestException as e:
            report_lines.append(
                f"{fname}: [COLOR red]Cloud Netzwerk Fehler ({e})[/COLOR]"
            )
            _log(f"Cloud-Netzwerkfehler für {fname}: {e}", xbmc.LOGERROR)
        except Exception as e:  # Dies ist jetzt Zeile 1250, die vorher bemängelt wurde.
            report_lines.append(f"{fname}: [COLOR red]Unbekannter Fehler ({e})[/COLOR]")
            _log(f"Unbekannter Fehler für {fname}: {e}", xbmc.LOGERROR)

    msg = "\n\n".join(report_lines) or "Kein ZIP-Backup vorhanden."
    xbmcgui.Dialog().textviewer("Cloud/Local-Hash Abgleich", msg)
    _log("Cloud-ZIP-Hash-Report abgeschlossen.", xbmc.LOGINFO)


# --- SYNC/Repair-Assistent ---
def zip_sync_repair():
    _log("Starte ZIP-Sync- und Reparatur-Assistent.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "ZIP-Sync/Reparatur übersprungen: Cloud-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        return

    url_base, user, password = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "ZIP-Sync/Reparatur übersprungen: Cloud URL nicht konfiguriert.",
            xbmc.LOGWARNING,
        )
        return

    zips = [f for f in sorted(os.listdir(ADDON_DIR)) if f.endswith(".zip")]
    if not zips:
        xbmcgui.Dialog().ok("SYNC/Reparatur", "Keine lokalen ZIP-Backups gefunden.")
        _log("Keine lokalen ZIP-Backups für Sync/Reparatur gefunden.", xbmc.LOGINFO)
        return

    report_lines = []
    repairable_items = []  # Stores (fname, remote_url, local_hash)

    for fname in zips:
        _log(f"Verarbeite ZIP für Sync/Reparatur: {fname}.", xbmc.LOGDEBUG)
        local_path = os.path.join(ADDON_DIR, fname)
        local_hash = file_hash(local_path)

        if local_hash is None:
            report_lines.append(
                f"{fname}: [COLOR red]Lokal defekt ({local_path})[/COLOR]"
            )
            _log(
                f"Lokaler Hash für {fname} konnte nicht berechnet werden (defekt).",
                xbmc.LOGERROR,
            )
            continue

        remote_url = f"{url_base}/{fname}"
        try:
            _log(
                f"Versuche Cloud-Version von {fname} abzurufen: {remote_url}",
                xbmc.LOGDEBUG,
            )
            resp = requests.get(
                remote_url,
                auth=(user, password) if user and password else None,
                timeout=60,
            )
            if resp.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(resp.content)
                    tmp_path = tmp.name  # KORREKTUR: tmp.name statt tmp.File
                remote_hash = file_hash(tmp_path)
                os.remove(tmp_path)

                if remote_hash is None:
                    report_lines.append(
                        f"{fname}: [COLOR red]Cloud-Datei defekt oder Hash Fehler ({remote_url})[/COLOR]"
                    )
                    _log(
                        f"Hash für Cloud-Datei {remote_url} konnte nicht berechnet werden (defekt).",
                        xbmc.LOGERROR,
                    )
                    continue

                if local_hash == remote_hash:
                    status = "[COLOR lime]identisch[/COLOR]"
                    _log(f"Datei {fname}: Lokal und Cloud identisch.", xbmc.LOGDEBUG)
                else:
                    status = "[COLOR orange]unterschiedlich (kann aus Cloud repariert werden)[/COLOR]"
                    repairable_items.append((fname, remote_url, local_hash))
                    _log(
                        f"Datei {fname}: Lokal und Cloud unterschiedlich. Hinzugefügt zu Reparaturliste.",
                        xbmc.LOGINFO,
                    )
                report_lines.append(
                    f"{fname}:\nLokal:  {local_hash}\nCloud:  {remote_hash}\nStatus: {status}"
                )
            else:  # File not found in cloud
                status = (
                    "[COLOR yellow]Fehlt in Cloud – kann hochgeladen werden[/COLOR]"
                )
                report_lines.append(
                    f"{fname}:\nLokal: {local_hash}\nCloud: (Fehlt!)\nStatus: {status}"
                )
                # remote_url is None for upload
                repairable_items.append((fname, None, local_hash))
                _log(
                    f"Datei {fname} fehlt in Cloud. Hinzugefügt zu Upload-Liste.",
                    xbmc.LOGINFO,
                )
        except requests.exceptions.RequestException as e:
            report_lines.append(
                f"{fname}: [COLOR red]Cloud Netzwerk Fehler ({e})[/COLOR]"
            )
            _log(f"Cloud-Netzwerkfehler für {fname}: {e}", xbmc.LOGERROR)
        except Exception as e:
            report_lines.append(f"{fname}: [COLOR red]Unbekannter Fehler ({e})[/COLOR]")
            _log(f"Unbekannter Fehler für {fname}: {e}", xbmc.LOGERROR)

    xbmcgui.Dialog().textviewer(
        "SYNC/Reparatur-Bericht",
        "\n\n".join(report_lines) or "Keine ZIP-Backups vorhanden.",
    )

    if not repairable_items:
        xbmcgui.Dialog().notification(
            "SYNC-Reparatur",
            "Nichts zu reparieren/synchronisieren!",
            xbmcgui.NOTIFICATION_INFO,
        )
        _log("Keine reparierbaren/synchronisierbaren Elemente gefunden.", xbmc.LOGINFO)
        return

    actions = [
        "Fehlende Backups in Cloud hochladen",
        "Lokale Backups vom Cloud-Backup ersetzen (wenn unterschiedlich)",
        "Abbrechen",
    ]
    choice = xbmcgui.Dialog().select("SYNC & Repair", actions)
    if choice == -1 or choice == 2:
        _log("Sync- und Reparatur-Aktion vom Benutzer abgebrochen.", xbmc.LOGINFO)
        return

    # Hochladen fehlender ZIPs in Cloud
    if choice == 0:
        _log("Starte Upload fehlender Backups in die Cloud.", xbmc.LOGINFO)
        for fname, cloudurl, _ in repairable_items:
            if cloudurl is None:  # Means it's missing in cloud and needs upload
                local_path = os.path.join(ADDON_DIR, fname)
                dest_url = f"{url_base}/{fname}"
                try:
                    with open(local_path, "rb") as f:
                        resp = requests.put(
                            dest_url,
                            data=f,
                            auth=(user, password) if user and password else None,
                            timeout=120,  # Longer timeout for upload
                        )
                    if 200 <= resp.status_code < 400:
                        xbmcgui.Dialog().notification(
                            "SYNC-Upload",
                            f"{fname} hochgeladen.",
                            xbmcgui.NOTIFICATION_INFO,
                        )
                        log_sync(
                            "UPLOAD_TO_CLOUD", fname, "Uploaded missing local backup."
                        )
                        _log(f"SYNC-Upload erfolgreich: {fname}.", xbmc.LOGINFO)
                    else:
                        _log(
                            f"SYNC-Upload fehlgeschlagen: Status {resp.status_code} für {dest_url}",
                            xbmc.LOGERROR,
                        )
                        xbmcgui.Dialog().notification(
                            "SYNC-Upload Fehler",
                            f"Hochladen von {fname} fehlgeschlagen: Status {resp.status_code}",
                            xbmcgui.NOTIFICATION_ERROR,
                        )
                        log_sync(
                            "ERROR_SYNC", fname, f"Upload failed: {resp.status_code}"
                        )
                except requests.exceptions.RequestException as e:
                    _log(f"SYNC-Upload Netzwerkfehler: {e}", xbmc.LOGERROR)
                    xbmcgui.Dialog().notification(
                        "SYNC-Upload Fehler", str(e), xbmcgui.NOTIFICATION_ERROR
                    )
                    log_sync("ERROR_SYNC", fname, f"Upload network error: {e}")

    # Lokale Backups mit Cloud überschreiben
    elif choice == 1:
        _log("Starte Reparatur lokaler Backups aus der Cloud.", xbmc.LOGINFO)
        for fname, cloudurl, local_hash in repairable_items:
            if cloudurl is not None:
                local_path = os.path.join(ADDON_DIR, fname)
                try:
                    resp = requests.get(
                        cloudurl,
                        auth=(user, password) if user and password else None,
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        # Before overwriting, make a .bak_
                        if os.path.exists(local_path):
                            timestr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            shutil.copy2(
                                local_path, f"{local_path}{BACKUP_SUFFIX}{timestr}"
                            )
                            _log(
                                f"Lokales Backup von {fname} vor Überschreiben gesichert.",
                                xbmc.LOGDEBUG,
                            )
                        with open(local_path, "wb") as f:
                            f.write(resp.content)
                        xbmcgui.Dialog().notification(
                            "SYNC-Repair",
                            f"{fname} ersetzt aus Cloud.",
                            xbmcgui.NOTIFICATION_INFO,
                        )
                        log_sync(
                            "REPAIR_FROM_CLOUD",
                            fname,
                            "Replaced local backup from cloud.",
                        )
                        _log(
                            f"SYNC-Reparatur erfolgreich: {fname} aus Cloud ersetzt.",
                            xbmc.LOGINFO,
                        )
                    else:
                        _log(
                            f"SYNC-Reparatur fehlgeschlagen: Status {resp.status_code} für {cloudurl}",
                            xbmc.LOGERROR,
                        )
                        xbmcgui.Dialog().notification(
                            "SYNC-Repair Fehler",
                            f"Reparatur von {fname} fehlgeschlagen: Status {resp.status_code}",
                            xbmcgui.NOTIFICATION_ERROR,
                        )
                        log_sync(
                            "ERROR_SYNC", fname, f"Repair failed: {resp.status_code}"
                        )
                except requests.exceptions.RequestException as e:
                    _log(f"SYNC-Reparatur Netzwerkfehler: {e}", xbmc.LOGERROR)
                    xbmcgui.Dialog().notification(
                        "SYNC-Repair Fehler", str(e), xbmcgui.NOTIFICATION_ERROR
                    )
                    log_sync("ERROR_SYNC", fname, f"Repair network error: {e}")


# --- Sync-Protokoll ---
def log_sync(action, filename, info=""):
    _log(f"Protokolliere Sync-Ereignis: {action} | {filename} | {info}", xbmc.LOGINFO)
    try:
        with open(SYNC_LOG(), "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {action} | {os.path.basename(filename)} | {info}\n")

        # Only notify for certain actions to avoid spamming
        noti_title = "Backup-Synchronisierung"
        if action in ("UPLOAD_TO_CLOUD", "REPAIR_FROM_CLOUD"):
            xbmcgui.Dialog().notification(
                noti_title,
                f"{action}: {os.path.basename(filename)}",
                xbmcgui.NOTIFICATION_INFO,
            )
        elif action in ("DIFF_HASH", "ERROR_SYNC"):
            xbmcgui.Dialog().notification(
                noti_title,
                f"Fehler: {action} für {os.path.basename(filename)}",
                xbmcgui.NOTIFICATION_WARNING,
            )
    except Exception as e:
        _log(f"SYNC-Log Fehler: {e}", xbmc.LOGERROR)


def show_sync_protocol():
    _log("Zeige Sync-Protokoll.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log("Sync-Protokoll übersprungen: Cloud-Funktionen deaktiviert.", xbmc.LOGINFO)
        return

    path = SYNC_LOG()
    if not os.path.exists(path):
        xbmcgui.Dialog().ok(
            "SYNC-Protokoll", "Noch keine Sync-/Repair-Vorgänge durchgeführt."
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        _log("Kein Sync-Protokoll gefunden.", xbmc.LOGINFO)
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read() or "(leer)"
    xbmcgui.Dialog().textviewer("SYNC/Reparatur-Protokoll", content)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    _log("Sync-Protokoll angezeigt.", xbmc.LOGINFO)


# --- Multiuser-Intervall-Sync beim Start ---
def auto_sync_cloud_interval_user():
    _log("Starte automatische Cloud-Synchronisierung.", xbmc.LOGINFO)
    # Master switch for all cloud features
    if not get_global_feature_settings()["enable_cloud_features"]:
        _log(
            "Auto-Sync übersprungen: Cloud features disabled in addon settings.",
            xbmc.LOGINFO,
        )
    if get_setting("auto_update_streams", "false") == "true":
        update_streams_from_url()

        return

    user = "default"
    cfg = get_user_config(user)
    hours = cfg.get("sync_hours", 24)
    AUTO_SYNC_MARK = os.path.join(ADDON_DIR, f"auto_sync_last_{user}.txt")
    now = datetime.datetime.now()
    needsync = True

    # Check if auto sync is enabled in addon settings
    addon = get_addon_settings()
    if not addon.getSettingBool("cloud_auto_sync_interval"):
        _log(
            "Auto-Sync by interval is disabled in settings for current user.",
            xbmc.LOGINFO,
        )
        return  # Do nothing if disabled

    if os.path.exists(AUTO_SYNC_MARK):
        try:
            with open(AUTO_SYNC_MARK, "r") as f:
                last_sync_str = f.read().strip()
                if last_sync_str:  # Check if string is not empty
                    last = datetime.datetime.fromisoformat(last_sync_str)
                    if (now - last).total_seconds() < hours * 3600:
                        needsync = False
                        _log(
                            f"Auto-Sync noch nicht fällig für Benutzer {user}. Nächste Synchronisierung in {(hours * 3600 - (now - last).total_seconds()) / 3600:.1f} Stunden.",
                            xbmc.LOGDEBUG,
                        )
                else:
                    _log(
                        f"Leere Auto-Sync-Marker-Datei für {user}. Führe Synchronisierung durch.",
                        xbmc.LOGWARNING,
                    )
        except Exception as e:
            _log(
                f"Fehler beim Lesen des Auto-Sync-Markers für {user}: {e}. Führe Synchronisierung durch.",
                xbmc.LOGERROR,
            )
            needsync = True  # If error reading, better to sync

    if needsync:
        _log(
            f"Führe automatische Synchronisierung für Benutzer {user} aus.",
            xbmc.LOGINFO,
        )
        # Call the sync/repair assistant
        zip_sync_repair()
        with open(AUTO_SYNC_MARK, "w") as f:
            f.write(now.isoformat())
    else:
        _log(
            f"Auto-Sync für Benutzer {user} übersprungen. Intervall noch nicht abgelaufen.",
            xbmc.LOGINFO,
        )


# Call auto-sync at startup (when addon is loaded)
auto_sync_cloud_interval_user()


# --- New Features Implementations ---


def missing_icons():
    _log("Starte Suche nach fehlenden Icons.", xbmc.LOGINFO)
    streams = load_json(STREAMS_JSON, {})
    missing_report = []

    for domain, stream_list in streams.items():
        for stream in stream_list:
            icon_path_in_json = stream.get("icon")

            # Check if an explicit icon path is given and exists
            explicit_icon_exists = False
            if icon_path_in_json:
                full_icon_path = os.path.join(ADDON_DIR, icon_path_in_json)
                if os.path.exists(full_icon_path):
                    explicit_icon_exists = True
                    _log(
                        f"Explizites Icon {icon_path_in_json} für Stream '{stream.get('name')}' gefunden.",
                        xbmc.LOGDEBUG,
                    )

            # Check inferred paths if no explicit icon exists or was invalid
            inferred_icon_exists = False
            if not explicit_icon_exists:
                normalized_stream_name = _normalize_filename(stream.get("name", ""))
                inferred_stream_path = os.path.join(
                    IMAGES_STREAMS_DIR, f"{normalized_stream_name}.png"
                )
                normalized_domain_name = _normalize_filename(domain)
                inferred_category_path = os.path.join(
                    IMAGES_CATEGORIES_DIR, f"{normalized_domain_name}.png"
                )

                if os.path.exists(inferred_stream_path):
                    inferred_icon_exists = True
                    _log(
                        f"Inferiertes Stream-Icon {inferred_stream_path} für '{stream.get('name')}' gefunden.",
                        xbmc.LOGDEBUG,
                    )
                elif os.path.exists(inferred_category_path):
                    inferred_icon_exists = True
                    _log(
                        f"Inferiertes Kategorie-Icon {inferred_category_path} für '{stream.get('name')}' gefunden.",
                        xbmc.LOGDEBUG,
                    )

            # Report based on findings
            if explicit_icon_exists or inferred_icon_exists:
                pass  # All good
            elif icon_path_in_json:
                missing_report.append(
                    f"- Domain '{domain}', Stream '{stream.get('name', 'Unbekannt')}': Explizites Icon '{icon_path_in_json}' fehlt."
                )
                _log(
                    f"Fehlendes explizites Icon gemeldet: {icon_path_in_json}",
                    xbmc.LOGWARNING,
                )
            else:
                missing_report.append(
                    f"- Domain '{domain}', Stream '{stream.get('name', 'Unbekannt')}': Kein Icon-Pfad in JSON definiert und nicht inferierbar."
                )
                _log(
                    f"Fehlendes Icon (nicht definiert und nicht inferierbar) gemeldet für '{stream.get('name')}'.",
                    xbmc.LOGWARNING,
                )

    msg = "\n".join(missing_report)
    if not msg:
        msg = "Alle Streams haben definierte Icons, die lokal existieren oder inferierbar sind."
        _log("Alle Icons gefunden/inferierbar.", xbmc.LOGINFO)
    else:
        _log("Bericht über fehlende Icons generiert.", xbmc.LOGWARNING)

    xbmcgui.Dialog().textviewer("Fehlende Icons/Thumbs", msg)


def zip_diff_preview():
    _log("Starte ZIP-Diff-Vorschau.", xbmc.LOGINFO)
    zip_path = xbmcgui.Dialog().browse(
        1,
        "ZIP-Backup zum Vergleich auswählen",
        "files",
        ".zip",
        False,
        False,
        ADDON_DIR,
    )
    if not zip_path or not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        xbmcgui.Dialog().ok(
            "ZIP Diff", "Kein gültiges ZIP ausgewählt oder abgebrochen."
        )
        _log("ZIP-Diff abgebrochen oder ungültige Datei ausgewählt.", xbmc.LOGINFO)
        return

    report_lines = [f"Vergleich von {os.path.basename(zip_path)} mit lokalen Dateien:"]
    _log(f"Analysiere ZIP-Datei: {zip_path}", xbmc.LOGDEBUG)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zip_contents = zf.namelist()
            _log(f"Inhalt des ZIP: {zip_contents}", xbmc.LOGDEBUG)

            for item_name in zip_contents:
                if item_name.endswith("/"):  # Skip directories
                    continue

                local_path = os.path.join(ADDON_DIR, item_name)

                item_status = f"- {item_name}: "

                # Compare content by hash (simplified)
                # Pass the file-like object directly to file_hash
                with zf.open(item_name) as zf_file_obj:
                    zip_item_hash = file_hash(zf_file_obj, chunk_size=8192)

                if os.path.exists(local_path):
                    local_item_hash = file_hash(local_path)
                    if zip_item_hash == local_item_hash:
                        item_status += "[COLOR lime]Identisch[/COLOR]"
                        _log(
                            f"ZIP-Datei {item_name}: Lokal und ZIP identisch.",
                            xbmc.LOGDEBUG,
                        )
                    else:
                        item_status += "[COLOR orange]Inhalt unterschiedlich[/COLOR]"
                        _log(
                            f"ZIP-Datei {item_name}: Inhalt unterschiedlich.",
                            xbmc.LOGINFO,
                        )
                else:
                    item_status += "[COLOR yellow]Lokal nicht vorhanden[/COLOR]"
                    _log(f"ZIP-Datei {item_name}: Lokal nicht vorhanden.", xbmc.LOGINFO)
                report_lines.append(item_status)

            # Check for local files not in zip
            # Only consider files that could be part of a backup (json, log, specific flags)
            local_backup_relevant_files = []
            for f in os.listdir(ADDON_DIR):
                if (
                    f.endswith(".json")
                    or f.endswith(".log")
                ):
                    # Exclude the backup/broken files themselves
                    if (
                        not (f.startswith("backup_") and f.endswith(".zip"))
                        and not (f.startswith("VIP_SNAPSHOT_") and f.endswith(".zip"))
                        and not BROKEN_JSON_PREFIX in f
                        and not BACKUP_SUFFIX in f
                        and not f.endswith(ZIP_TAG_EXTENSION)
                        and not f.endswith(ENCRYPTED_EXTENSION)
                    ):
                        local_backup_relevant_files.append(f)
            _log(
                f"Lokal vorhandene, relevante Dateien: {local_backup_relevant_files}",
                xbmc.LOGDEBUG,
            )

            for local_fname in local_backup_relevant_files:
                if local_fname not in zip_contents:
                    report_lines.append(
                        f"- {local_fname}: [COLOR cyan]Lokal vorhanden, nicht im ZIP[/COLOR]"
                    )
                    _log(
                        f"Lokale Datei {local_fname} nicht im ZIP-Archiv gefunden.",
                        xbmc.LOGINFO,
                    )

    except Exception as e:
        _log(f"ZIP Diff Fehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Fehler", f"Fehler beim ZIP-Vergleich: {e}", xbmcgui.NOTIFICATION_ERROR
        )
        return

    xbmcgui.Dialog().textviewer("ZIP Diff Preview", "\n".join(report_lines))
    _log("ZIP-Diff-Vorschau abgeschlossen.", xbmc.LOGINFO)


def cloud_backup_browser():
    _log("Starte Cloud-Backup-Browser.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_cloud_features"]:
        xbmcgui.Dialog().notification(
            "Cloud", "Cloud-Funktionen sind deaktiviert.", xbmcgui.NOTIFICATION_WARNING
        )
        _log(
            "Cloud-Backup-Browser übersprungen: Cloud-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        return

    url_base, user, password = get_cloud_credentials()
    if not url_base:
        xbmcgui.Dialog().notification(
            "Fehler", "Cloud URL nicht konfiguriert.", xbmcgui.NOTIFICATION_ERROR
        )
        _log(
            "Cloud-Backup-Browser übersprungen: Cloud URL nicht konfiguriert.",
            xbmc.LOGWARNING,
        )
        return

    # List local zip files as suggestions for what might be in the cloud
    local_zips = sorted(
        [
            f
            for f in os.listdir(ADDON_DIR)
            if f.endswith(".zip") or f.endswith(ENCRYPTED_EXTENSION)
        ]
    )
    suggestions = [os.path.basename(f) for f in local_zips]

    # Add a common naming pattern suggestion
    current_user = "default"
    now_str = datetime.datetime.now().strftime("%Y%m%d")
    suggestions.insert(0, f"backup_{now_str}_{current_user}.zip")
    suggestions.insert(0, f"VIP_SNAPSHOT_{now_str}_{current_user}.zip")
    suggestions = sorted(list(set(suggestions)))  # Remove duplicates and sort
    _log(f"Vorschläge für Cloud-Dateien: {suggestions}", xbmc.LOGDEBUG)

    # Let user select or manually enter a filename
    selected_idx = xbmcgui.Dialog().select(
        "Backup aus Cloud wählen oder Namen eingeben",
        suggestions + ["[Anderen Dateinamen eingeben]"],
    )

    if selected_idx == -1:  # Cancelled
        _log("Cloud-Backup-Browser abgebrochen.", xbmc.LOGINFO)
        return

    selected_filename = ""
    if selected_idx < len(suggestions):
        selected_filename = suggestions[selected_idx]
    else:  # "Anderen Dateinamen eingeben"
        selected_filename = xbmcgui.Dialog().input(
            "Dateiname in der Cloud (z.B. backup_YYYYMMDD_HHMMSS.zip)"
        )
        if not selected_filename or not selected_filename.strip():
            xbmcgui.Dialog().notification(
                "Abbruch", "Kein Dateiname eingegeben.", xbmcgui.NOTIFICATION_WARNING
            )
            _log(
                "Cloud-Backup-Browser abgebrochen: Kein Dateiname eingegeben.",
                xbmc.LOGINFO,
            )
            return
        if not selected_filename.lower().endswith(
            ".zip"
        ) and not selected_filename.lower().endswith(ENCRYPTED_EXTENSION):
            xbmcgui.Dialog().notification(
                "Hinweis",
                "Dateiname sollte .zip oder .enc enden.",
                xbmcgui.NOTIFICATION_INFO,
            )
            _log(
                f"Hinweis: Dateiname {selected_filename} endet nicht mit .zip oder .enc.",
                xbmc.LOGINFO,
            )

    remote_url = f"{url_base}/{selected_filename}"
    target_path = os.path.join(ADDON_DIR, selected_filename)
    _log(
        f"Versuche, '{selected_filename}' von {remote_url} herunterzuladen nach {target_path}.",
        xbmc.LOGDEBUG,
    )

    if os.path.exists(target_path):
        if not xbmcgui.Dialog().yesno(
            "Datei existiert",
            f"'{os.path.basename(target_path)}' existiert bereits lokal. Überschreiben?",
        ):
            _log(
                "Download abgebrochen: Datei existiert bereits und Überschreiben verweigert.",
                xbmc.LOGINFO,
            )
            return

    try:
        resp = requests.get(
            remote_url, auth=(user, password) if user and password else None, timeout=60
        )
        if resp.status_code == 200:
            with open(target_path, "wb") as f:
                f.write(resp.content)
            xbmcgui.Dialog().ok(
                "Download erfolgreich",
                f"'{os.path.basename(selected_filename)}' wurde heruntergeladen.",
            )
            log_history("CLOUD_BROWSE_DOWNLOAD", target_path, f"from {remote_url}")
            _log(f"Download erfolgreich: {selected_filename}.", xbmc.LOGINFO)

            # Offer to restore if it's a zip
            if selected_filename.lower().endswith(".zip"):
                if xbmcgui.Dialog().yesno(
                    "Wiederherstellen?",
                    f"Möchten Sie das heruntergeladene ZIP-Backup '{os.path.basename(selected_filename)}' jetzt wiederherstellen?",
                ):
                    _log(
                        f"Wiederherstellung von heruntergeladenem ZIP {selected_filename} angefordert.",
                        xbmc.LOGINFO,
                    )
                    temp_param_string = f"?action=zip_restore_file&file={urllib.parse.quote_plus(target_path)}"
                    router(temp_param_string)
            elif selected_filename.lower().endswith(ENCRYPTED_EXTENSION):
                if xbmcgui.Dialog().yesno(
                    "Entschlüsseln?",
                    f"Möchten Sie die heruntergeladene verschlüsselte Datei '{os.path.basename(selected_filename)}' jetzt entschlüsseln?",
                ):
                    _log(
                        f"Entschlüsselung von heruntergeladener verschlüsselter Datei {selected_filename} angefordert.",
                        xbmc.LOGINFO,
                    )
                    password_for_decrypt = xbmcgui.Dialog().input(
                        "Passwort zum Entschlüsseln", type=xbmcgui.INPUT_ALPHANUM
                    )
                    if password_for_decrypt:
                        dec_file = decrypt_file(target_path, password_for_decrypt)
                        if dec_file:
                            xbmcgui.Dialog().ok(
                                "Entschlüsselt",
                                f"Datei entschlüsselt und gespeichert als: {os.path.basename(dec_file)}",
                            )
                            os.remove(target_path)  # Clean up encrypted file
                            _log(
                                f"Entschlüsselung erfolgreich: {dec_file}.",
                                xbmc.LOGINFO,
                            )
                        else:
                            xbmcgui.Dialog().notification(
                                "Fehler",
                                "Entschlüsselung fehlgeschlagen!",
                                xbmcgui.NOTIFICATION_ERROR,
                            )
                            _log(
                                "Entschlüsselung nach Download fehlgeschlagen.",
                                xbmc.LOGERROR,
                            )
                    else:
                        xbmcgui.Dialog().notification(
                            "Abbruch",
                            "Kein Passwort zum Entschlüsseln eingegeben.",
                            xbmcgui.NOTIFICATION_WARNING,
                        )
                        _log(
                            "Entschlüsselung nach Cloud-Download abgebrochen: Kein Passwort.",
                            xbmc.LOGINFO,
                        )

            else:
                _log(
                    f"Cloud-Download fehlgeschlagen: Status {resp.status_code} für {remote_url}",
                    xbmc.LOGERROR,
                )
                xbmcgui.Dialog().notification(
                    "Fehler",
                    f"Datei '{selected_filename}' nicht in der Cloud gefunden oder Zugriff verweigert (Status: {resp.status_code}).",
                    xbmcgui.NOTIFICATION_ERROR,
                )
    except requests.exceptions.RequestException as e:
        _log(f"Cloud-Backup-Browser Netzwerkfehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Netzwerkfehler",
            f"Verbindung zur Cloud fehlgeschlagen: {e}",
            xbmcgui.NOTIFICATION_ERROR,
        )
    except Exception as e:
        _log(f"Unbekannter Fehler im Cloud-Backup-Browser: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Fehler",
            f"Unbekannter Fehler beim Cloud-Download: {e}",
            xbmcgui.NOTIFICATION_ERROR,
        )


# Neue Funktionen zur Filterung/Sortierung
def filter_streams(streams, filter_type="alphabetical"):
    filtered = []
    for domain, stream_list in streams.items():
        for stream in stream_list:
            stream_copy = stream.copy()
            stream_copy["domain"] = domain
            filtered.append(stream_copy)

    if filter_type == "alphabetical":
        filtered.sort(key=lambda x: x["name"])
    elif filter_type == "genre":
        filtered.sort(key=lambda x: x.get("genre", ""))
    elif filter_type == "newest":
        filtered.sort(key=lambda x: x.get("added", ""), reverse=True)
    elif filter_type == "popularity":
        playcounts = load_json(PLAYCOUNT_JSON_PATH(), {})
        filtered.sort(key=lambda x: playcounts.get(x["url"], 0), reverse=True)

    return filtered


def show_filter_menu():
    options = [
        ("Alphabetisch", "alphabetical"),
        ("Nach Genre", "genre"),
        ("Neueste zuerst", "newest"),
        ("Beliebteste zuerst", "popularity"),
    ]

    selected = xbmcgui.Dialog().select("Filter/Sortierung", [opt[0] for opt in options])
    if selected >= 0:
        return options[selected][1]
    return None


# Favoriten Funktionen
FAVORITES_JSON = os.path.join(ADDON_DIR, "favorites.json")


def get_favorites():
    return load_json(FAVORITES_JSON, [])


def save_favorites(favorites):
    save_json(FAVORITES_JSON, favorites)


def toggle_favorite(stream_data):
    favorites = get_favorites()
    url = stream_data["url"]

    if any(fav["url"] == url for fav in favorites):
        favorites = [fav for fav in favorites if fav["url"] != url]
        added = False
    else:
        favorites.append(stream_data)
        added = True

    save_favorites(favorites)
    return added


def show_favorites():
    favorites = get_favorites()
    if not favorites:
        xbmcgui.Dialog().ok("Favoriten", "Keine Favoriten gespeichert")
        return

    for fav in favorites:
        li = xbmcgui.ListItem(label=fav["name"])
        li.setProperty("IsPlayable", "true")
        url = f"{BASE_URL}?action=play_stream&domain=favorites&name={urllib.parse.quote_plus(fav['name'])}&url={urllib.parse.quote_plus(fav['url'])}"
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def get_current_track_info(url):
    try:
        # Beispiel für Icecast/Shoutcast Streams
        if "icecast" in url or "shoutcast" in url:
            headers = {"Icy-MetaData": "1"}
            response = requests.get(url, headers=headers, stream=True, timeout=3)
            metaint = int(response.headers.get("icy-metaint", 0))
            if metaint > 0:
                response.raw.read(metaint)
                metadata = response.raw.read(16 * 1024).decode("utf-8", errors="ignore")
                # Extrahiere Titel aus "StreamTitle='...';"
                title = re.search(r"StreamTitle='(.*?)';", metadata)
                if title:
                    return {"title": title.group(1)}

    except Exception as e:
        _log(f"Metadaten Fehler: {e}", xbmc.LOGERROR)
    return None


def update_now_playing():
    track_info = get_current_track_info(xbmc.Player().getPlayingFile())
    if track_info:
        xbmc.executebuiltin(
            f"Notification({track_info.get('title','Unbekannter Titel')},Now Playing)"
        )


def add_stream_manually():
    dialog = xbmcgui.Dialog()
    name = dialog.input("Stream Name")
    if not name:
        return

    url = dialog.input("Stream URL")
    if not url:
        return

    domain = dialog.input("Kategorie/Genre")
    if not domain:
        domain = "Benutzerdefiniert"

    streams = load_json(STREAMS_JSON, {})
    if domain not in streams:
        streams[domain] = []

    streams[domain].append(
        {"name": name, "url": url, "added": datetime.datetime.now().isoformat()}
    )

    save_json(STREAMS_JSON, streams)
    xbmcgui.Dialog().notification("Erfolg", f"{name} wurde hinzugefügt")


def import_playlist():
    path = xbmcgui.Dialog().browse(1, "Playlist auswählen", "files", ".m3u|.pls")
    if not path:
        return

    try:
        with open(path, "r") as f:
            content = f.read()

        streams = {}
        for line in content.split("\n"):
            if line.startswith("http"):
                url = line.strip()
                name = f"Importierter Stream {len(streams)+1}"
                streams[name] = {"name": name, "url": url}

        if streams:
            domain = os.path.splitext(os.path.basename(path))[0]
            all_streams = load_json(STREAMS_JSON, {})
            all_streams[domain] = list(streams.values())
            save_json(STREAMS_JSON, all_streams)
            xbmcgui.Dialog().notification(
                "Erfolg", f"{len(streams)} Streams importiert"
            )

    except Exception as e:
        xbmcgui.Dialog().notification("Fehler", str(e))


def update_streams_from_url():
    _log("Starte Update von externer URL.", xbmc.LOGINFO)
    url = xbmcgui.Dialog().input("Stream-Listen URL eingeben (JSON)", defaultt="https://")
    if not url:
        return

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            remote_streams = response.json()
            if not isinstance(remote_streams, dict):
                xbmcgui.Dialog().ok("Fehler", "Ungültiges Stream-Format")
                return

            local_streams = load_json(STREAMS_JSON, {})
            added_count = 0

            for domain, items in remote_streams.items():
                if domain not in local_streams:
                    local_streams[domain] = items
                    added_count += len(items)
                else:
                    for item in items:
                        exists = any(s.get("url") == item.get("url") for s in local_streams.get(domain, []))
                        if not exists:
                            local_streams[domain].append(item)
                            added_count += 1

            save_json(STREAMS_JSON, local_streams)
            xbmcgui.Dialog().notification("Stream-Update", f"{added_count} Streams hinzugefügt")
            _log(f"Stream-Update abgeschlossen: {added_count} Streams", xbmc.LOGINFO)
        else:
            xbmcgui.Dialog().ok("Fehler", f"HTTP {response.status_code}")

    except Exception as e:
        _log(f"Update Fehler: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Fehler", str(e))


def set_custom_image():
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    stream_name = params.get("name", "")
    domain = params.get("domain", "")

    if not stream_name or not domain:
        xbmcgui.Dialog().ok("Fehler", "Keine Stream-Daten übergeben")
        return

    image_path = xbmcgui.Dialog().browse(2, "Bild/Logo auswählen", "images", ".png|.jpg|.jpeg")
    if not image_path:
        return

    dest_dir = os.path.join(IMAGES_STREAMS_DIR, domain)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, f"{_normalize_filename(stream_name)}.png")
    shutil.copy(image_path, dest_path)

    streams = load_json(STREAMS_JSON, {})
    for stream in streams.get(domain, []):
        if stream.get("name") == stream_name:
            stream["icon"] = f"resources/images/streams/{domain}/{_normalize_filename(stream_name)}.png"
            break

    save_json(STREAMS_JSON, streams)
    xbmcgui.Dialog().notification("Erfolg", f"Logo für {stream_name} gesetzt")
    _log(f"Logo gesetzt für {stream_name} in {domain}", xbmc.LOGINFO)


def set_domain_image():
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    domain = params.get("domain", "")

    if not domain:
        xbmcgui.Dialog().ok("Fehler", "Keine Domain übergeben")
        return

    image_path = xbmcgui.Dialog().browse(2, "Domain-Logo auswählen", "images", ".png|.jpg|.jpeg")
    if not image_path:
        return

    dest_dir = os.path.join(IMAGES_STREAMS_DIR, domain)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, "domain_icon.png")
    shutil.copy(image_path, dest_path)

    xbmcgui.Dialog().notification("Erfolg", f"Logo für {domain} gesetzt")
    _log(f"Domain-Logo gesetzt für {domain}", xbmc.LOGINFO)


def streamstats():
    _log("Starte Stream-Statistik.", xbmc.LOGINFO)
    playcounts = load_json(PLAYCOUNT_JSON_PATH(), {})
    history = load_json(HISTORY_JSON_PATH(), [])

    report_lines = []
    report_lines.append("--- Playcount Statistik ---")
    if playcounts:
        # Sort by playcount, descending
        sorted_playcounts = sorted(
            playcounts.items(), key=lambda item: item[1], reverse=True
        )
        for url, count in sorted_playcounts[:10]:  # Top 10
            # Try to find the name in streams_json for better display
            stream_name = "Unbekannt"
            streams_data = load_json(STREAMS_JSON, {})
            for domain_streams in streams_data.values():
                for s in domain_streams:
                    if s.get("url") == url:
                        stream_name = s.get("name", "Unbekannt")
                        break
                if stream_name != "Unbekannt":
                    break
            report_lines.append(f"- {stream_name}: {count} Wiedergaben")
        _log(
            f"Playcount-Statistik für {len(sorted_playcounts)} Streams erstellt.",
            xbmc.LOGDEBUG,
        )
    else:
        report_lines.append("Noch keine Wiedergabedaten vorhanden.")
        _log("Keine Playcount-Daten gefunden.", xbmc.LOGINFO)

    report_lines.append("\n--- Letzte Wiedergaben ---")
    if history:
        # Sort by played timestamp, descending (most recent first)
        sorted_history = sorted(
            history, key=lambda x: x.get("played", ""), reverse=True
        )
        for entry in sorted_history[:10]:  # Last 10 plays
            report_lines.append(
                f"- {entry.get('name', 'Unbekannt')} (Domain: {entry.get('domain', 'N/A')}) - {entry.get('played', 'N/A')}"
            )
        _log(
            f"History-Statistik für {len(sorted_history)} Einträge erstellt.",
            xbmc.LOGDEBUG,
        )
    else:
        report_lines.append("Kein Wiedergabeverlauf vorhanden.")
        _log("Keine History-Daten gefunden.", xbmc.LOGINFO)

    xbmcgui.Dialog().textviewer("Stream Statistik", "\n".join(report_lines))
    _log("Stream-Statistik angezeigt.", xbmc.LOGINFO)


def recentchanged():
    _log("Starte Suche nach kürzlich geänderten/hinzugefügten Streams.", xbmc.LOGINFO)
    streams = load_json(STREAMS_JSON, {})
    report_lines = []

    report_lines.append(
        "--- Kürzlich hinzugefügt (letzte {} Tage) ---".format(RECENT_DAYS)
    )
    new_streams = []
    for domain, stream_list in streams.items():
        for stream in stream_list:
            if is_recent(stream):
                new_streams.append(
                    f"- {stream.get('name', 'Unbekannt')} (Domain: {domain})"
                )
    if new_streams:
        report_lines.extend(new_streams)
        _log(f"{len(new_streams)} neue Streams gefunden.", xbmc.LOGDEBUG)
    else:
        report_lines.append("Keine kürzlich hinzugefügten Streams.")
        _log("Keine neuen Streams gefunden.", xbmc.LOGINFO)

    report_lines.append(
        "\n--- Kürzlich aktualisiert (letzte {} Tage) ---".format(RECENT_DAYS)
    )
    updated_streams = []
    for domain, stream_list in streams.items():
        for stream in stream_list:
            # Check if updated, but not newly added (to avoid double counting)
            if is_updated(stream) and not is_recent(stream):
                updated_streams.append(
                    f"- {stream.get('name', 'Unbekannt')} (Domain: {domain})"
                )
    if updated_streams:
        report_lines.extend(updated_streams)
        _log(f"{len(updated_streams)} aktualisierte Streams gefunden.", xbmc.LOGDEBUG)
    else:
        report_lines.append("Keine kürzlich aktualisierten Streams.")
        _log("Keine aktualisierten Streams gefunden.", xbmc.LOGINFO)

    xbmcgui.Dialog().textviewer("Zuletzt hinzugefügt/geändert", "\n".join(report_lines))
    _log("Bericht 'Zuletzt hinzugefügt/geändert' angezeigt.", xbmc.LOGINFO)


def github_features_menu():
    """Placeholder function for GitHub-related features."""
    _log("GitHub-Features-Menü aufgerufen.", xbmc.LOGINFO)
    if not get_global_feature_settings()["enable_github_features"]:
        xbmcgui.Dialog().notification(
            "GitHub",
            "GitHub-Funktionen sind deaktiviert.",
            xbmcgui.NOTIFICATION_WARNING,
        )
        _log(
            "GitHub-Features-Menü übersprungen: GitHub-Funktionen deaktiviert.",
            xbmc.LOGINFO,
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return

    # Here you would add menu items for GitHub-specific functionalities
    # For example:
    # xbmcplugin.addDirectoryItem(
    #     handle=ADDON_HANDLE,
    #     url=f"{BASE_URL}?action=check_github_updates",
    #     listitem=xbmcgui.ListItem(label="Check for Addon Updates on GitHub"),
    #     isFolder=False
    # )
    # xbmcplugin.addDirectoryItem(
    #     handle=ADDON_HANDLE,
    #     url=f"{BASE_URL}?action=load_streams_from_github_gist",
    #     listitem=xbmcgui.ListItem(label="Load Streams from GitHub Gist"),
    #     isFolder=False
    # )

    xbmcgui.Dialog().notification(
        "GitHub",
        "GitHub-Funktionen sind aktiv, aber noch nicht implementiert.",
        xbmcgui.NOTIFICATION_INFO,
    )
    _log(
        "GitHub-Funktionen sind aktiv, aber Menü-Elemente noch nicht implementiert.",
        xbmc.LOGINFO,
    )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# Neue Funktionen für erweiterte History
def update_history(stream_data, duration_played=0):
    history = load_json(HISTORY_JSON_PATH(), [])

    # Existierenden Eintrag aktualisieren oder neuen erstellen
    existing = next((h for h in history if h["url"] == stream_data["url"]), None)

    if existing:
        existing["last_played"] = datetime.datetime.now().isoformat()
        existing["play_count"] = existing.get("play_count", 0) + 1
        existing["total_duration"] = existing.get("total_duration", 0) + duration_played
    else:
        history.append(
            {
                "name": stream_data["name"],
                "url": stream_data["url"],
                "domain": stream_data["domain"],
                "first_played": datetime.datetime.now().isoformat(),
                "last_played": datetime.datetime.now().isoformat(),
                "play_count": 1,
                "total_duration": duration_played,
            }
        )

    # Auf maximale Anzahl begrenzen (z.B. 100 Einträge)
    save_json(HISTORY_JSON_PATH(), history[-100:])


def show_enhanced_history():
    history = sorted(
        load_json(HISTORY_JSON_PATH(), []), key=lambda x: x.get("last_played", ""), reverse=True
    )

    for item in history:
        li = xbmcgui.ListItem(
            label=f"{item.get('name', 'Unknown')} [COLOR gray]({item.get('domain', 'Unknown')})[/COLOR]"
        )
        li.setInfo(
            "music",
            {
                "title": f"Abgespielt: {item.get('play_count', 0)}x",
                "duration": f"{item.get('total_duration', 0)//60} min",
            },
        )
        li.setProperty("IsPlayable", "true")

        context_menu = [
            (
                "Teilen",
                f"RunPlugin({BASE_URL}?action=share_stream&url={urllib.parse.quote_plus(item.get('url', ''))})",
            )
        ]
        li.addContextMenuItems(context_menu)

        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE,
            url=f"{BASE_URL}?action=play_stream&domain={urllib.parse.quote_plus(item.get('domain', 'Unknown'))}&name={urllib.parse.quote_plus(item.get('name', ''))}&url={urllib.parse.quote_plus(item.get('url', ''))}",
            listitem=li,
            isFolder=False,
        )

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


# Sharing-Funktionen
def generate_qr_code(url):
    try:
        import qrcode

        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image()
        temp_path = os.path.join(
            xbmcvfs.translatePath("special://temp"), "stream_qr.png"
        )
        img.save(temp_path)

        return temp_path
    except:
        return None


def share_stream(url):
    share_method = xbmcgui.Dialog().select(
        "Teilen über", ["QR-Code anzeigen", "Link kopieren", "E-Mail senden"]
    )

    if share_method == 0:  # QR-Code
        qr_path = generate_qr_code(url)
        if qr_path:
            xbmcgui.Dialog().browseSingle(1, "QR-Code", "pictures", qr_path)

    elif share_method == 1:  # Link kopieren
        xbmcgui.Dialog().textviewer("Stream Link", url)

    elif share_method == 2:  # E-Mail
        recipient = xbmcgui.Dialog().input("E-Mail Adresse")
        if recipient:
            subject = "Stream Link aus sKullsRadioSuite"
            body = f"Hier ist der Stream-Link:\n\n{url}"
            xbmc.executebuiltin(f"SendMail({recipient},{subject},{body})")

            # Suchfunktionen


def search_streams(search_term):
    _log(f"search_streams: Suche nach '{search_term}'", xbmc.LOGDEBUG)
    streams = load_json(STREAMS_JSON, {})
    _log(f"search_streams: Geladene Streams-Domains: {list(streams.keys())}", xbmc.LOGDEBUG)
    results = []

    if not search_term:
        return results

    search_lower = search_term.lower()

    for domain, stream_list in streams.items():
        for stream in stream_list:
            name = stream.get("name", "")
            genre = stream.get("genre", "")
            if not name:
                continue
            search_text = f"{name} {domain} {genre}".lower()
            if search_lower in search_text:
                results.append((domain, stream))

    _log(f"search_streams: {len(results)} Ergebnisse gefunden", xbmc.LOGDEBUG)
    return results


def show_search_results(results):
    _log(f"show_search_results: Zeige {len(results)} Ergebnisse", xbmc.LOGINFO)
    xbmcplugin.setContent(ADDON_HANDLE, "music")

    results_sorted = sorted(results, key=lambda x: x[0])

    for domain, stream in results_sorted:
        name = stream.get("name", "Unknown")
        url = stream.get("url", "")
        li = xbmcgui.ListItem(label=f"{name} [COLOR gray]({domain})[/COLOR]")
        li.setInfo("music", {"title": name, "album": domain})
        li.setProperty("IsPlayable", "true")
        icon_path = xbmcvfs.translatePath("special://home/addons/plugin.audio.sKullsRadioSuite/resources/media/favorite.png")
        li.setArt({"icon": icon_path, "thumb": icon_path})

        play_url = f"{BASE_URL}?action=play_stream&domain={urllib.parse.quote_plus(domain)}&name={urllib.parse.quote_plus(name)}&url={urllib.parse.quote_plus(url)}"
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=play_url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def show_search_dialog():
    _log("Starte Suche.", xbmc.LOGINFO)
    search_term = xbmcgui.Dialog().input("Suche nach Streams")
    if not search_term:
        return

    _log(f"Suchbegriff: '{search_term}'", xbmc.LOGDEBUG)
    results = search_streams(search_term)
    _log(f"Gefundene Ergebnisse: {len(results)}", xbmc.LOGDEBUG)

    if not results:
        xbmcgui.Dialog().ok("Suche", f"Keine Ergebnisse für '{search_term}'")
        return

    # Baue URL für die Suchergebnisse
    search_url = f"{BASE_URL}?action=search_results&term={urllib.parse.quote_plus(search_term)}"
    _log(f"Wechsle zu: {search_url}", xbmc.LOGDEBUG)
    xbmc.executebuiltin(f"Container.Update({search_url})")


def show_search_results_page():
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    term = params.get("term", "")
    results = search_streams(term)
    _log(f"search_results_page: {len(results)} Ergebnisse für '{term}'", xbmc.LOGINFO)

    if not results:
        xbmcgui.Dialog().ok("Suche", "Keine Ergebnisse gefunden")
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return

    xbmcplugin.setContent(ADDON_HANDLE, "music")

    # Header
    header = xbmcgui.ListItem(label=f"[COLOR deepskyblue][B]=== {len(results)} Ergebnisse für '{term}' ===[/B][/COLOR]")
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url="", listitem=header, isFolder=False)

    for domain, stream in sorted(results, key=lambda x: x[0]):
        name = stream.get("name", "Unknown")
        url = stream.get("url", "")
        li = xbmcgui.ListItem(label=f"{name} [COLOR gray]({domain})[/COLOR]")
        li.setProperty("IsPlayable", "true")
        li.setProperty("resolvetype", "direct")
        icon_path = xbmcvfs.translatePath("special://home/addons/plugin.audio.sKullsRadioSuite/resources/media/favorite.png")
        li.setArt({"icon": icon_path, "thumb": icon_path})

        play_url = f"{BASE_URL}?action=play_stream&domain={urllib.parse.quote_plus(domain)}&name={urllib.parse.quote_plus(name)}&url={urllib.parse.quote_plus(url)}"
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=play_url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def open_settings():
    # Öffnet Einstellungen und setzt den About-Tab als Standard
    ADDON.openSettings()
    xbmc.executebuiltin("SetFocus(9000)")  # Fokus auf die Einstellungen


def create_backup():
    backup_mgr = BackupManager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{ADDON.getSetting('backup_prefix')}{timestamp}.zip"
    backup_path = backup_mgr.get_backup_path(filename)

    # Backup-Logik hier
    zip_file(backup_path, source_files)

    # Aufräumen
    backup_mgr.cleanup_old_backups()
    xbmcgui.Dialog().notification("Backup erstellt", f"Gespeichert in:\n{backup_path}")


def check_update():
    try:
        latest_ver = get_latest_version()  # Ihre Update-Logik hier
        if latest_ver > ADDON.getAddonInfo("version"):
            xbmcgui.Dialog().ok(
                f"{ADDON_NAME} Update", f"Version {latest_ver} verfügbar!"
            )
        else:
            xbmcgui.Dialog().notification(
                ADDON_NAME, "Kein Update verfügbar", xbmcgui.NOTIFICATION_INFO
            )
    except Exception as e:
        xbmcgui.Dialog().notification(
            ADDON_NAME, "Update-Check fehlgeschlagen", xbmcgui.NOTIFICATION_ERROR
        )


def show_changelog():
    changelog = """
    [B][COLOR gold]Version 3.1.1[/COLOR][/B]
    • Neuer About-Tab
    • Verbesserte Cloud-Sync
    • Bugfixes im Backup-System
    
    [B]3.1.0[/B] - Phoenix Update:
    • Komplett neue UI
    • AES-256 Verschlüsselung
    """
    xbmcgui.Dialog().textviewer(f"{ADDON_NAME} - Changelog", changelog)


# --- Main-Menü & Router ---
def main_menu(streams):
    _log("Erstelle Hauptmenü.", xbmc.LOGINFO)
    feature_settings = get_global_feature_settings()

    # Header
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url="", listitem=xbmcgui.ListItem(label="==================="), isFolder=False)
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url="", listitem=xbmcgui.ListItem(label="[B][COLOR gold]sKulls Radio Suite[/COLOR][/B]"), isFolder=False)
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url="", listitem=xbmcgui.ListItem(label="==================="), isFolder=False)

    # Suche - Blau
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=show_search_dialog",
        listitem=xbmcgui.ListItem(label="[COLOR deepskyblue]🔍 Suche[/COLOR]"),
        isFolder=False,
    )

    # Filter/Sortierung - Cyan
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=show_filter_menu",
        listitem=xbmcgui.ListItem(label="[COLOR cyan]⚙ Filter / Sortierung[/COLOR]"),
        isFolder=True,
    )

    # Favoriten - Gold
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=show_favorites",
        listitem=xbmcgui.ListItem(label="[COLOR gold]★ Favoriten[/COLOR]"),
        isFolder=True,
    )

    # Erweiterte History - Orange
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=show_enhanced_history",
        listitem=xbmcgui.ListItem(label="[COLOR orange]📜 Verlauf[/COLOR]"),
        isFolder=True,
    )

    # Stream hinzufügen - Lime
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=add_stream",
        listitem=xbmcgui.ListItem(label="[COLOR lime]➕ Stream hinzufügen[/COLOR]"),
        isFolder=False,
    )

    # Playlist importieren - Violet
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=import_playlist",
        listitem=xbmcgui.ListItem(label="[COLOR violet]📀 Playlist importieren[/COLOR]"),
        isFolder=False,
    )

    # Streams von URL laden - Cyan
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=f"{BASE_URL}?action=update_streams_url",
        listitem=xbmcgui.ListItem(label="[COLOR cyan]🌐 Streams von URL laden[/COLOR]"),
        isFolder=False,
    )

    # Separator
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url="", listitem=xbmcgui.ListItem(label="[COLOR red][B]===== TOOLS =====[/B][/COLOR]"), isFolder=False)
    specials = [
        # Stream Features - Rot
        ("[COLOR red]❤️ Stream Health-Check[/COLOR]", "health_check", os.path.join(MEDIA_ICON_PATH, "health.png")),
        ("[COLOR grey]⚠ Fehlende Icons[/COLOR]", "missing_icons", os.path.join(MEDIA_ICON_PATH, "imagewarn.png")),
        # Backup - Blau
        ("[COLOR deepskyblue]💾 ZIP Backup[/COLOR]", "zip_backup", os.path.join(MEDIA_ICON_PATH, "zip.png")),
        ("[COLOR deepskyblue]📁 Backup-Galerie[/COLOR]", "backup_gallery", os.path.join(MEDIA_ICON_PATH, "zip.png")),
        ("[COLOR deepskyblue]🏷 Backups filtern[/COLOR]", "backup_tag_filter", os.path.join(MEDIA_ICON_PATH, "filter.png")),
        # Snapshot - Gold
        ("[COLOR gold]⭐ VIP Snapshot[/COLOR]", "create_release_save", os.path.join(MEDIA_ICON_PATH, "star.png")),
        # Diagnose - Lila
        ("[COLOR violet]↩ Undo Restore[/COLOR]", "gui_undo_restore", os.path.join(MEDIA_ICON_PATH, "undo.png")),
        ("[COLOR violet]📋 JSON Diagnose[/COLOR]", "broken_json_diagnose", os.path.join(MEDIA_ICON_PATH, "log.png")),
        ("[COLOR violet]📦 ZIP Diagnose[/COLOR]", "broken_zip_diagnose", os.path.join(MEDIA_ICON_PATH, "zip.png")),
    ]

    # Add GitHub Features if enabled
    if feature_settings["enable_github_features"]:
        _log("GitHub-Features im Menü hinzugefügt.", xbmc.LOGDEBUG)
        specials.append(
            (
                "GitHub-Features (Platzhalter)",
                "github_features_menu",
                # Assuming you have a github.png icon
                os.path.join(MEDIA_ICON_PATH, "github.png"),
            )
        )

    # Add Cloud/Sync features if enabled
    if feature_settings["enable_cloud_features"]:
        _log("Cloud-Features im Menü hinzugefügt.", xbmc.LOGDEBUG)
        specials.extend(
            [
                ("--- Cloud & Sync ---", None, None),  # Separator
                (
                    "ZIP-Backup-Integritäts-Check (Hashvergleich)",
                    "zip_hash_check",
                    os.path.join(MEDIA_ICON_PATH, "hash.png"),
                ),
                (
                    "HASH-Übersicht aller lokalen ZIP-Backups",  # Still shows local hashes
                    "zip_hash_overview",
                    os.path.join(MEDIA_ICON_PATH, "hashlist.png"),
                ),
                (
                    "Cloud-Hash-Report für ZIP-Backups",
                    "cloud_zip_hash_report",
                    os.path.join(MEDIA_ICON_PATH, "cloudhash.png"),
                ),
                (
                    "SYNC & Reparatur-Assistent für Backups",
                    "zip_sync_repair",
                    os.path.join(MEDIA_ICON_PATH, "sync.png"),
                ),
                (
                    "SYNC/Reparatur-Protokoll anzeigen",
                    "show_sync_protocol",
                    os.path.join(MEDIA_ICON_PATH, "log.png"),
                ),
                (
                    "Sync-Intervall festlegen",
                    "set_sync_interval_menu",
                    os.path.join(MEDIA_ICON_PATH, "settings.png"),
                ),
                (
                    "Backup verschlüsselt in Cloud hochladen",
                    "backup_cloud_upload_enc",
                    os.path.join(MEDIA_ICON_PATH, "lock.png"),
                ),
                (
                    "Backup verschlüsselt aus Cloud holen",
                    "backup_cloud_download_enc",
                    os.path.join(MEDIA_ICON_PATH, "unlock.png"),
                ),
                (
                    "Backup-Diff anzeigen (ZIP vs. lokal)",
                    "zip_diff_preview",
                    os.path.join(MEDIA_ICON_PATH, "compare.png"),
                ),
                (
                    "Cloud-Backups durchsuchen und holen",
                    "cloud_backup_browser",
                    os.path.join(MEDIA_ICON_PATH, "cloud.png"),
                ),
            ]
        )

    specials.extend(
        [
            # Statistik/UI-Komfort (immer verfügbar)
            ("--- Statistik ---", None, None),  # Separator
            ("[COLOR orange]📊 Stream-Statistik[/COLOR]", "streamstats", os.path.join(MEDIA_ICON_PATH, "stats.png")),
            ("[COLOR cyan]🆕 Zuletzt hinzugefügt[/COLOR]", "recentchanged", os.path.join(MEDIA_ICON_PATH, "update.png")),
        ]
    )

    for label, action, icon in specials:
        if action is None:  # This is a separator
            li = xbmcgui.ListItem(label=label)
            xbmcplugin.addDirectoryItem(
                handle=ADDON_HANDLE, url="", listitem=li, isFolder=False
            )
            continue

        menu_url = f"{BASE_URL}?action={action}"
        li = xbmcgui.ListItem(label=label)
        if icon:
            icon_path = xbmcvfs.translatePath(icon) if icon.startswith("special://") else icon
            li.setArt({"icon": icon_path, "thumb": icon_path})
        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE, url=menu_url, listitem=li, isFolder=True
        )

    sep_li = xbmcgui.ListItem(label="[COLOR grey]────────────[/COLOR]")
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE, url="", listitem=sep_li, isFolder=False
    )

    streams_data = load_json(STREAMS_JSON, {})
    # Only show stream categories if there are any streams
    if streams_data:
        for domain in sorted(streams_data.keys()):
            url = f"{BASE_URL}?action=list_streams&domain={urllib.parse.quote_plus(domain)}"
            li = xbmcgui.ListItem(label=domain)

            # Bild für die Kategorie (Domain) im Hauptmenü zuweisen
            category_icon_path = None
            normalized_domain_name = _normalize_filename(domain)
            if normalized_domain_name:
                potential_path = os.path.join(
                    IMAGES_CATEGORIES_DIR, f"{normalized_domain_name}.png"
                )
                if os.path.exists(potential_path):
                    category_icon_path = potential_path
                    _log(
                        f"Kategorie-Icon '{domain}' gefunden: {category_icon_path}",
                        xbmc.LOGDEBUG,
                    )
                else:
                    _log(
                        f"Kategorie-Icon für Domain '{domain}' nicht gefunden: {potential_path}",
                        xbmc.LOGDEBUG,
                    )

            if category_icon_path:
                li.setArt({"icon": category_icon_path, "thumb": category_icon_path})
            else:
                _log(
                    f"Kein spezifisches Icon für Domain '{domain}' gefunden. Verwende Standard oder Skin-Fallback.",
                    xbmc.LOGDEBUG,
                )

            xbmcplugin.addDirectoryItem(
                handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True
            )
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    _log("Hauptmenü erfolgreich geladen.", xbmc.LOGINFO)


def router(paramstring):
    _log(f"Router aufgerufen mit Parametern: {paramstring}", xbmc.LOGDEBUG)
    # Load streams for main menu if needed
    streams = load_json(STREAMS_JSON, {})
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get("action")
    _log(f"Aktion: {action}", xbmc.LOGDEBUG)

    # --- Stream Related Actions ---
    if action == "play_stream":
        domain = urllib.parse.unquote_plus(params.get("domain", ""))
        name = urllib.parse.unquote_plus(params.get("name", ""))
        url = urllib.parse.unquote_plus(params.get("url", ""))
        play_stream(domain, name, url)
        return  # Important: Don't call endOfDirectory after playing

    elif action == "list_streams" and "domain" in params:
        list_streams(urllib.parse.unquote_plus(params["domain"]))

    # --- Settings Actions ---
    elif action == "set_sync_interval_menu":
        set_sync_interval_menu()
    elif action == "search_menu":
        search_menu()

    # Neue Cases in der router() Funktion:
    elif action == "show_enhanced_history":
        show_enhanced_history()

    elif action == "share_stream":
        share_stream(urllib.parse.unquote_plus(params["url"]))

    elif action == "show_search_dialog":
        show_search_dialog()
    elif action == "search_results":
        show_search_results_page()

    # --- Stream Management ---
    elif action == "add_stream":
        add_stream_manually()
    elif action == "import_playlist":
        import_playlist()
    elif action == "update_streams_url":
        update_streams_from_url()
    elif action == "set_custom_image":
        set_custom_image()
    elif action == "set_domain_image":
        set_domain_image()

    # --- Backup & Restore Actions ---
    elif action == "zip_backup":
        zip_backup()
    elif (
        action == "zip_restore_file"
    ):  # Specific action for restoring a selected ZIP file
        zip_restore_file()
    elif (
        action == "bak_restore_file"
    ):  # Specific action for restoring a selected .bak_ file
        bak_restore_file()
    elif action == "backup_gallery":
        backup_gallery()
    elif action == "backup_tag_edit":
        backup_tag_edit()
    elif action == "backup_tag_filter":
        backup_tag_filter()
    elif action == "create_release_save":  # Renamed action from 'release_save'
        create_release_save("Manuell durch User")
    elif action == "backup_delete":  # Called from context menus
        backup_delete()
    elif action == "play_backup":
        backup_gallery()

    # --- Diagnosis & Repair Actions ---
    elif action == "gui_undo_restore":
        gui_undo_restore()
    elif action == "broken_json_diagnose":
        broken_json_diagnose()
    elif action == "broken_zip_diagnose":
        broken_zip_diagnose()

    # --- Hash & Integrity Checks ---
    elif action == "zip_hash_check":
        zip_hash_check()
    elif action == "zip_hash_overview":
        zip_hash_overview()

    # --- Cloud & Sync Actions ---
    elif action == "cloud_zip_hash_report":
        cloud_zip_hash_report()
    elif action == "zip_sync_repair":
        zip_sync_repair()
    elif action == "show_sync_protocol":
        show_sync_protocol()
    elif action == "backup_cloud_upload_enc":
        backup_cloud_upload_enc()
    elif action == "backup_cloud_download_enc":
        backup_cloud_download_enc()

    # --- New/Implemented Features ---
    elif action == "missing_icons":
        missing_icons()
    elif action == "zip_diff_preview":
        zip_diff_preview()
    elif action == "cloud_backup_browser":
        cloud_backup_browser()
    elif action == "streamstats":
        streamstats()
    elif action == "recentchanged":
        recentchanged()
    elif action == "health_check":  # This was missing from the router previously too!
        health_check()
    elif action == "show_filter_menu":
        filter_type = show_filter_menu()
        if filter_type:
            streams = load_json(STREAMS_JSON, {})
            filtered = filter_streams(streams, filter_type)
            # Zeige gefilterte Streams an...

    elif action == "show_favorites":
        show_favorites()

    elif action == "toggle_favorite":
        stream_data = {
            "name": urllib.parse.unquote_plus(params["name"]),
            "url": urllib.parse.unquote_plus(params["url"]),
            "domain": urllib.parse.unquote_plus(params["domain"]),
        }
        added = toggle_favorite(stream_data)
        notification = (
            "Zur Favoriten hinzugefügt" if added else "Aus Favoriten entfernt"
        )
        xbmcgui.Dialog().notification("Favoriten", notification)

    # elif action == "github_features_menu":  # New GitHub placeholder action
    # Fügen Sie diese Cases zur router() Funktion hinzu:

    # --- Default: Show Main Menu ---
    else:
        main_menu(streams)


if __name__ == "__main__":
    _log("Addon-Start (main-Block).", xbmc.LOGDEBUG)
    try:
        router(sys.argv[2][1:])
    except Exception as e:
        # Hier ist der entscheidende Punkt. Wenn `e` ein KeyError ist, zeigt str(e) nur den Schlüssel an.
        # Wenn es andere Exceptions gibt, möchten wir auch den Typ und Details sehen.
        error_type = type(e).__name__
        error_content = str(e)
        xbmc.log(
            f"[sKullsRadioSuite] Addon fatal error - Type: {error_type}, Content: {error_content}. Full Traceback:",
            xbmc.LOGFATAL,
        )
        # Ausgabe des vollständigen Tracebacks
        xbmc.log(traceback.format_exc(), xbmc.LOGFATAL)
        xbmcgui.Dialog().notification(
            "Kritischer Fehler",
            f"Es ist ein schwerwiegender Addon-Fehler aufgetreten: {error_content}. Bitte siehe das Kodi-Log für Details.",
            xbmcgui.NOTIFICATION_ERROR,
        )
