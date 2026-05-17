# sKulls Radio Suite - Detaillierte Dokumentation

## Inhaltsverzeichnis
1. [Überblick](#überblick)
2. [Installation](#installation)
3. [Hauptfunktionen](#hauptfunktionen)
4. [Menü-Struktur](#menü-struktur)
5. [Stream-Verwaltung](#stream-verwaltung)
6. [Suche](#suche)
7. [Backup & Wiederherstellung](#backup--wiederherstellung)
8. [Tools](#tools)
9. [Cloud-Sync](#cloud-sync)
10. [Tipps & Tricks](#tipps--tricks)

---

## Überblick

**sKulls Radio Suite** ist ein umfassendes Kodi-Radio-Add-on mit Cloud-Sync, AES-256-Verschlüsselung und vielen integrierten Tools.

- **Version:** 3.2.1
- **Kompatibilität:** Kodi 21.x (Omega)
- **Sprache:** Deutsch

---

## Installation

1. Add-on als ZIP installieren oder aus Ordner laden
2. Einstellungen öffnen und Cloud-Features aktivieren (optional)
3. Streams werden automatisch geladen

---

## Hauptfunktionen

### Stream-Verwaltung
- **Streams** aus verschiedenen Genres und Ländern
- **Favoriten** - Streams als Favoriten markieren
- **Verlauf** - Zuletzt gespielte Streams anzeigen
- **Filter & Sortierung** - Streams nach Genre, Land, Qualität filtern

### Suche
- **Schnellsuche** im Hauptmenü
- Sucht nach Stream-Name, Domain, Genre
- Ergebnisse werden als klickbare Liste angezeigt
- Stream durch Klick direkt abspielen

### Backup & Wiederherstellung
- **ZIP-Backup** - Manuelle Sicherung von Einstellungen
- **VIP-Snapshot** - Schnellsicherung von Favoriten, Verlauf, Playcounts
- **Backup-Galerie** - Alle Backups anzeigen, wiederherstellen, löschen
- **Undo-Restore** - Gelöschte Dateien aus .bak_ Backups wiederherstellen

### Cloud-Sync (Optional)
- Google Drive / Dropbox Support
- AES-256 verschlüsselte Backups
- Automatische Synchronisierung per Zeitintervall

### Tools
- **Stream Health-Check** - Prüft ob Streams online sind
- **Playcount-Statistik** - Zeigt meistgespielte Streams
- **Zuletzt hinzugefügt** - Neue Streams seit letztem Besuch
- **Diagnose-Tools** - JSON/ZIP Integritätsprüfung

---

## Menü-Struktur

```
┌─────────────────────────────────────┐
│ === sKulls Radio Suite ===          │
├─────────────────────────────────────┤
│ 🔍 Suche                    [Blau] │
│ ⚙ Filter / Sortierung       [Cyan] │
│ ★ Favoriten                 [Gold] │
│ 📜 Verlauf                  [Orange]│
│ ➕ Stream hinzufügen        [Lime]  │
│ 📀 Playlist importieren     [Violett]│
├─────────────────────────────────────┤
│ ===== TOOLS =====            [Rot]  │
├─────────────────────────────────────┤
│ ❤️ Stream Health-Check     [Rot]   │
│ ⚠ Fehlende Icons           [Grau]  │
│ 💾 ZIP Backup              [Blau]  │
│ 📁 Backup-Galerie          [Blau]  │
│ 🏷 Backups filtern         [Blau]  │
│ ⭐ VIP Snapshot            [Gold]  │
│ ↩ Undo Restore             [Violett]│
│ 📋 JSON Diagnose           [Violett]│
│ 📦 ZIP Diagnose            [Violett]│
├─────────────────────────────────────┤
│ --- GitHub Features --- (wenn aktiviert) │
├─────────────────────────────────────┤
│ --- Statistik ---            [Orange]│
│ 📊 Stream-Statistik         [Orange]│
│ 🆕 Zuletzt hinzugefügt      [Cyan]  │
├─────────────────────────────────────┤
│ Stream-Kategorien (Domains)         │
│ • bigFM                           │
│ • Radio.de                        │
│ • ...                             │
└─────────────────────────────────────┘
```

### Farb-Bedeutung
- **[Blau]** - Suche, Filter, Backup
- **[Cyan]** - Neu hinzugefügt, Filteroptionen
- **[Gold]** - Favoriten, VIP-Features
- **[Orange]** - Verlauf, Statistik
- **[Lime]** - Stream hinzufügen
- **[Violett]** - Playlist, Diagnose
- **[Rot]** - Health-Check, wichtige Tools

---

## Stream-Verwaltung

### Stream abspielen
1. Kategorie auswählen (z.B. "bigFM")
2. Stream auswählen
3. Stream startet automatisch

### Stream zu Favoriten hinzufügen
- Im Kontextmenü: "Zu Favoriten hinzufügen"
- Oder über das Stern-Symbol

### Stream aus Verlauf abspielen
1. "Verlauf" im Hauptmenü wählen
2. Stream auswählen (Return-Taste oder Kontextmenü)
3. Stream wird abgespielt

---

## Suche

### Suchfunktion nutzen
1. "🔍 Suche" im Hauptmenü wählen
2. Suchbegriff eingeben (z.B. "Mashup", "Techno")
3. Ergebnisse werden als Liste angezeigt
4. Gewünschten Stream auswählen und abspielen

### Suchtipps
- Suche funktioniert nach: Name, Genre, Domain
- Groß-/Kleinschreibung egal
- Teilsuche möglich ("Pop" findet "Pop, Rock, Hits")

---

## Backup & Wiederherstellung

### ZIP-Backup erstellen
1. "💾 ZIP Backup" wählen
2. Dateien auswählen (mehrere möglich)
3. Namen eingeben (.zip nicht vergessen)
4. Tag/Kategorie vergeben (optional)
5. Backup wird im Backup-Ordner gespeichert

### VIP-Snapshot
1. "⭐ VIP Snapshot" wählen
2. Automatische Sicherung von:
   - Favoriten
   - Verlauf
   - Playcounts
3. Wird im Backup-Ordner als "VIP_SNAPSHOT_*.zip" gespeichert

### Backup-Galerie
1. "📁 Backup-Galerie" wählen
2. Alle Backups werden angezeigt
3. Optionen pro Backup:
   - "ZIP wiederherstellen" - Dateien zurückkopieren
   - "Tag bearbeiten" - Kategorie ändern
   - "Bild zuweisen" - Icon setzen
   - "Datei löschen" - Backup löschen

### Undo-Restore (Gelöschte Dateien retten)
1. "↩ Undo Restore" wählen
2. Liste der .bak_ Dateien wird angezeigt
3. Gewünschte Sicherung auswählen
4. Wiederherstellung bestätigen
5. Original-Datei wird überschrieben

### Backup-Ordner
Standard-Pfad: `userdata/addon_data/plugin.audio.sKullsRadioSuite/Backups`

---

## Tools

### Stream Health-Check
- Prüft alle Streams auf Verfügbarkeit
- Zeigt Online/Offline-Status
- Speichert Bericht in userdata/addon_data/

### Playcount-Statistik
- Zeigt meistgespielte Streams
- Anzahl der Wiedergaben pro Stream

### Zuletzt hinzugefügt
- Streams anzeigen, die seit dem letzten Besuch hinzugefügt wurden

### Fehlende Icons
- Prüft, ob alle Stream-Icons vorhanden sind

### JSON/ZIP-Diagnose
- Überprüft Integrität der JSON-Dateien
- Repariert defekte ZIP-Dateien

---

## Cloud-Sync

### Einrichtung
1. Einstellungen öffnen
2. "Cloud Features" aktivieren
3. Cloud-Anbieter wählen (Google Drive / Dropbox)
4. Zugangsdaten eingeben

### Auto-Sync
- Intervall einstellbar (stündlich/täglich/weekly)
- Automatisches Hochladen von Backups
- Automatisches Herunterladen fehlender Dateien

### Verschlüsselung
- AES-256 Verschlüsselung für sensible Daten
- Optional: Cloud-Upload nur verschlüsselt

---

## Tipps & Tricks

### Tastenkombinationen
- **Return** - Stream abspielen (aus Liste)
- **Kontextmenü** - Zusatzoptionen anzeigen
- **Back** - Zurück zum vorherigen Menü

### Backup-Strategie
1. Regelmäßige VIP-Snapshots erstellen
2. Vor größeren Änderungen manuelles Backup
3. Wichtige Backups als "VIP-Release" taggen

### Performance
- Health-Check kann bei vielen Streams länger dauern
- Cloud-Sync nur bei Bedarf aktivieren
- Filter nutzen um Listen zu verkleinern

### Fehlerbehebung
- Stream startet nicht: Health-Check prüfen
- Suche zeigt keine Ergebnisse: Weniger spezifisch suchen
- Backup-Fehler: Diagnose-Tool nutzen

---

## Einstellungen

### Wichtige Optionen
- `backup_folder` - Speicherort für Backups
- `enable_cloud_features` - Cloud-Sync aktivieren
- `sync_interval` - Auto-Sync Zeitintervall
- `encryption_enabled` - AES-256 Verschlüsselung

### Einstellungen öffnen
- Über das Hauptmenü oder Kodi-Einstellungen

---

## Version-History

- **3.2.1** - Fix: Suche und Verlauf jetzt abspielbar, Backup-Ordner in userdata
- **3.2.0** - Multi-User und Night-Mode entfernt (Kodi-Profile verwenden)
- **3.1.1** - Neu: About-Tab in Einstellungen
- **3.1.0** - Phoenix Update (UI-Overhaul)

---

## Support

Bei Fragen oder Problemen:
- Kodi-Logdateien prüfen (unter `kodi.log`)
- Health-Check und Diagnose-Tools nutzen
- Backup vor Änderungen erstellen

---

**Viel Spaß mit sKulls Radio Suite!**