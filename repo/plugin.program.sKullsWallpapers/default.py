# -*- coding: utf-8 -*-
import sys
import os
import time
import urllib.parse as up
import urllib.request as urlreq
import re

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

# sKulls source module
try:
    import resources.lib.skulls_source as skulls_source
except Exception:
    skulls_source = None

# Robust import for scraper
try:
    from resources.lib import wc_scraper as wc
except Exception:
    _ADDON = xbmcaddon.Addon()
    _BASE = xbmcvfs.translatePath(_ADDON.getAddonInfo("path"))
    _LIBDIR = os.path.join(_BASE, "resources", "lib")
    if _LIBDIR not in sys.path:
        sys.path.insert(0, _LIBDIR)
    import wc_scraper as wc

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id") or "plugin.program.sKullsWallpapers"
HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else -1
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else "plugin.program.sKullsWallpapers"
BASE_SITE = "https://wallpaperscraft.com/"

# Profile dirs (for cached category thumbs)
PROFILE_DIR = xbmcvfs.translatePath(ADDON.getAddonInfo("profile")) or xbmcvfs.translatePath(
    f"special://profile/addon_data/{ADDON_ID}"
)
try:
    if not xbmcvfs.exists(PROFILE_DIR):
        xbmcvfs.mkdirs(PROFILE_DIR)
except Exception:
    pass
CAT_THUMB_DIR = os.path.join(PROFILE_DIR, "cat_thumbs")
try:
    if not xbmcvfs.exists(CAT_THUMB_DIR):
        xbmcvfs.mkdirs(CAT_THUMB_DIR)
except Exception:
    pass

# Cache-Dir für Offline-Speicherung
CACHE_DIR = os.path.join(PROFILE_DIR, "cache")
try:
    if not xbmcvfs.exists(CACHE_DIR):
        xbmcvfs.mkdirs(CACHE_DIR)
except Exception:
    pass

import json
import threading
import queue

# ---------- Cache-System ----------
CACHE_FILE = os.path.join(CACHE_DIR, "wallpaper_cache.json")
CACHE_MAX_AGE = 24 * 3600  # 24 Stunden

def _load_cache():
    try:
        if xbmcvfs.exists(CACHE_FILE):
            f = xbmcvfs.File(CACHE_FILE, "r")
            data = f.read()
            f.close()
            return json.loads(data)
    except Exception:
        pass
    return {}

def _save_cache(data):
    try:
        f = xbmcvfs.File(CACHE_FILE, "w")
        f.write(json.dumps(data, indent=2))
        f.close()
    except Exception:
        pass

def _get_cache(kind, slug, page):
    cache = _load_cache()
    key = f"{kind}:{slug}:{page}"
    if key in cache:
        entry = cache[key]
        if time.time() - entry.get("ts", 0) < CACHE_MAX_AGE:
            return entry.get("data")
    return None

def _set_cache(kind, slug, page, data):
    cache = _load_cache()
    key = f"{kind}:{slug}:{page}"
    cache[key] = {"data": data, "ts": time.time()}
    _save_cache(cache)

def _clear_cache():
    try:
        if xbmcvfs.exists(CACHE_FILE):
            xbmcvfs.delete(CACHE_FILE)
    except Exception:
        pass

# ---------- Paralleles Laden ----------
def _parallel_load_thumbs(items, max_workers=4):
    results = {}
    q = queue.Queue()
    for i, it in enumerate(items):
        q.put((i, it))
    lock = threading.Lock()
    def worker():
        while True:
            try:
                idx, it = q.get(timeout=0.1)
            except queue.Empty:
                return
            thumb = it.get("thumb", "")
            if thumb:
                try:
                    req = urlreq.Request(thumb, headers={"User-Agent": "Mozilla/5.0"})
                    with urlreq.urlopen(req, timeout=5) as r:
                        data = r.read()
                        with lock:
                            results[idx] = data
                except Exception:
                    pass
            q.task_done()
    threads = []
    for _ in range(min(max_workers, len(items))):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return results

# ---------- Backup-Quelle ----------
def _is_source_available(source_name):
    if source_name == "wallpaperscraft":
        try:
            req = urlreq.Request(BASE_SITE, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
            with urlreq.urlopen(req, timeout=5) as r:
                return r.getcode() < 400
        except Exception:
            return False
    return True

# ---------- Favoriten ----------
FAVORITES_FILE = xbmcvfs.translatePath(os.path.join(PROFILE_DIR, "favorites.json"))

def _load_favorites():
    try:
        if xbmcvfs.exists(FAVORITES_FILE):
            f = xbmcvfs.File(FAVORITES_FILE, "r")
            data = f.read()
            f.close()
            return json.loads(data)
    except Exception:
        pass
    return []

def _save_favorites(favs):
    try:
        import os
        # Ensure directory exists
        fav_dir = os.path.dirname(FAVORITES_FILE)
        if not xbmcvfs.exists(fav_dir):
            xbmcvfs.mkdirs(fav_dir)
        # Write file
        f = xbmcvfs.File(FAVORITES_FILE, "w")
        f.write(json.dumps(favs))
        f.close()
        _log(f"Saved {len(favs)} favorites to {FAVORITES_FILE}")
    except Exception as e:
        _log(f"Save favorites error: {e}")

def _add_favorite(title, url, thumb):
    favs = _load_favorites()
    _log(f"Current favorites: {len(favs)}")
    for f in favs:
        if f.get("url") == url:
            _log("Duplicate favorite")
            return False
    favs.insert(0, {"title": title, "url": url, "thumb": thumb, "added": time.time()})
    _save_favorites(favs)
    _log("Favorite added successfully")
    return True

def _remove_favorite(url):
    favs = _load_favorites()
    favs = [f for f in favs if f.get("url") != url]
    _save_favorites(favs)

def _is_favorite(url):
    favs = _load_favorites()
    return any(f.get("url") == url for f in favs)

def _get_favorites():
    return _load_favorites()

# ---------- Wallpaper Set (ZIP-Download) ----------
SET_SELECT_FILE = xbmcvfs.translatePath(os.path.join(PROFILE_DIR, "set_selection.json"))

def _load_set_selection():
    try:
        if xbmcvfs.exists(SET_SELECT_FILE):
            f = xbmcvfs.File(SET_SELECT_FILE, "r")
            data = f.read()
            f.close()
            return json.loads(data)
    except Exception:
        pass
    return []

def _save_set_selection(items):
    try:
        import os
        set_dir = os.path.dirname(SET_SELECT_FILE)
        if not xbmcvfs.exists(set_dir):
            xbmcvfs.mkdirs(set_dir)
        f = xbmcvfs.File(SET_SELECT_FILE, "w")
        f.write(json.dumps(items))
        f.close()
    except Exception as e:
        _log(f"Save set error: {e}")

def _add_to_set(title, url, thumb):
    items = _load_set_selection()
    for i in items:
        if i.get("url") == url:
            return False
    items.append({"title": title, "url": url, "thumb": thumb})
    _save_set_selection(items)
    return True

def _remove_from_set(url):
    items = _load_set_selection()
    items = [i for i in items if i.get("url") != url]
    _save_set_selection(items)

def _clear_set():
    _save_set_selection([])

def _get_set_count():
    return len(_load_set_selection())

# ---------- Suchverlauf ----------
HISTORY_FILE = xbmcvfs.translatePath(os.path.join(PROFILE_DIR, "search_history.json"))
MAX_HISTORY = 10

def _load_history():
    try:
        if xbmcvfs.exists(HISTORY_FILE):
            f = xbmcvfs.File(HISTORY_FILE, "r")
            data = f.read()
            f.close()
            return json.loads(data)
    except Exception:
        pass
    return []

def _save_history(history):
    try:
        f = xbmcvfs.File(HISTORY_FILE, "w")
        f.write(json.dumps(history, indent=2))
        f.close()
    except Exception:
        pass

def _add_to_history(query):
    if not query:
        return
    history = _load_history()
    if query in history:
        history.remove(query)
    history.insert(0, query)
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]
    _save_history(history)

def _get_history():
    return _load_history()

def _clear_history():
    _save_history([])

# ---------- Resolution Filter ----------
RESOLUTION_FILTERS = {
    "0": "",      # All
    "1": "3840",  # 4K
    "2": "2560",  # 2K
    "3": "1920",  # FullHD
    "4": "1280",  # HD
}

def _get_resolution_filter():
    return _get("resolution_filter", "0")

