import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib.request
import urllib.parse
import json
from gallery import list_gallery, list_images_in_genre, gallery_context_router
from wallpaperonline import list_main_menu, list_images, wallpaper_context_router
from favorites import show_favorites, add_favorite, remove_favorite
from batchzip import zip_export_genre, start_slideshow
from adult import edit_adult_keywords, edit_active_genres
from debug_helper import debug_log

AddonID = 'plugin.image.sKullswallpapers'
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
icon = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/icon.png')
fanart = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/fanart.jpg')
settings_xml = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/resources/settings.xml')

def get_params():
    params = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        paramstring = sys.argv[2].replace('?', '')
        for part in paramstring.split('&'):
            if '=' in part:
                k, v = part.split('=', 1)
                params[k] = urllib.parse.unquote_plus(v)
    return params

params = get_params()
mode   = int(params.get('mode', 0))
param  = params.get('param')
img    = params.get('img')
genre  = params.get('genre')
name   = params.get('name')

# -- PIN-Setup (verschleiert im settings.xml: <setting id="adult_pin" ... option="hidden" ... />)
def force_pin_setup():
    pin = addon.getSetting('adult_pin')
    if not pin:
        addon.setSetting('adult_pin','0000')
        pin = '0000'
    if pin == '0000':
        while True:
            new_pin = xbmcgui.Dialog().numeric(0, "Bitte neuen PIN setzen (mind. 4 Ziffern, nicht 0000):")
            if new_pin and len(new_pin)>=4 and new_pin != '0000':
                addon.setSetting('adult_pin',new_pin)
                xbmcgui.Dialog().ok("PIN gespeichert","Dein neuer PIN ist gesetzt!")
                break
            xbmcgui.Dialog().ok("Fehler","PIN muss mind. 4stellig und ungleich '0000' sein!")
force_pin_setup()

# ------------------- MODES ROUTER -----------------------
if mode == 0:
    list_main_menu()
elif mode == 9999:
    list_gallery()
elif mode == 200 and param:
    list_images_in_genre(param)
elif mode in (201,210,211,212,213,214,215,220,221):
    gallery_context_router(mode, params)
elif mode == 1 and param and name:
    list_images(param, name)
elif mode in (2,3,4,5,50,51,52,53,55):
    wallpaper_context_router(mode, params)
elif mode == 888:
    show_favorites()
elif mode == 10:
    edit_adult_keywords()
elif mode == 20:
    edit_active_genres()
elif mode == 1000:
    # Quellen hinzufügen (GUI)
    from wallpaperonline import add_extra_url
    add_extra_url()
elif mode == 1001:
    # Quellen verwalten (GUI)
    from wallpaperonline import manage_extra_urls
    manage_extra_urls()
elif mode == 2000:
    from wallpaperonline import show_community_sources
    show_community_sources()
else:
    list_main_menu()