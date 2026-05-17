# sKulls Fusion Wallpapers

**Version:** 1.2.3
**Kodi Version:** 21.3+ (Omega)
**Python:** 3.0.1

Ein hochwertiges Wallpaper-Add-on für Kodi mit Unterstützung für WallpapersCraft, Internet Archive und eigene Quellen.

---

## Funktionen

### Hauptfunktionen
- **WallpapersCraft Suche** - Durchsuche tausende 4K/HD Wallpapers
- **sKulls Archive** - Wallpapers vom Internet Archive
- **Zufalls-Wallpaper** - Zufälliges Wallpaper aus einer Kategorie
- **Favoriten** - Speichere deine Lieblings-Wallpapers
- **Wallpaper-Set** - Erstelle eigene Kollektionen
- **Diashow-Modus** - Slideshow aus Favoriten oder Set

### Filter & Einstellungen
- **18+ Filter** - Filterung von adult content (einstellbar)
- **Auflösungs-Filter** - Filtere nach 4K, 2K, FullHD, HD
- **Offline-Cache** - 24h Cache für schnellere Ladezeiten
- **Backup-Quelle** - Automatischer Fallback zu sKulls Archive

### Custom Sources
- Eigene Wallpaper-Quellen hinzufügen
- Internet Archive Ordner durchsuchen
- Vorschau, Favoriten, Download für alle Quellen

---

## Installation

### Voraussetzungen
- Kodi 21.3 (Omega) oder höher
- Python 3.0.1

### Installationsmethoden

#### 1. Aus ZIP installieren
1. Lade die `.zip` Datei herunter
2. Gehe zu Kodi → Einstellungen → Add-ons → Aus ZIP installieren
3. Wähle die heruntergeladene ZIP-Datei

#### 2. Manuell installieren
1. Entpacke die Dateien in den Add-on Ordner:
   - Windows: `%APPDATA%\Kodi\addons\plugin.program.sKullsWallpapers\`
   - Linux/Mac: `~/.kodi/addons/plugin.program.sKullsWallpapers/`
2. Starte Kodi neu

---

## Benutzerhandbuch

### Hauptmenü

```
====================
sKulls Fusion Wallpapers
====================

🔍 Search Wallpapers
📜 Search History (wenn vorhanden)
🎲 Random Wallpaper
★ My Favorites (Anzahl)
📁 Wallpaper Set (Anzahl)
-------------------
📂 My Wallpapers
💀 sKulls Archive
[Custom Sources]
[Manage Custom Sources]
-------------------
📋 Categories
```

### Suchfunktion
1. Klicke auf "Search Wallpapers"
2. Gib einen Suchbegriff ein (z.B. "nature", "cars", "space")
3. Durchsuche die Ergebnisse
4. Wähle ein Wallpaper für Optionen

### Wallpaper Optionen
Beim Auswahl eines Wallpapers:
- **PREVIEW** - Vorschau anzeigen
- **ADD TO FAVORITES** - Zu Favoriten hinzufügen
- **ADD TO SET** - Zum Wallpaper-Set hinzufügen
- **DOWNLOAD** - In lokalen Ordner speichern
- **Verfügbare Auflösungen** - Wähle die gewünschte Auflösung

### Favoriten & Set
- **Favoriten** - Persönliche Sammlung
- **Wallpaper-Set** - Für Diashows
- Beide können als Slideshow abgespielt werden

### Custom Sources
Im Hauptmenü unter "Custom Sources":
1. Klicke auf "+ Add New Source" (in den Einstellungen)
2. Gib einen Namen ein
3. Gib die URL ein (z.B. ein Archive.org Ordner)
4. Die Source erscheint im Menü

#### Internet Archive Beispiel
URL: `https://ia601602.us.archive.org/6/items/tr049_20230511/WALLPAPERS/`

---

## Einstellungen

### General
- **Download folder** - Zielordner für Downloads
- **Static thumbnails** - Statische Kategorie-Bilder
- **Show 18+** - Adult-Content anzeigen

### Filter
- **Resolution filter** - Nach Auflösung filtern
  - Alle
  - 4K (3840x)
  - 2K (2560x)
  - FullHD (1920x)
  - HD (1280x)

### Custom Sources
- **Add New Source** - Neue Quelle hinzufügen

### Advanced
- **Enable cache** - Offline-Cache (24h)
- **Backup source** - Automatischer Fallback
- **Clear cache** - Cache leeren

---

## Tastenkombinationen

| Aktion | Beschreibung |
|--------|--------------|
| Rechtsklick | Kontextmenü |
| Info-Taste | Wallpaper-Details |
| Play-Taste | Download starten |

---

## Ordnerstruktur

```
plugin.program.sKullsWallpapers/
├── default.py              # Haupt-Add-on
├── addon.xml              # Add-on Manifest
├── README.md              # Diese Datei
├── icon.png               # Add-on Icon
├── fanart.jpg             # Hintergrundbild
├── changelog.txt          # Änderungen
└── resources/
    ├── settings.xml       # Einstellungen
    ├── media/             # Icons
    └── lib/
        ├── skulls_source.py    # Internet Archive
        └── wc_scraper.py       # WallpapersCraft
```

---

## Fehlerbehebung

### Problem: Keine Ergebnisse
- Prüfe die Internetverbindung
- Versuche es später erneut

### Problem: Langsame Ladezeiten
- Aktiviere den Offline-Cache
- Erhöhe die Auflösung nicht zu hoch

### Problem: Custom Sources funktionieren nicht
- URL muss mit `http://` oder `https://` beginnen
- Archive.org: Verwende den Ordner-Link, nicht die Datei

### Problem: Download fehlgeschlagen
- Prüfe den Download-Ordner in den Einstellungen
- Genug Speicherplatz vorhanden?

---

## Quellen

- **WallpapersCraft** - `wallpaperscraft.com`
- **Internet Archive** - `archive.org`
- **Eigene Quellen** - Benutzer-definiert

---

## Lizenz

**GPL-3.0** - GNU General Public License v3.0

---

## Kontakt & Support

- Website: [wird noch hinzugefügt]
- Forum: [wird noch hinzugefügt]
- Email: [wird noch hinzugefügt]

---

## Version History

### v1.2.3
- Custom Sources (eigene Quellen)
- Auflösungs-Filter
- Farbige UI
- Bugfixes

### v1.2.0
- Diashow-Modus
- Wallpaper-Set
- Farbige Menü-Labels
- Eigene Icons

### v1.1.x
- Suchverlauf
- Zufalls-Wallpaper
- Favoriten

### v1.0.x
- Erste Version (Fork von plugin.video.4kwallpapers)

---

*Erstellt von sKulls inc.*