def _apply_resolution_filter(items):
    """Filter wallpapers by resolution based on setting"""
    res_filter = _get_resolution_filter()
    min_width = RESOLUTION_FILTERS.get(res_filter, "")
    if not min_width:
        return items
    filtered = []
    for item in items:
        thumb = item.get("thumb", "")
        if min_width in thumb:
            filtered.append(item)
    return filtered

# ---------- Custom Sources ----------
def _load_custom_sources():
    """Load custom wallpaper sources from settings"""
    data = _get("custom_sources", "")
    if not data:
        return []
    try:
        import json
        sources = json.loads(data)
        return sources if isinstance(sources, list) else []
    except Exception:
        return []

def _save_custom_sources(sources):
    """Save custom wallpaper sources to settings"""
    try:
        import json
        ADDON.setSetting("custom_sources", json.dumps(sources))
    except Exception as e:
        _log(f"Failed to save custom sources: {e}")

def add_custom_source(params):
    """Add a new custom wallpaper source"""
    kb = xbmcgui.Dialog()
    name = kb.input("Custom Source Name", type=xbmcgui.INPUT_ALPHANUM)
    if not name:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    url = kb.input("Wallpaper Folder URL", type=xbmcgui.INPUT_ALPHANUM)
    if not url:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    if not url.startswith("http"):
        url = "https://" + url
    sources = _load_custom_sources()
    sources.append({"name": name, "url": url})
    _save_custom_sources(sources)
    xbmcgui.Dialog().notification("sKulls Wallpapers", f"Added: {name}", _media_icon("favorites"), 2000)
    xbmc.executebuiltin("Container.Refresh")

def manage_custom_sources(params):
    """Manage and delete custom wallpaper sources"""
    _log("manage_custom_sources called")
    sources = _load_custom_sources()
    _log(f"Loaded sources: {sources}")

    if not sources:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "No custom sources", _media_icon("favorites"), 2000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    xbmcplugin.setContent(HANDLE, "files")

    # Header
    li = xbmcgui.ListItem(label="Manage Custom Sources")
    li.setArt({"icon": _media_icon("categories"), "thumb": _media_icon("categories")})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    for i, src in enumerate(sources):
        name = src.get("name", "Unknown")
        url = src.get("url", "")
        _log(f"Source {i}: {name} - {url}")
        li = xbmcgui.ListItem(label=name)
        li.setArt({"icon": _media_icon("archive"), "thumb": _media_icon("archive")})
        cm = [(f"Delete", f'RunPlugin("{_url(mode="delete_custom_source", index=str(i))}")')]
        li.addContextMenuItems(cm, replaceItems=False)
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="browse_custom_source", url=url, name=name), li, isFolder=True)

    # Add button
    li = xbmcgui.ListItem(label="[COLOR deepskyblue]+ Add New Source[/COLOR]")
    li.setArt({"icon": _media_icon("search"), "thumb": _media_icon("search")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="add_custom_source"), li, isFolder=False)

    _log("Calling endOfDirectory")
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

def open_custom_url(params):
    """Open custom wallpaper source URL in browser"""
    url = params.get("url", "")
    name = params.get("name", "Custom Source")
    if url:
        xbmc.executebuiltin(f"RunPlugin({url})")
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def delete_custom_source(params):
    """Delete a custom wallpaper source"""
    try:
        idx = int(params.get("index", "-1"))
    except Exception:
        idx = -1
    sources = _load_custom_sources()
    if 0 <= idx < len(sources):
        name = sources[idx].get("name", "Unknown")
        del sources[idx]
        _save_custom_sources(sources)
        xbmcgui.Dialog().notification("sKulls Wallpapers", f"Deleted: {name}", _media_icon("favorites"), 2000)
    xbmc.executebuiltin("Container.Refresh")

def browse_custom_source(params):
    """Browse custom wallpaper source - try to find images"""
    url = params.get("url", "")
    name = params.get("name", "Custom Source")
    if not url:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    xbmcplugin.setContent(HANDLE, "images")
    _log(f"Browsing custom source: {name} - {url}")

    found = set()

    try:
        req = urlreq.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlreq.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            _log(f"Fetched {len(html)} bytes")
    except Exception as e:
        _log(f"Failed to fetch: {e}")
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Cannot load URL", _media_icon("favorites"), 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    # Debug: save first 2000 chars
    _log(f"HTML sample: {html[:500]}")

    # Internet Archive special handling
    if "archive.org" in url:
        _log("Processing archive.org URL...")

        base_url = url.rstrip("/")

        # First try to find image files directly
        for m in re.finditer(r'href="([^"#]+)"', html):
            link = m.group(1)
            if link.startswith("#") or link.startswith("?") or link == "../":
                continue
            # Check for image files
            if any(link.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
                if link.startswith("http"):
                    found.add(link)
                elif link.startswith("/"):
                    found.add("https://archive.org" + link)
                else:
                    found.add(base_url + "/" + link.lstrip("/"))

        # If no images found, try to find subfolders
        if not found:
            _log("No images found, looking for subfolders...")
            for m in re.finditer(r'href="([^"/]+/)"', html):
                folder = m.group(1)
                if folder and folder not in ["../", "../"]:
                    folder_url = base_url + "/" + folder
                    li = xbmcgui.ListItem(label=f"[COLOR cyan]📁 {folder}[/COLOR]")
                    li.setArt({"icon": _media_icon("archive"), "thumb": _media_icon("archive")})
                    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="browse_custom_source", url=folder_url, name=name + "/" + folder), li, isFolder=True)
            if found:
                _log(f"Archive.org: found {len(found)} images directly")
            else:
                xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
                return
    else:
        # Regular website patterns
        patterns = [
            r'src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',
            r'src=\'([^\']+\.(?:jpg|jpeg|png|gif|webp))\'',
            r'href="([^"]+\.(?:jpg|jpeg|png))"',
            r'data-src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',
        ]
        for pat in patterns:
            for m in re.finditer(pat, html, re.I):
                img_url = m.group(1)
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    parsed = up.urlparse(url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                if "://" in img_url and img_url not in found:
                    found.add(img_url)
        _log(f"Regular site: found {len(found)} images")

    _log(f"Found {len(found)} images")

    if not found:
        li = xbmcgui.ListItem(label="[Open in browser]")
        li.setArt({"icon": _media_icon("archive"), "thumb": _media_icon("archive")})
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)
    else:
        for img_url in list(found)[:50]:
            fname = img_url.split("/")[-1][:50] or "image"
            li = xbmcgui.ListItem(label=fname)
            li.setArt({"thumb": img_url, "icon": img_url})
            xbmcplugin.addDirectoryItem(HANDLE, _url(mode="custom_wallpaper", img=img_url, title=fname), li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def custom_wallpaper(params):
    """Show wallpaper options for custom source images"""
    img_url = params.get("img", "")
    title = params.get("title", "Wallpaper")

    if not img_url:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    thumb = img_url
    xbmcplugin.setContent(HANDLE, "images")

    # Preview
    pli = xbmcgui.ListItem(label="[COLOR deepskyblue]PREVIEW[/COLOR]")
    pli.setArt({"thumb": thumb, "icon": _media_icon("preview")})
    purl = _url(mode="preview_image", img=img_url, title=title)
    xbmcplugin.addDirectoryItem(HANDLE, purl, pli, isFolder=False)

    # Add to Favorites
    fav_url = _url(mode="add_favorite", title=title, url=img_url, thumb=thumb)
    fav_li = xbmcgui.ListItem(label="[COLOR gold]ADD TO FAVORITES[/COLOR]")
    fav_li.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
    xbmcplugin.addDirectoryItem(HANDLE, fav_url, fav_li, isFolder=False)

    # Add to Set
    set_url = _url(mode="add_to_set", title=title, url=img_url, thumb=thumb)
    set_li = xbmcgui.ListItem(label="[COLOR violet]ADD TO SET[/COLOR]")
    set_li.setArt({"icon": _media_icon("set"), "thumb": _media_icon("set")})
    xbmcplugin.addDirectoryItem(HANDLE, set_url, set_li, isFolder=False)

    # Download
    dl_li = xbmcgui.ListItem(label="[COLOR lime]DOWNLOAD[/COLOR]")
    dl_li.setArt({"thumb": thumb, "icon": _media_icon("download")})
    dl_url = _url(mode="download_image", img=img_url, title=title, label="custom", ref="custom")
    dl_li.setProperty("IsPlayable", "false")
    xbmcplugin.addDirectoryItem(HANDLE, dl_url, dl_li, isFolder=False)

    # Separator
    li = xbmcgui.ListItem(label=f"--- {title} ---")
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # Show actual image
    li = xbmcgui.ListItem(label=f"[COLOR cyan]View Image[/COLOR]")
    li.setArt({"thumb": thumb, "icon": thumb, "fanart": thumb})
    xbmcplugin.addDirectoryItem(HANDLE, img_url, li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# ---------- Mehrsprachigkeit ----------
try:
    ADDON_LANG = ADDON.getLocalizedString
except Exception:
    def ADDON_LANG(id):
        return str(id)

def _tr(msgid):
    translations = {
        "30000": "Search History",
        "30001": "Clear History",
        "30002": "No recent searches",
        "30003": "Preview",
        "30004": "Download",
        "30005": "Downloading...",
        "30006": "Done",
        "30007": "Cancel",
    }
    return translations.get(str(msgid), msgid)

def _log(msg):
    try:
        xbmc.log(f"[{ADDON_ID}] {msg}", xbmc.LOGINFO)
    except Exception:
        print(f"[{ADDON_ID}] {msg}")

def _url(**kwargs):
    return BASE_URL + "?" + up.urlencode(kwargs)

def _get(setting, default=""):
    try:
        v = ADDON.getSetting(setting)
        return v if v not in ("", None) else default
    except Exception:
        return default

def _get_bool(setting, default=False):
    return (_get(setting, "true" if default else "false").lower() in ("true","1","yes","on"))

def _sanitize_name(name):
    bad = '<>:"/\\|?*'
    out = "".join(("_" if c in bad else c) for c in name).strip()
    return out[:120] or "wallpaper"

def _addon_path(*parts):
    base = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))
    return os.path.join(base, *parts)

