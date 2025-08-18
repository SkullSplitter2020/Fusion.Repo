import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib.parse

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
icon = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/icon.png')
fanart = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/fanart.jpg')

def add_dir(name, url, mode, icon, fanart, is_folder, context_menu=None):
    li = xbmcgui.ListItem(label=name)
    li.setArt({'thumb': icon, 'icon': icon, 'fanart': fanart})
    li.setInfo(type='pictures', infoLabels={"Title": name})
    if context_menu:
        li.addContextMenuItems(context_menu)
    u = sys.argv[0] + "?mode=%d&param=%s&name=%s" % (
        mode, urllib.parse.quote_plus(url), urllib.parse.quote_plus(name))
    xbmcplugin.addDirectoryItem(addon_handle, u, li, is_folder)

def get_favorites():
    fav = addon.getSetting('favorites')
    return fav.split('|') if fav else []

def save_favorites(favs):
    addon.setSetting('favorites', '|'.join(favs))

def add_favorite(param):
    favs = get_favorites()
    if param not in favs:
        favs.append(param)
        save_favorites(favs)
        xbmcgui.Dialog().notification("Favorit", "Wallpaper als Favorit gespeichert.")

def remove_favorite(param):
    favs = get_favorites()
    if param in favs:
        favs.remove(param)
        save_favorites(favs)
        xbmcgui.Dialog().notification("Favorit", "Wallpaper entfernt.")

def show_favorites():
    favs = get_favorites()
    if not favs:
        xbmcgui.Dialog().ok("Keine Favoriten", "Noch keine Wallpaper als Favorit markiert.")
        xbmcplugin.endOfDirectory(addon_handle)
        return
    for fav in favs:
        # Erwarte Format: "img_url#genre#fname"
        if '#' in fav:
            try:
                img_url, genre, fname = fav.split('#', 2)
            except Exception:
                continue
            context_menu = [
                ('[B]Löschen[/B]', f'RunPlugin({sys.argv[0]}?mode=51&param={urllib.parse.quote_plus(fav)})'),
                ('[B]Download[/B]', f'RunPlugin({sys.argv[0]}?mode=2&param={urllib.parse.quote_plus(img_url + "|" + genre)}&name={urllib.parse.quote_plus(fname)})')
            ]
            li = xbmcgui.ListItem(label=fname)
            li.setArt({'thumb': img_url, 'icon': img_url, 'fanart': fanart})
            li.setInfo(type='pictures', infoLabels={"Title": fname})
            li.addContextMenuItems(context_menu)
            u = sys.argv[0] + "?mode=2&param=%s&name=%s" % (
                urllib.parse.quote_plus(img_url + "|" + genre),
                urllib.parse.quote_plus(fname))
            xbmcplugin.addDirectoryItem(addon_handle, u, li, False)
    xbmcplugin.endOfDirectory(addon_handle)