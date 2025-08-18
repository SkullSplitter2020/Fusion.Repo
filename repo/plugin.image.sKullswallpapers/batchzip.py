import os
import zipfile
import xbmcgui
import xbmc

def zip_export_genre(genre_path):
    folder_name = os.path.basename(genre_path)
    zip_path = xbmcgui.Dialog().browse(3, "Ziel-Ordner wählen", "files", "", False, False)
    if not zip_path:
        return
    zip_file = os.path.join(zip_path, f"{folder_name}.zip")
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as ziph:
            for fname in os.listdir(genre_path):
                lower = fname.lower()
                if lower.endswith(('.jpg','.jpeg','.png','.bmp','.gif')):
                    absfile = os.path.join(genre_path, fname)
                    ziph.write(absfile, fname)
        xbmcgui.Dialog().ok("Exportiert!", f"ZIP wurde gespeichert: {zip_file}")
    except Exception as e:
        xbmcgui.Dialog().ok("Export-Fehler", f"ZIP fehlgeschlagen:\n{str(e)}")

def start_slideshow(genre_path):
    if not os.path.isdir(genre_path):
        xbmcgui.Dialog().ok("Fehler", f"Ordner nicht gefunden: {genre_path}")
        return
    xbmc.executebuiltin(f"RunScript(script.slideshow,{genre_path})")
    xbmcgui.Dialog().ok("Slideshow", "Slideshow gestartet!\nBenutze Kodi-Slideshow-Funktion.")