def _http_get_small(url, timeout=5, max_bytes=400 * 1024):
    try:
        req = urlreq.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlreq.urlopen(req, timeout=timeout) as r:
            chunks, total = [], 0
            while True:
                buf = r.read(min(64 * 1024, max_bytes - total))
                if not buf:
                    break
                chunks.append(buf)
                total += len(buf)
                if total >= max_bytes:
                    break
            return b"".join(chunks)
    except Exception as e:
        _log(f"thumb fetch failed: {e}")
        return b""

def _cat_cache_path(slug):
    return os.path.join(CAT_THUMB_DIR, f"{slug}.jpg")

def _cat_local_art(slug):
    cat_dir = _addon_path("resources", "media", "categories")
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(cat_dir, slug + ext)
        if xbmcvfs.exists(p):
            return p
    aliases = {
        "black_and_white": ["black-and-white", "bw"],
        "tv-series": ["tv_series", "tvseries", "serials", "tv"],
        "hi-tech": ["technologies", "technology", "tech"],
        "sport": ["sports"],
    }
    for alt in aliases.get(slug, []):
        for ext in (".png", ".jpg", ".jpeg"):
            p = os.path.join(cat_dir, alt + ext)
            if xbmcvfs.exists(p):
                return p
    fallback = _addon_path("resources", "media", "catalog_default.png")
    return fallback if xbmcvfs.exists(fallback) else ""

def _cat_thumb(slug):
    cached = _cat_cache_path(slug)
    if xbmcvfs.exists(cached):
        return cached
    return _cat_local_art(slug)

def _get_download_dir():
    raw = (_get("download_path", "").strip()
           or "special://home/addons/resource.images.skinbackgrounds")
    try:
        if not xbmcvfs.exists(raw):
            xbmcvfs.mkdirs(raw)
    except Exception:
        pass
    dest_dir = xbmcvfs.translatePath(raw)
    try:
        if not xbmcvfs.exists(dest_dir):
            xbmcvfs.mkdirs(dest_dir)
    except Exception:
        pass
    return dest_dir



def _should_abort():
    try:
        import xbmc
        return xbmc.Monitor().abortRequested()
    except Exception:
        return False

def _category_entries():
    return [
        ("3D", "3d", "catalog"),
        ("Abstract", "abstract", "catalog"),
        ("Anime", "anime", "catalog"),
        ("City", "city", "catalog"),
        ("Dark", "dark", "catalog"),
        ("Flowers", "flowers", "catalog"),
        ("Minimalism", "minimalism", "catalog"),
        ("Motorcycles", "motorcycles", "catalog"),
        ("Other", "other", "catalog"),
        ("Space", "space", "catalog"),
        ("Textures", "textures", "catalog"),
        ("Vector", "vector", "catalog"),

        ("Animals", "animals", "catalog"),
        ("Art", "art", "catalog"),
        ("Black", "black", "catalog"),
        ("Black and White", "black_and_white", "catalog"),
        ("Cars", "cars", "catalog"),
        ("Fantasy", "fantasy", "catalog"),
        ("Food", "food", "catalog"),
        ("Holidays", "holidays", "catalog"),
        ("Macro", "macro", "catalog"),
        ("Music", "music", "catalog"),
        ("Nature", "nature", "catalog"),
        ("Sport", "sport", "catalog"),
        ("Technologies", "hi-tech", "catalog"),
        ("TV Series", "tv-series", "tag"),
        ("Words", "words", "catalog"),
    ]

# -------------------------------
# Root (reports: files) + Search + My Wallpapers
# -------------------------------
def _media_icon(name):
    """Lade Icon aus media-Ordner oder fallback"""
    # Mapping für Icons mit anderen Dateinamen
    name_map = {
        "mywallpaper": "my-wallpaper",
        "set": "wallpaper-set",
        "history": "search-history",
    }
    icon_name = name_map.get(name, name)
    icon_path = os.path.join(_addon_path("resources", "media", f"{icon_name}.png"))
    if xbmcvfs.exists(icon_path):
        return icon_path
    # Fallbacks
    fallback = {
        "search": "DefaultAddonsSearch.png",
        "random": "DefaultMovie.png",
        "favorites": "DefaultAddonsInfo.png",
        "set": "DefaultFolder.png",
        "download": "DefaultDownload.png",
        "preview": "DefaultPicture.png",
        "slideshow": "Default slideshow.png",
        "archive": "DefaultFolder.png",
        "mywallpaper": "DefaultFolder.png",
        "categories": "DefaultFolder.png",
        "wallpaper": "DefaultPicture.png",
        "history": "DefaultAddonsSearch.png",
    }
    return fallback.get(name, "DefaultAddonsInfo.png")

