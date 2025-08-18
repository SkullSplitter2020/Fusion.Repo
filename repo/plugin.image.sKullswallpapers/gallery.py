import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import shutil
import zipfile
import urllib.parse
from debug_helper import debug_log

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
download_dir = xbmcvfs.translatePath(addon.getSetting('remote_path'))
icon = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/icon.png')
fanart = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/fanart.jpg')
resource_images_dir = xbmcvfs.translatePath('special://home/addons/resource.images.sKullswallpaper/')

def add_dir(name, url, mode, icon, fanart, is_folder, context_menu=None):
    li = xbmcgui.ListItem(label=name)
    li.setArt({'thumb': icon, 'icon': icon, 'fanart': fanart})
    li.setInfo(type='pictures', infoLabels={"Title": name})
    if context_menu:
        li.addContextMenuItems(context_menu)
    u = sys.argv[0] + "?mode=%d&param=%s&name=%s" % (
        mode, urllib.parse.quote_plus(url), urllib.parse.quote_plus(name))
    xbmcplugin.addDirectoryItem(addon_handle, u, li, is_folder)

def list_gallery():
    try:
        if not os.path.exists(dl_dir):
            xbmcgui.Dialog().ok("Fehler", f"Download-Ordner nicht gefunden:\n{dl_dir}")
            xbmcplugin.endOfDirectory(addon_handle)
            return
        dirs = [d for d in os.listdir(dl_dir) if os.path.isdir(os.path.join(dl_dir, d))]
        if not dirs:
            xbmcgui.Dialog().ok("Galerie leer", "Noch keine Wallpaper-Genres als lokale Ordner gefunden!")
            xbmcplugin.endOfDirectory(addon_handle)
            return
        for genre in dirs:
            abs_genre_path = os.path.join(dl_dir, genre)
            add_dir(f'[B]{genre}[/B]', abs_genre_path, mode=200, icon=icon, fanart=fanart, is_folder=True)
        xbmcplugin.endOfDirectory(addon_handle)
    except Exception as e:
        xbmcgui.Dialog().ok("Fehler", f"Fehler in Galerie: {e}")
        xbmcplugin.endOfDirectory(addon_handle)
        
def list_images_in_genre(genre_path):
    folder_name = os.path.basename(genre_path)
    xbmcplugin.setPluginCategory(addon_handle, f"Galerie - {folder_name}")
    if not os.path.exists(genre_path):
        xbmcgui.Dialog().ok("Fehler", f"Ordner nicht gefunden:\n{genre_path}")
        return
    all_images = [img for img in os.listdir(genre_path) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
    for fname in all_images:
        img_path = os.path.join(genre_path, fname)
        context_menu = [
            ('[B]Als Hintergrund setzen[/B]', f'RunPlugin({sys.argv[0]}?mode=210&img={img_path})'),
            ('[B]Löschen[/B]', f'RunPlugin({sys.argv[0]}?mode=211&img={img_path}&genre={folder_name})'),
            ('[B]Verschieben[/B]', f'RunPlugin({sys.argv[0]}?mode=212&img={img_path}&genre={folder_name})'),
            ('[B]Umbenennen[/B]', f'RunPlugin({sys.argv[0]}?mode=213&img={img_path}&genre={folder_name})'),
            ('[B]Zu resource.images.sKullswallpaper[/B]', f'RunPlugin({sys.argv[0]}?mode=214&img={img_path})'),
            ('[B]Als Favorit speichern[/B]', f'RunPlugin({sys.argv[0]}?mode=215&img={img_path})')
        ]
        li = xbmcgui.ListItem(label=fname)
        li.setArt({'thumb': img_path, 'icon': img_path, 'fanart': img_path})
        li.setInfo(type='pictures', infoLabels={"Title": fname})
        li.addContextMenuItems(context_menu)
        u = sys.argv[0] + f"?mode=201&img={urllib.parse.quote_plus(img_path)}&genre={urllib.parse.quote_plus(folder_name)}"
        xbmcplugin.addDirectoryItem(addon_handle, u, li, False)
    xbmcplugin.endOfDirectory(addon_handle)

def set_wallpaper(img_path):
    xbmc.executebuiltin(f"Skin.SetString(CustomWallpaper,{img_path})")
    xbmcgui.Dialog().ok("Wallpaper", "Bild wurde als Hintergrund gesetzt.")

def delete_image(img_path, genre):
    ok = xbmcgui.Dialog().yesno("Bild löschen", f"Wirklich löschen?\n{img_path}")
    if ok and xbmcvfs.exists(img_path):
        xbmcvfs.delete(img_path)
        xbmcgui.Dialog().notification("Löschen", "Bild gelöscht.", xbmcgui.NOTIFICATION_INFO)
        xbmc.executebuiltin('Container.Refresh')

def move_image(img_path, current_genre):
    dirs = [d for d in os.listdir(download_dir) if os.path.isdir(os.path.join(download_dir, d)) and d != current_genre]
    sel = xbmcgui.Dialog().select("Zielordner wählen:", dirs)
    if sel == -1:
        return
    new_genre = dirs[sel]
    dest_path = os.path.join(download_dir, new_genre, os.path.basename(img_path))
    shutil.move(img_path, dest_path)
    xbmcgui.Dialog().notification("Verschieben", f"Bild verschoben nach {new_genre}", xbmcgui.NOTIFICATION_INFO)
    xbmc.executebuiltin('Container.Refresh')

def rename_image(img_path, genre):
    new_name = xbmcgui.Dialog().input("Neuer Dateiname:", defaultt=os.path.basename(img_path))
    if new_name:
        dest_path = os.path.join(download_dir, genre, new_name)
        os.rename(img_path, dest_path)
        xbmcgui.Dialog().notification("Umbenennen", "Bild umbenannt.", xbmcgui.NOTIFICATION_INFO)
        xbmc.executebuiltin('Container.Refresh')

def copy_to_resource_images(img_path):
    if not xbmcvfs.exists(resource_images_dir):
        xbmcvfs.mkdirs(resource_images_dir)
    dest_path = os.path.join(resource_images_dir, os.path.basename(img_path))
    shutil.copy(img_path, dest_path)
    xbmcgui.Dialog().ok("resource.images.sKullswallpaper", "Bild ins Gallery-Addon kopiert.")

def save_as_favorite_img(img_path):
    favs = addon.getSetting('gallery_favorites')
    favs = favs.split('|') if favs else []
    if img_path not in favs:
        favs.append(img_path)
        addon.setSetting('gallery_favorites', '|'.join(favs))
        xbmcgui.Dialog().ok("Favorit", "Bild gespeichert.")
    else:
        xbmcgui.Dialog().ok("Favorit", "Bild ist schon Favorit.")

def gallery_context_router(mode, params):
    img = params.get('img')
    genre = params.get('genre')
    if mode == 210 and img:
        set_wallpaper(img)
    elif mode == 211 and img and genre:
        delete_image(img, genre)
    elif mode == 212 and img and genre:
        move_image(img, genre)
    elif mode == 213 and img and genre:
        rename_image(img, genre)
    elif mode == 214 and img:
        copy_to_resource_images(img)
    elif mode == 215 and img:
        save_as_favorite_img(img)
    elif mode == 220 and genre:
        from batchzip import zip_export_genre
        zip_export_genre(genre)
    elif mode == 221 and genre:
        from batchzip import start_slideshow
        start_slideshow(genre)