def show_root():
    xbmcplugin.setContent(HANDLE, "files")

    # Header - 3 Zeilen
    icon_path = _addon_path("icon.png")
    fanart_path = _addon_path("fanart.jpg")
    li = xbmcgui.ListItem(label="[B]========================[/B]")
    li.setArt({"icon": icon_path, "thumb": icon_path, "fanart": fanart_path})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    li = xbmcgui.ListItem(label="[B]sKulls Fusion Wallpapers[/B]")
    li.setArt({"icon": icon_path, "thumb": icon_path, "fanart": fanart_path})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    li = xbmcgui.ListItem(label="[B]========================[/B]")
    li.setArt({"icon": icon_path, "thumb": icon_path, "fanart": fanart_path})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # Search - Blau
    li = xbmcgui.ListItem(label="[COLOR deepskyblue]Search Wallpapers[/COLOR]")
    li.setArt({"icon": _media_icon("search"), "thumb": _media_icon("search")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="search_prompt"), li, isFolder=False)

    # Search History
    history = _get_history()
    if history:
        hi = xbmcgui.ListItem(label="[COLOR grey]Search History[/COLOR]")
        hi.setArt({"icon": _media_icon("history"), "thumb": _media_icon("history")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="show_history"), hi, isFolder=True)

    # Random Wallpaper - Orange
    ri = xbmcgui.ListItem(label="[COLOR orange]Random Wallpaper[/COLOR]")
    ri.setArt({"icon": _media_icon("random"), "thumb": _media_icon("random")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="random_wallpaper"), ri, isFolder=True)

    # Favorites - Gold/Gelb
    favs = _get_favorites()
    fav_count = len(favs)
    fi = xbmcgui.ListItem(label=f"[COLOR gold]My Favorites ({fav_count})[/COLOR]")
    fi.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="show_favorites"), fi, isFolder=True)

    # Wallpaper Set - Lila
    set_count = _get_set_count()
    si = xbmcgui.ListItem(label=f"[COLOR violet]Wallpaper Set ({set_count})[/COLOR]")
    si.setArt({"icon": _media_icon("set"), "thumb": _media_icon("set")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="show_set"), si, isFolder=True)

    # Separator
    li = xbmcgui.ListItem(label="-------------------")
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # My Wallpapers - Grün
    mi = xbmcgui.ListItem(label="[COLOR lime]My Wallpapers[/COLOR]")
    mi.setArt({"icon": _media_icon("mywallpaper"), "thumb": _media_icon("mywallpaper")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="my_wallpapers", dir=_get_download_dir()), mi, isFolder=True)

    # sKulls Archive - Rot
    di = xbmcgui.ListItem(label="[COLOR red]sKulls Archive[/COLOR]")
    di.setArt({"icon": _media_icon("archive"), "thumb": _media_icon("archive")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="skulls_root"), di, isFolder=True)

    # Custom Sources - Lila
    custom_sources = _load_custom_sources()
    for src in custom_sources:
        name = src.get("name", "Unknown")
        url = src.get("url", "")
        li = xbmcgui.ListItem(label=f"[COLOR violet]{name}[/COLOR]")
        li.setArt({"icon": _media_icon("archive"), "thumb": _media_icon("archive")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="browse_custom_source", url=url, name=name), li, isFolder=True)

    # Manage Custom Sources
    li = xbmcgui.ListItem(label="[COLOR grey]Manage Custom Sources[/COLOR]")
    li.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="manage_custom_sources"), li, isFolder=True)

    # Separator
    li = xbmcgui.ListItem(label="-------------------")
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # Categories Header - Cyan
    li = xbmcgui.ListItem(label="[COLOR cyan]Categories[/COLOR]")
    li.setArt({"icon": _media_icon("categories"), "thumb": _media_icon("categories")})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # Categories (use cached/local art now; warm in background after opening)
    entries = _category_entries()
    for title, slug, kind in entries:
        li = xbmcgui.ListItem(label=title)
        thumb = _cat_thumb(slug)
        if thumb:
            li.setArt({"thumb": thumb, "icon": thumb, "poster": thumb, "fanart": thumb})
        url = _url(mode="category", kind=kind, slug=slug, page="1", title=title)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

    # Schedule background warming (only if dynamic thumbs enabled)
    if not _get_bool("use_static_thumbs", False):
        # Cancel previous runs and schedule a new one 1s after open
        xbmc.executebuiltin('CancelAlarm(wcthumbs,true)')
        xbmc.executebuiltin(f'AlarmClock(wcthumbs,RunPlugin("{_url(mode="warm_thumbs", idx="0")}"),00:00:01,true)')

def search_prompt(_params):
    """Prompt for a query, then open the Search results (page 1)."""
    try:
        dlg = xbmcgui.Dialog()
        query = dlg.input("Search Wallpapers", type=xbmcgui.INPUT_ALPHANUM)
    except Exception:
        query = ""
    if not query:
        try:
            xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        except Exception:
            pass
        return
    _add_to_history(query)
    # Navigate to search results page 1, replacing the current view
    try:
        xbmc.executebuiltin(f'Container.Update("{_url(mode="search", q=query, page="1")}")')
    except Exception:
        pass
    try:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
    except Exception:
        pass
    return

def show_history(_params):
    """Zeige Suchverlauf."""
    xbmcplugin.setContent(HANDLE, "files")
    history = _get_history()
    if not history:
        li = xbmcgui.ListItem(label=_tr("30002"))
        xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)
    else:
        for q in history:
            li = xbmcgui.ListItem(label=q)
            li.setArt({"icon": _media_icon("search"), "thumb": _media_icon("search")})
            url = _url(mode="search", q=q, page="1")
            xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)
        # Clear history button
        cli = xbmcgui.ListItem(label=f"[{_tr('30001')}]")
        cli.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="clear_history"), cli, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def clear_history(_params):
    """Lösche Suchverlauf."""
    _clear_history()
    try:
        xbmcgui.Dialog().notification("sKulls Wallpapers", _tr("30001"), "DefaultAddonsInfo.png", 2000)
    except Exception:
        pass
    xbmc.executebuiltin("Container.Refresh")



def warm_thumbs(params):
    """No-op stub to handle any leftover scheduled calls safely."""
    try:
        xbmc.executebuiltin('CancelAlarm(wcthumbs,true)')
    except Exception:
        pass
    try:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
    except Exception:
        pass
    return



def list_search_results(params):
    query = params.get("q", "")
    page = int(params.get("page", "1"))
    xbmcplugin.setContent(HANDLE, "movies")
    _log(f"Search '{query}' page={page}")

    if _should_abort():
        return
    # Retry the network search a few times before declaring "No results".
    # This avoids a premature notification while the site responds slowly.
    items, has_next = [], False
    max_wait_s = 10  # total extra wait budget (kept modest to avoid blocking UI too long)
    start = time.time()
    attempts = 0

    # Show a busy dialog while we give the search a fair chance to return.
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
    except Exception:
        pass

    while not items:
        attempts += 1
        try:
            items, has_next = wc.list_search(query, page)
        except Exception as e:
            _log(f"list_search error (attempt {attempts}): {e}")
            items, has_next = [], False

        # If we got items or we've waited long enough, break.
        if items or (time.time() - start) >= max_wait_s or attempts >= 2:
            break

        # Brief pause before a quick re-try in case the first attempt raced with a slow site.
        xbmc.sleep(800)

    # Close busy dialog if we opened it
    try:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    except Exception:
        pass

    if not items:
        try:
            xbmcgui.Dialog().notification("sKulls Wallpapers", f"No results for '{query}'", "DefaultAddonsInfo.png", 3000)
        except Exception:
            pass

    # Apply resolution filter
    items = _apply_resolution_filter(items)

    if not items:
        try:
            xbmcgui.Dialog().notification("sKulls Wallpapers", "No wallpapers match resolution filter", "DefaultAddonsInfo.png", 3000)
        except Exception:
            pass

    for it in items:
        lbl = it.get("title") or "Wallpaper"
        li = xbmcgui.ListItem(label=lbl)
        th = it.get("thumb")
        if th:
            li.setArt({"thumb": th, "icon": th, "poster": th, "fanart": th})
        _set_video_title(li, lbl)
        url = _url(mode="wallpaper", page_url=it.get("href",""), title=lbl)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    if has_next:
        nli = xbmcgui.ListItem(label=f"Next (page {page+1})")
        _set_video_title(nli, f"{query} — page {page+1}")
        nurl = _url(mode="search", q=query, page=str(page+1))
        xbmcplugin.addDirectoryItem(HANDLE, nurl, nli, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, updateListing=(page>1), cacheToDisc=False)


# -------------------------------
# Category (reports: movies) -> list wallpapers
# -------------------------------
def list_category(params):
    kind  = params.get("kind", "catalog")
    slug  = params.get("slug", "")
    title = params.get("title", slug or "Wallpapers")
    page  = int(params.get("page", "1"))
    use_cache = _get_bool("use_cache", True)

    if _should_abort():
        return
    _log(f"Opening '{title}' ({kind}:{slug}) page={page}")
    xbmcplugin.setContent(HANDLE, "movies")

    items, has_next = [], False

    # 1. Cache prüfen (wenn aktiviert)
    if use_cache:
        cached = _get_cache(kind, slug, page)
        if cached:
            _log(f"Using cache for {kind}:{slug}:{page}")
            items = cached.get("items", [])
            has_next = cached.get("has_next", False)

    # 2. Von WallpapersCraft laden (wenn nicht aus Cache)
    if not items:
        try:
            items, has_next = wc.list_wallpapers(kind, slug, page)
        except Exception as e:
            _log(f"list_wallpapers error for {kind}:{slug} p{page}: {e}")

    # 3. Backup: Falls WallpapersCraft nicht verfügbar, sKulls Archive nutzen
    if not items and skulls_source:
        _log("WallpapersCraft unavailable, trying sKulls archive as backup...")
        try:
            cats = skulls_source.list_categories()
            for c in cats:
                if c.get("title", "").lower() == slug.lower() or slug.lower() in c.get("title", "").lower():
                    imgs = skulls_source.list_images(c.get("href", ""))
                    for img in imgs:
                        items.append({
                            "title": img.get("title", "Wallpaper"),
                            "thumb": img.get("thumb", ""),
                            "href": img.get("img", "")
                        })
                    has_next = False
                    break
        except Exception as e:
            _log(f"Backup source failed: {e}")

    if not items:
        aliases = {
            "black_and_white": ["black-and-white", "bw"],
            "tv-series": ["tv_series", "tvseries", "serials", "tv"],
            "hi-tech": ["technologies", "technology", "tech"],
            "sport": ["sports"],
        }
        candidates = [(kind, slug)]
        if slug in aliases:
            for s in aliases[slug]:
                candidates.append((kind, s))
        for s in [slug] + aliases.get(slug, []):
            candidates.append(("tag", s))

        seen = set()
        for k, s in candidates:
            key = f"{k}:{s}"
            if key in seen:
                continue
            seen.add(key)
            try:
                tmp_items, tmp_next = wc.list_wallpapers(k, s, page)
                if tmp_items:
                    kind, slug = k, s
                    items, has_next = tmp_items, tmp_next
                    break
            except Exception:
                continue

    if not items:
        try:
            xbmcgui.Dialog().notification("sKulls Wallpapers", f"{title}: No results or timed out", "DefaultAddonsInfo.png", 3000)
        except Exception:
            pass

    # Apply resolution filter
    items = _apply_resolution_filter(items)

    for it in items:
        lbl = it.get("title") or title
        li = xbmcgui.ListItem(label=lbl)
        th = it.get("thumb")
        if th:
            li.setArt({"thumb": th, "icon": th, "poster": th, "fanart": th})
        _set_video_title(li, lbl)
        url = _url(mode="wallpaper", page_url=it.get("href",""), title=lbl)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    if has_next:
        nli = xbmcgui.ListItem(label=f"Next (page {page+1})")
        _set_video_title(nli, f"{title} — page {page+1}")
        nurl = _url(mode="category", kind=kind, slug=slug, page=str(page+1), title=title)
        xbmcplugin.addDirectoryItem(HANDLE, nurl, nli, isFolder=True)

    # Cache speichern
    if use_cache and items:
        _set_cache(kind, slug, page, {"items": items, "has_next": has_next})

    xbmcplugin.endOfDirectory(HANDLE, updateListing=(page>1), cacheToDisc=False)

# -------------------------------
# Wallpaper submenu (reports: files) -> 4K & 1080p; clicking downloads
# -------------------------------
def _set_video_title(li, title):
    try:
        vit = li.getVideoInfoTag()
        vit.setTitle(title)
    except Exception:
        li.setInfo("video", {"title": title})

def wallpaper_menu(params):
    page_url = params.get("page_url","")
    title    = params.get("title","Wallpaper")

    xbmcplugin.setContent(HANDLE, "files")

    try:
        sizes = wc.list_sizes(page_url)  # [{"label","url","thumb"}]
    except Exception as e:
        _log(f"list_sizes failed: {e}")
        sizes = []

    if not sizes:
        try:
            xbmcgui.Dialog().notification("sKulls Wallpapers", "No sizes found", "DefaultAddonsInfo.png", 3000)
        except Exception:
            pass
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    # Preview option
    preview_url = sizes[0].get("url", "")
    if preview_url:
        pli = xbmcgui.ListItem(label="PREVIEW")
        pli.setArt({"thumb": sizes[0].get("thumb", ""), "icon": _media_icon("preview")})
        purl = _url(mode="preview_image", img=preview_url, title=title)
        xbmcplugin.addDirectoryItem(HANDLE, purl, pli, isFolder=False)

    # Add to Favorites
    fav_url = _url(mode="add_favorite", title=title, url=page_url, thumb=sizes[0].get("thumb", ""))
    fav_li = xbmcgui.ListItem(label="ADD TO FAVORITES")
    fav_li.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
    xbmcplugin.addDirectoryItem(HANDLE, fav_url, fav_li, isFolder=False)

    # Add to Set
    set_url = _url(mode="add_to_set", title=title, url=page_url, thumb=sizes[0].get("thumb", ""))
    set_li = xbmcgui.ListItem(label="ADD TO SET")
    set_li.setArt({"icon": _media_icon("set"), "thumb": _media_icon("set")})
    xbmcplugin.addDirectoryItem(HANDLE, set_url, set_li, isFolder=False)

    # Separator
    li = xbmcgui.ListItem(label="--- Available Resolutions ---")
    xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)

    # Sort sizes by resolution (largest first)
    def res_sort(s):
        lbl = s.get("label", "0x0")
        try:
            w, h = lbl.split("x")
            return int(w) * int(h)
        except Exception:
            return 0
    sizes_sorted = sorted(sizes, key=res_sort, reverse=True)

    for s in sizes_sorted:
        label = s.get("label", "Unknown")
        img_url = s.get("url", "")
        if not img_url:
            continue
        # Icon basierend auf Auflösung
        if "3840" in label or "4096" in label:
            icon = "DefaultStar.png"
        elif "1920" in label:
            icon = "DefaultDownload.png"
        else:
            icon = "DefaultDownload.png"
        li = xbmcgui.ListItem(label=f"DOWNLOAD {label}")
        th = s.get("thumb", "")
        if th:
            li.setArt({"thumb": th, "icon": icon})
        url = _url(mode="download_image", img=img_url, title=title, label=label, ref=page_url)
        li.setProperty("IsPlayable", "false")
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def preview_image(params):
    """Vorschau eines Bildes anzeigen."""
    img_url = params.get("img", "")
    title = params.get("title", "Preview")
    if img_url:
        xbmc.executebuiltin(f'ShowPicture("{img_url}")')
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# Download selected image
# -------------------------------
def download_image(params):
    img_url = params.get("img", "")
    title   = params.get("title", "Wallpaper")
    label   = params.get("label", "")
    referer = params.get("ref", "")

    if not img_url:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Missing image URL", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    dest_dir = _get_download_dir()

    base = _sanitize_name(f"{title}_{label}" if label else title)
    p = up.urlparse(img_url)
    ext = os.path.splitext(os.path.basename(p.path))[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"

    i = 0
    while True:
        name = f"{base}{'' if i == 0 else f'_{i}'}{ext}"
        full = os.path.join(dest_dir, name)
        if not xbmcvfs.exists(full):
            dest_path = full
            break
        i += 1

    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Accept": "*/*",
    }
    if referer:
        headers["Referer"] = referer

    dp = xbmcgui.DialogProgress()
    dp.create("sKulls Wallpapers", "Starting download...")
    try:
        req = urlreq.Request(img_url, headers=headers)
        with urlreq.urlopen(req, timeout=20) as r:
            total = int(r.headers.get("Content-Length", "0")) or 0
            f = xbmcvfs.File(dest_path, "w")
            try:
                chunk = 1024 * 1024
                read = 0
                last = 0
                while True:
                    if dp.iscanceled():
                        return
                    buf = r.read(chunk)
                    if not buf:
                        break
                    f.write(buf)
                    read += len(buf)
                    now = time.time()
                    if now - last > 0.1:
                        pct = int((read * 100) / total) if total else 0
                        dp.update(max(0, min(100, pct)),
                                  f"Downloading...\\n{read//1024//1024} / {total//1024//1024} MB")
                        last = now
            finally:
                f.close()
        dp.update(100, "Finishing...")
        xbmcgui.Dialog().notification("sKulls Wallpapers", f"Saved to:\\n{dest_dir}", "DefaultAddonsInfo.png", 3500)
    except Exception as e:
        _log(f"Download failed: {e}")
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Download failed", "DefaultAddonsInfo.png", 3000)
    finally:
        try:
            dp.close()
        except Exception:
            pass
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# My Wallpapers: browse, view, delete, import
# -------------------------------
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")

def my_wallpapers(params):
    cur = params.get("dir") or _get_download_dir()
    cur = xbmcvfs.translatePath(cur)

    xbmcplugin.setContent(HANDLE, "images")

    # Top actions
    imp1 = xbmcgui.ListItem(label="[Import single image…]")
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="import_image"), imp1, isFolder=False)
    imp2 = xbmcgui.ListItem(label="[Import multiple images…]")
    xbmcplugin.addDirectoryItem(HANDLE, _url(mode="import_folder"), imp2, isFolder=False)

    dl = _get_download_dir().rstrip("/\\")
    if os.path.normpath(cur) != os.path.normpath(dl):
        par = os.path.dirname(cur.rstrip("/\\")) or cur
        pli = xbmcgui.ListItem(label="↥ Parent folder")
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="my_wallpapers", dir=par), pli, isFolder=True)

    try:
        dirs, files = xbmcvfs.listdir(cur)
    except Exception:
        dirs, files = [], []
    for d in dirs:
        p = os.path.join(cur, d)
        li = xbmcgui.ListItem(label=f"[{d}]")
        li.setArt({"icon": _media_icon("mywallpaper"), "thumb": _media_icon("mywallpaper")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="my_wallpapers", dir=p), li, isFolder=True)

    for f in files:
        if not f.lower().endswith(IMG_EXTS):
            continue
        p = os.path.join(cur, f)
        li = xbmcgui.ListItem(label=f)
        li.setArt({"thumb": p, "icon": p, "poster": p, "fanart": p})
        url = _url(mode="open_context", fp=p)
        cmi = [
            ("View",   f'RunPlugin("{_url(mode="view_file", fp=p)}")'),
            ("Delete", f'RunPlugin("{_url(mode="delete_file", fp=p)}")'),
        ]
        li.addContextMenuItems(cmi, replaceItems=False)
        li.setProperty("IsPlayable", "false")
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def open_context(params):
    xbmc.executebuiltin('Action(ContextMenu)')
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def view_file(params):
    fp = params.get("fp","")
    if fp:
        xbmc.executebuiltin(f'ShowPicture("{fp}")')
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def delete_file(params):
    fp = params.get("fp","")
    if not fp or not xbmcvfs.exists(fp):
        xbmcgui.Dialog().notification("sKulls Wallpapers", "File not found", "DefaultAddonsInfo.png", 2500)
    else:
        if xbmcgui.Dialog().yesno("Delete", f"Delete this file?\\n{os.path.basename(fp)}"):
            ok = False
            try:
                ok = xbmcvfs.delete(fp)
            except Exception as e:
                _log(f"delete failed: {e}")
            if ok:
                xbmcgui.Dialog().notification("sKulls Wallpapers", "Deleted", "DefaultAddonsInfo.png", 2000)
            else:
                xbmcgui.Dialog().notification("sKulls Wallpapers", "Delete failed", "DefaultAddonsInfo.png", 2500)
        xbmc.executebuiltin("Container.Refresh")
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def import_image(_params):
    try:
        src = xbmcgui.Dialog().browse(2, "Select image", "files", ".jpg|.jpeg|.png|.webp")
    except TypeError:
        src = xbmcgui.Dialog().browse(1, "Select image", "files")
    if not src:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    if not xbmcvfs.exists(src):
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Source not found", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    if not src.lower().endswith((".jpg",".jpeg",".png",".webp")):
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Not an image file", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    dest_dir = _get_download_dir()
    base = _sanitize_name(os.path.splitext(os.path.basename(src))[0])
    ext = os.path.splitext(src)[1].lower() or ".jpg"
    i = 0
    while True:
        name = f"{base}{'' if i == 0 else f'_{i}'}{ext}"
        dest = os.path.join(dest_dir, name)
        if not xbmcvfs.exists(dest):
            break
        i += 1
    ok = False
    try:
        ok = xbmcvfs.copy(src, dest)
    except Exception as e:
        _log(f"copy failed: {e}")
    if ok:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Imported", "DefaultAddonsInfo.png", 2000)
    else:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Import failed", "DefaultAddonsInfo.png", 2500)
    xbmc.executebuiltin(f'Container.Update("{_url(mode="my_wallpapers", dir=dest_dir)}", replace)')

def import_folder(_params):
    try:
        src_dir = xbmcgui.Dialog().browse(3, "Select folder", "files")
    except TypeError:
        src_dir = xbmcgui.Dialog().browse(0, "Select folder", "files")
    if not src_dir:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    if not xbmcvfs.exists(src_dir):
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Folder not found", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    dest_dir = _get_download_dir()
    try:
        dirs, files = xbmcvfs.listdir(src_dir)
    except Exception:
        dirs, files = [], []
    images = [f for f in files if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
    if not images:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "No images in folder", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    dp = xbmcgui.DialogProgress()
    dp.create("Importing", f"{len(images)} image(s)…")
    copied, failed = 0, 0
    for idx, fname in enumerate(images, 1):
        if dp.iscanceled():
            break
        dp.update(int((idx * 100) / len(images)), f"{fname}")
        src = os.path.join(src_dir, fname)
        base = _sanitize_name(os.path.splitext(fname)[0])
        ext = os.path.splitext(fname)[1].lower()
        j = 0
        while True:
            name = f"{base}{'' if j == 0 else f'_{j}'}{ext}"
            dest = os.path.join(dest_dir, name)
            if not xbmcvfs.exists(dest):
                break
            j += 1
        try:
            if xbmcvfs.copy(src, dest):
                copied += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    try:
        dp.close()
    except Exception:
        pass

    xbmcgui.Dialog().notification("sKulls Wallpapers", f"Imported: {copied}, Failed: {failed}", "DefaultAddonsInfo.png", 3500)
    xbmc.executebuiltin(f'Container.Update("{_url(mode="my_wallpapers", dir=dest_dir)}", replace)')



# -------------------------------
# sKulls Wallpapers integration
# -------------------------------
def skulls_root(_params):
    if not skulls_source:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "sKulls source not available", "DefaultAddonsInfo.png", 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    xbmcplugin.setContent(HANDLE, "files")
    try:
        cats = skulls_source.list_categories()
    except Exception as e:
        _log(f"sKulls list_categories failed: {e}")
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Failed to load sKulls categories", "DefaultAddonsInfo.png", 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    show_adult = _get_bool("show_adult", False)
    adult_keywords = ["xxx", "adult", "porn", "sex", "18+", "nsfw"]

    for c in cats:
        title = c.get("title") or "Folder"
        href  = c.get("href") or ""

        # Filter XXX/Adult if disabled
        if not show_adult:
            if any(kw in title.lower() for kw in adult_keywords):
                continue

        li = xbmcgui.ListItem(label=title)
        li.setArt({"icon": _media_icon("categories"), "thumb": _media_icon("categories")})
        url = _url(mode="skulls_category", path=href, title=title)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def list_skulls_category(params):
    if not skulls_source:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "sKulls source not available", "DefaultAddonsInfo.png", 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return
    path = params.get("path", "")
    title = params.get("title", "sKulls")
    xbmcplugin.setContent(HANDLE, "images")

    # Check adult filter
    show_adult = _get_bool("show_adult", False)
    adult_keywords = ["xxx", "adult", "porn", "sex", "18+", "nsfw"]
    is_adult_cat = any(kw in title.lower() for kw in adult_keywords)

    if is_adult_cat and not show_adult:
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    try:
        imgs = skulls_source.list_images(path)
    except Exception as e:
        _log(f"sKulls list_images failed: {e}")
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Failed to load images", "DefaultAddonsInfo.png", 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    for it in imgs:
        name = it.get("title") or "Wallpaper"
        img  = it.get("img") or ""
        thumb = it.get("thumb") or img

        # Menu mit Optionen
        li = xbmcgui.ListItem(label=name)
        art = {"thumb": thumb, "icon": thumb, "fanart": thumb, "poster": thumb}
        li.setArt(art)
        li.setInfo("image", {"title": name})

        # Öffne Menu beim Klick
        url = _url(mode="skulls_wallpaper_menu", img=img, title=name, thumb=thumb)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def skulls_wallpaper_menu(params):
    """Menü für sKulls Wallpaper mit Preview, Favorites, Set."""
    img_url = params.get("img", "")
    title = params.get("title", "Wallpaper")
    thumb = params.get("thumb", "")

    xbmcplugin.setContent(HANDLE, "files")

    if not img_url:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "No image URL", "DefaultAddonsInfo.png", 2500)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    # Preview
    pli = xbmcgui.ListItem(label="PREVIEW")
    pli.setArt({"thumb": thumb, "icon": _media_icon("preview")})
    purl = _url(mode="preview_image", img=img_url, title=title)
    xbmcplugin.addDirectoryItem(HANDLE, purl, pli, isFolder=False)

    # Add to Favorites
    fav_url = _url(mode="add_favorite", title=title, url=img_url, thumb=thumb)
    fav_li = xbmcgui.ListItem(label="ADD TO FAVORITES")
    fav_li.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
    xbmcplugin.addDirectoryItem(HANDLE, fav_url, fav_li, isFolder=False)

    # Add to Set
    set_url = _url(mode="add_to_set", title=title, url=img_url, thumb=thumb)
    set_li = xbmcgui.ListItem(label="ADD TO SET")
    set_li.setArt({"icon": _media_icon("set"), "thumb": _media_icon("set")})
    xbmcplugin.addDirectoryItem(HANDLE, set_url, set_li, isFolder=False)

    # Download
    li = xbmcgui.ListItem(label="DOWNLOAD")
    li.setArt({"thumb": thumb, "icon": _media_icon("download")})
    url = _url(mode="download_image", img=img_url, title=title, label="sKulls", ref="skulls")
    li.setProperty("IsPlayable", "false")
    xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# Random Wallpaper
# -------------------------------
def random_wallpaper(_params):
    xbmcplugin.setContent(HANDLE, "movies")
    import random

    # Try multiple random categories
    entries = _category_entries()
    random.shuffle(entries)

    items = []
    cat_title = "Unknown"

    for cat in entries[:5]:  # Try up to 5 categories
        title, slug, kind = cat[0], cat[1], cat[2]
        try:
            items, _ = wc.list_wallpapers(kind, slug, 1)
            if items:
                cat_title = title
                break
        except Exception:
            continue

    if not items:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "No wallpapers found", "DefaultAddonsInfo.png", 3000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    _log(f"Random wallpaper from {cat_title}")
    xbmcgui.Dialog().notification("sKulls Wallpapers", f"Random from {cat_title}", "DefaultAddonsInfo.png", 1500)

    # Pick random item as main
    item = random.choice(items)
    it_title = item.get("title") or "Random"
    it_url = item.get("href", "")

    li = xbmcgui.ListItem(label=f"RANDOM: {it_title}")
    th = item.get("thumb", "")
    if th:
        li.setArt({"thumb": th, "icon": th, "poster": th, "fanart": th})
    url = _url(mode="wallpaper", page_url=it_url, title=it_title)
    xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    # More random options
    for _ in range(min(9, len(items))):
        if items:
            r = random.choice(items)
            rt = r.get("title") or "Wallpaper"
            rl = r.get("href", "")
            li = xbmcgui.ListItem(label=rt)
            if r.get("thumb"):
                li.setArt({"thumb": r.get("thumb"), "icon": r.get("thumb")})
            url = _url(mode="wallpaper", page_url=rl, title=rt)
            xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# Favorites
# -------------------------------
def show_favorites(_params):
    xbmcplugin.setContent(HANDLE, "images")
    favs = _get_favorites()
    _log(f"show_favorites: loaded {len(favs)} items")

    if not favs:
        li = xbmcgui.ListItem(label="No favorites yet - add some from wallpaper menu!")
        xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)
    else:
        _log(f"Showing {len(favs)} favorites")
        # Slideshow button
        sli = xbmcgui.ListItem(label="Start Slideshow")
        sli.setArt({"icon": _media_icon("slideshow"), "thumb": _media_icon("slideshow")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="slideshow", source="favorites"), sli, isFolder=False)

        for f in favs:
            name = f.get("title", "Wallpaper")
            url = f.get("url", "")
            thumb = f.get("thumb", "")
            li = xbmcgui.ListItem(label=name)
            li.setArt({"thumb": thumb, "icon": thumb, "fanart": thumb, "poster": thumb})
            li.setInfo("image", {"title": name})
            # Context menu with remove
            cm = [("Remove from Favorites", f'RunPlugin("{_url(mode="remove_favorite", url=url)}")')]
            try:
                li.addContextMenuItems(cm, replaceItems=False)
            except Exception:
                pass
            page_url = url
            xbmcplugin.addDirectoryItem(HANDLE, _url(mode="wallpaper", page_url=page_url, title=name), li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def add_favorite(params):
    title = params.get("title", "Wallpaper")
    url = params.get("url", "")
    thumb = params.get("thumb", "")
    _log(f"add_favorite: title={title}, url={url}, thumb={thumb}")
    result = _add_favorite(title, url, thumb)
    _log(f"add_favorite result: {result}")
    if result:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Added to favorites!", "DefaultAddonsInfo.png", 2000)
    else:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Already in favorites", "DefaultAddonsInfo.png", 2000)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def remove_favorite(params):
    url = params.get("url", "")
    _remove_favorite(url)
    xbmc.executebuiltin("Container.Refresh")

# -------------------------------
# Wallpaper Set (Batch)
# -------------------------------
def show_set(_params):
    xbmcplugin.setContent(HANDLE, "files")
    items = _load_set_selection()

    if not items:
        li = xbmcgui.ListItem(label="Wallpaper Set is empty")
        xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)
    else:
        # Slideshow button
        sli = xbmcgui.ListItem(label="Start Slideshow")
        sli.setArt({"icon": _media_icon("slideshow"), "thumb": _media_icon("slideshow")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="slideshow", source="set"), sli, isFolder=False)

        # Download all
        if items:
            li = xbmcgui.ListItem(label=f"[Download All ({len(items)} images)]")
            li.setArt({"icon": _media_icon("download"), "thumb": _media_icon("download")})
            xbmcplugin.addDirectoryItem(HANDLE, _url(mode="download_set"), li, isFolder=False)

        # Clear set
        cli = xbmcgui.ListItem(label="[Clear Set]")
        cli.setArt({"icon": _media_icon("favorites"), "thumb": _media_icon("favorites")})
        xbmcplugin.addDirectoryItem(HANDLE, _url(mode="clear_set"), cli, isFolder=False)

        for it in items:
            name = it.get("title", "Wallpaper")
            url = it.get("url", "")
            thumb = it.get("thumb", "")
            li = xbmcgui.ListItem(label=name)
            li.setArt({"thumb": thumb, "icon": thumb})
            # Remove from set
            cm = [("Remove from Set", f'RunPlugin("{_url(mode="remove_from_set", url=url)}")')]
            try:
                li.addContextMenuItems(cm, replaceItems=False)
            except Exception:
                pass
            xbmcplugin.addDirectoryItem(HANDLE, _url(mode="wallpaper", page_url=url, title=name), li, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def add_to_set(params):
    title = params.get("title", "Wallpaper")
    url = params.get("url", "")
    thumb = params.get("thumb", "")
    if _add_to_set(title, url, thumb):
        xbmcgui.Dialog().notification("sKulls Wallpapers", f"Added to Set ({_get_set_count()})", "DefaultAddonsInfo.png", 2000)
    else:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Already in Set", "DefaultAddonsInfo.png", 2000)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

def remove_from_set(params):
    url = params.get("url", "")
    _remove_from_set(url)
    xbmc.executebuiltin("Container.Refresh")

def clear_set(_params):
    _clear_set()
    xbmcgui.Dialog().notification("sKulls Wallpapers", "Wallpaper Set cleared", "DefaultAddonsInfo.png", 2000)
    xbmc.executebuiltin("Container.Refresh")

def download_set(_params):
    """Download all images in set."""
    items = _load_set_selection()
    if not items:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Set is empty", "DefaultAddonsInfo.png", 2000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    dest_dir = _get_download_dir()
    dp = xbmcgui.DialogProgress()
    dp.create("sKulls Wallpapers", f"Downloading {len(items)} images...")

    downloaded = 0
    failed = 0

    for idx, it in enumerate(items):
        if dp.iscanceled():
            break
        dp.update(int((idx * 100) / len(items)), f"Downloading {idx+1}/{len(items)}")
        page_url = it.get("url", "")
        title = it.get("title", "wallpaper")

        if not page_url:
            failed += 1
            continue

        # Hole die Bild-URL von der Seite
        img_url = None
        try:
            sizes = wc.list_sizes(page_url)
            if sizes:
                # Nimm die größte verfügbare
                def res_sort(s):
                    lbl = s.get("label", "0x0")
                    try:
                        w, h = lbl.split("x")
                        return int(w) * int(h)
                    except Exception:
                        return 0
                sizes_sorted = sorted(sizes, key=res_sort, reverse=True)
                img_url = sizes_sorted[0].get("url", "")
        except Exception as e:
            _log(f"Get sizes failed: {e}")

        if not img_url:
            failed += 1
            continue

        try:
            base = _sanitize_name(title)
            p = up.urlparse(img_url)
            ext = os.path.splitext(os.path.basename(p.path))[1].lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png"):
                ext = ".jpg"
            dest_path = os.path.join(dest_dir, f"{base}{ext}")
            i = 1
            while xbmcvfs.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base}_{i}{ext}")
                i += 1

            # Download mit Streaming
            req = urlreq.Request(img_url, headers={"User-Agent": "Mozilla/5.0", "Referer": page_url})
            with urlreq.urlopen(req, timeout=30) as r:
                total = int(r.headers.get("Content-Length", 0)) or 0
                f = xbmcvfs.File(dest_path, "w")
                try:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        buf = r.read(chunk_size)
                        if not buf:
                            break
                        f.write(buf)
                finally:
                    f.close()
            downloaded += 1
        except Exception as e:
            _log(f"Set download failed: {e}")
            failed += 1

    try:
        dp.close()
    except Exception:
        pass
        pass

    _clear_set()
    xbmcgui.Dialog().notification("sKulls Wallpapers", f"Downloaded: {downloaded}, Failed: {failed}", "DefaultAddonsInfo.png", 4000)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# Slideshow - als Bildschirmschoner-Modus
# -------------------------------
def slideshow(params):
    """Start slideshow with images from favorites or set."""
    mode = params.get("source", "favorites")
    _log(f"Slideshow started, mode={mode}")

    image_urls = []
    local_files = []

    # Temp dir für Slideshow-Bilder
    slide_dir = xbmcvfs.translatePath(os.path.join(PROFILE_DIR, "slideshow"))
    try:
        if not xbmcvfs.exists(slide_dir):
            xbmcvfs.mkdirs(slide_dir)
    except:
        pass

    # Lade alle Favoriten/Set und hole Bild-URLs
    dp = xbmcgui.DialogProgress()
    dp.create("Preparing slideshow...", "Loading images...")

    if mode == "favorites":
        favs = _get_favorites()
        _log(f"Slideshow: loading {len(favs)} favorites")
        for idx, f in enumerate(favs):
            if dp.iscanceled():
                break
            dp.update(int((idx * 100) / len(favs)), f"Loading {idx+1}/{len(favs)}")
            page_url = f.get("url", "")
            fav_title = f.get("title", "")
            thumb = f.get("thumb", "")
            _log(f"Processing favorite {idx+1}: {fav_title[:30]}...")
            _log(f"  URL: {page_url[:50] if page_url else 'None'}...")

            img_url = None

            # Check if it's a direct image URL (sKulls/Archive)
            if page_url and ("archive.org" in page_url or page_url.endswith((".jpg", ".jpeg", ".png", ".webp"))):
                img_url = page_url
                _log(f"  Direct image URL (sKulls)")
            # Or a wallpaperscraft page URL
            elif page_url:
                try:
                    sizes = wc.list_sizes(page_url)
                    _log(f"  Got {len(sizes) if sizes else 0} sizes for {fav_title[:20]}")
                    if sizes:
                        def res_sort(s):
                            lbl = s.get("label", "0x0")
                            try:
                                w, h = lbl.split("x")
                                return int(w) * int(h)
                            except:
                                return 0
                        sizes_sorted = sorted(sizes, key=res_sort, reverse=True)
                        img_url = sizes_sorted[0].get("url", "")
                except Exception as e:
                    _log(f"Slideshow error for {fav_title}: {e}")

            if img_url:
                image_urls.append((fav_title, img_url))
                _log(f"  Added: {img_url[:40]}...")
            else:
                _log(f"  FAILED - no image URL")
    elif mode == "set":
        set_items = _load_set_selection()
        for idx, it in enumerate(set_items):
            if dp.iscanceled():
                break
            dp.update(int((idx * 100) / len(set_items)), f"Loading {idx+1}/{len(set_items)}")
            page_url = it.get("url", "")
            if page_url:
                try:
                    sizes = wc.list_sizes(page_url)
                    if sizes:
                        def res_sort(s):
                            lbl = s.get("label", "0x0")
                            try:
                                w, h = lbl.split("x")
                                return int(w) * int(h)
                            except:
                                return 0
                        sizes_sorted = sorted(sizes, key=res_sort, reverse=True)
                        img_url = sizes_sorted[0].get("url", "")
                        if img_url:
                            image_urls.append((it.get("title", "img"), img_url))
                except Exception as e:
                    _log(f"Slideshow set error: {e}")

    # Download alle Bilder lokal
    dp.update(0, "Downloading images for slideshow...")
    for idx, (name, img_url) in enumerate(image_urls):
        if dp.iscanceled():
            break
        dp.update(int((idx * 100) / len(image_urls)), f"Downloading {idx+1}/{len(image_urls)}")
        try:
            ext = os.path.splitext(os.path.basename(up.urlparse(img_url).path))[1] or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png"):
                ext = ".jpg"
            local_path = os.path.join(slide_dir, f"slide_{idx}{ext}")
            req = urlreq.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlreq.urlopen(req, timeout=15) as r:
                with xbmcvfs.File(local_path, "w") as f:
                    f.write(r.read())
            local_files.append(local_path)
        except Exception as e:
            _log(f"Download slide error: {e}")

    try:
        dp.close()
    except:
        pass

    _log(f"Slideshow: {len(local_files)} local files ready")

    if not local_files:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "No images ready", "DefaultAddonsInfo.png", 2000)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
        return

    # Starte Slideshow mit lokalen Dateien
    if len(local_files) == 1:
        xbmc.executebuiltin(f'ShowPicture("{local_files[0]}")')
    else:
        # Öffne erstes Bild
        xbmc.executebuiltin(f'ShowPicture("{local_files[0]}")')
        # Starte Slideshow mit Ordner
        xbmc.sleep(1500)
        xbmc.executebuiltin(f'SlideShow({slide_dir})')

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)


# -------------------------------
# Cache Management
# -------------------------------
def clear_cache(_params):
    _clear_cache()
    try:
        xbmcgui.Dialog().notification("sKulls Wallpapers", "Cache cleared", "DefaultAddonsInfo.png", 2000)
    except Exception:
        pass
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# -------------------------------
# Router / Entry
# -------------------------------
def router(params):
    mode = params.get("mode", "root")
    if mode == "root":
        show_root()
    elif mode == "search_prompt":
        search_prompt(params)
    elif mode == "search":
        list_search_results(params)
    elif mode == "category":
        list_category(params)
    elif mode == "wallpaper":
        wallpaper_menu(params)
    elif mode == "download_image":
        download_image(params)
    elif mode == "my_wallpapers":
        my_wallpapers(params)
    elif mode == "open_context":
        open_context(params)
    elif mode == "view_file":
        view_file(params)
    elif mode == "delete_file":
        delete_file(params)
    elif mode == "import_image":
        import_image(params)
    elif mode == "import_folder":
        import_folder(params)
    elif mode == "warm_thumbs":
        warm_thumbs(params)
    elif mode == "skulls_root":
        skulls_root(params)
    elif mode == "skulls_category":
        list_skulls_category(params)
    elif mode == "skulls_wallpaper_menu":
        skulls_wallpaper_menu(params)
    elif mode == "clear_cache":
        clear_cache(params)
    elif mode == "add_custom_source":
        add_custom_source(params)
    elif mode == "manage_custom_sources":
        manage_custom_sources(params)
    elif mode == "delete_custom_source":
        delete_custom_source(params)
    elif mode == "open_custom_url":
        open_custom_url(params)
    elif mode == "open_settings":
        ADDON.openSettings()
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
    elif mode == "browse_custom_source":
        browse_custom_source(params)
    elif mode == "custom_wallpaper":
        custom_wallpaper(params)
    elif mode == "show_history":
        show_history(params)
    elif mode == "clear_history":
        clear_history(params)
    elif mode == "preview_image":
        preview_image(params)
    elif mode == "random_wallpaper":
        random_wallpaper(params)
    elif mode == "show_favorites":
        show_favorites(params)
    elif mode == "add_favorite":
        add_favorite(params)
    elif mode == "remove_favorite":
        remove_favorite(params)
    elif mode == "show_set":
        show_set(params)
    elif mode == "add_to_set":
        add_to_set(params)
    elif mode == "remove_from_set":
        remove_from_set(params)
    elif mode == "clear_set":
        clear_set(params)
    elif mode == "download_set":
        download_set(params)
    elif mode == "slideshow":
        slideshow(params)
    else:
        show_root()

if __name__ == "__main__":
    qs = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        qs = dict(up.parse_qsl(sys.argv[2][1:]))
    router(qs)

