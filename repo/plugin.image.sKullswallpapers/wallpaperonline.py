import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib.request
import urllib.parse
import random
import json
from bs4 import BeautifulSoup as bs
from debug_helper import debug_log
import downloader

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
icon = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/icon.png')
fanart = xbmcvfs.translatePath('special://home/addons/plugin.image.sKullswallpapers/fanart.jpg')
download_dir = xbmcvfs.translatePath(addon.getSetting('remote_path'))

addon = xbmcaddon.Addon()

def get_extra_urls():
    urls = []
    i = 1
    while True:
        val = addon.getSetting(f"extra_url_{i}")
        if val:
            urls.append(val.strip())
            i += 1
        else:
            break
    return urls

def open_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0','Connection': 'keep-alive'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def get_genre_dirs():
    archive_urls = [addon.getSetting('archive_org_url').strip()] + get_extra_urls()
    custom_genres = [g.strip() for g in addon.getSetting('genres').split(',') if g.strip()]
    adult_keywords = [w.strip().lower() for w in addon.getSetting('adult_keywords').split(',') if w.strip()]
    raw = addon.getSetting('show_adult')
    show_adult = raw.lower() in ('true','1','ja','yes')
    genres = []
    for org_url in archive_urls:
        if not org_url.endswith('/'):
            org_url += '/'
        try:
            html = open_url(org_url).decode('utf-8', errors='replace')
            soup = bs(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.endswith('/') and not href.startswith('../'):
                    name = href.strip('/').replace('%20', ' ')
                    is_adult = any([k in name.lower() for k in adult_keywords])
                    xbmc.log(f"DBG | GENRE={name}   is_adult={is_adult}   show_adult={show_adult}", xbmc.LOGWARNING)
                    if is_adult and not show_adult:
                        continue
                    genres.append((name, org_url + href, is_adult))
        except Exception as e:
            xbmc.log(f"Fehler beim Laden der Quelle {org_url}: {e}", xbmc.LOGWARNING)
    return genres
        
def open_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0','Connection': 'keep-alive'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def add_dir(name, url, mode, icon, fanart, is_folder, context_menu=None):
    li = xbmcgui.ListItem(label=name)
    li.setArt({'thumb': icon, 'icon': icon, 'fanart': fanart})
    li.setInfo(type='pictures', infoLabels={"Title": name})
    if context_menu:
        li.addContextMenuItems(context_menu)
    u = sys.argv[0] + "?mode=%d&param=%s&name=%s" % (
        mode, urllib.parse.quote_plus(url), urllib.parse.quote_plus(name))
    xbmcplugin.addDirectoryItem(addon_handle, u, li, is_folder)

def list_main_menu():
    add_dir('[B][COLOR gold]Meine Galerie[/COLOR][/B]', '', mode=9999, icon=icon, fanart=fanart, is_folder=True)
    add_dir('[B][COLOR orange]Favoriten[/COLOR][/B]', '', mode=888, icon=icon, fanart=fanart, is_folder=True)
    add_dir('[B][COLOR deepskyblue]Community-Quellen[/COLOR][/B]', '', mode=2000, icon=icon, fanart=fanart, is_folder=True)
    for name, genre_url, is_adult in get_genre_dirs():
        display_name = name
        if is_adult:
            display_name += ' [ADULT]'
        add_dir(display_name, genre_url, mode=1, icon=icon, fanart=fanart, is_folder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_images(genre_url, genre_name):
    html = open_url(genre_url).decode('utf-8', errors='replace')
    soup = bs(html, 'html.parser')
    adult_keywords = [w.strip().lower() for w in addon.getSetting('adult_keywords').split(',') if w.strip()]
    is_adult = any([k in genre_name.lower() for k in adult_keywords])
    if is_adult and not pin_prompt("PIN für Adult-Genre:"):
        xbmcgui.Dialog().ok("PIN falsch", "Zugriff verweigert.")
        xbmcplugin.endOfDirectory(addon_handle)
        return
    imgs = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if any(href.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            fname = href.replace('%20', ' ')
            img_url = genre_url + href
            imgs.append((img_url, fname))
    filtered_imgs = [item for item in imgs if True]
    for img_url, fname in filtered_imgs:
        fav_key = f"{img_url}#{genre_name}#{fname}"
        context_menu = [
            ('[B]Download[/B]', f'RunPlugin({sys.argv[0]}?mode=2&param={urllib.parse.quote_plus(img_url + "|" + genre_name)}&name={urllib.parse.quote_plus(fname)})'),
            ('[B]Löschen[/B]', f'RunPlugin({sys.argv[0]}?mode=3&param={urllib.parse.quote_plus(fname + "|" + genre_name)})'),
            ('[B]Verschieben[/B]', f'RunPlugin({sys.argv[0]}?mode=4&param={urllib.parse.quote_plus(fname + "|" + genre_name)})'),
            ('[B]Bildinfo[/B]', f'RunPlugin({sys.argv[0]}?mode=5&param={urllib.parse.quote_plus(img_url)}&name={urllib.parse.quote_plus(fname)})'),
            ('[B]Zu Favoriten[/B]', f'RunPlugin({sys.argv[0]}?mode=50&param={urllib.parse.quote_plus(fav_key)})'),
            ('[B]Favorit entfernen[/B]', f'RunPlugin({sys.argv[0]}?mode=51&param={urllib.parse.quote_plus(fav_key)})'),
            ('[B]Als Hintergrund setzen[/B]', f'RunPlugin({sys.argv[0]}?mode=52&param={urllib.parse.quote_plus(img_url)})'),
            ('[B]Teilen/Upload (Demo)[/B]', f'RunPlugin({sys.argv[0]}?mode=53&param={urllib.parse.quote_plus(img_url + "|" + fname)})')
        ]
        li = xbmcgui.ListItem(label=fname)
        li.setArt({'thumb': img_url, 'icon': img_url, 'fanart': fanart})
        li.setInfo(type='pictures', infoLabels={"Title": fname})
        li.addContextMenuItems(context_menu)
        u = sys.argv[0] + f"?mode=2&param={urllib.parse.quote_plus(img_url + '|' + genre_name)}&name={urllib.parse.quote_plus(fname)}"
        xbmcplugin.addDirectoryItem(addon_handle, u, li, False)
    if filtered_imgs:
        rand_img_url, rand_fname = random.choice(filtered_imgs)
        add_dir('[B][COLOR lightblue]Zufälliges Bild anzeigen[/COLOR][/B]', rand_img_url + "|" + genre_name,
                mode=5, icon=rand_img_url, fanart=fanart, is_folder=False)
    if filtered_imgs:
        add_dir('[B][COLOR green]Alle in diesem Genre herunterladen[/COLOR][/B]', genre_url + "|" + genre_name,
                mode=55, icon=icon, fanart=fanart, is_folder=False)
    xbmcplugin.endOfDirectory(addon_handle)

def pin_prompt(msg="Für diese Aktion ist ein PIN erforderlich."):
    pin = addon.getSetting('adult_pin')
    entered = xbmcgui.Dialog().numeric(0, msg)
    return entered == pin

def download_image(param):
    img_url, genre = param.split('|', 1)
    genre = genre.replace(' ', '_')
    save_name = os.path.basename(urllib.parse.urlparse(img_url).path)
    genre_folder = os.path.join(download_dir, genre)
    if not xbmcvfs.exists(genre_folder):
        xbmcvfs.mkdirs(genre_folder)
    dest = os.path.join(genre_folder, save_name)
    dp = xbmcgui.DialogProgress()
    dp.create("Download", f"Lade {save_name} nach {genre}")
    try:
        downloader.download(img_url, dest, dp)
        xbmcgui.Dialog().ok('Fertig', f'Bild gespeichert als:\n{dest}')
    except Exception as e:
        xbmcgui.Dialog().ok("Fehler beim Download", str(e))

def delete_image(param):
    fname, genre = param.split('|', 1)
    genre = genre.replace(' ', '_')
    file_path = os.path.join(download_dir, genre, fname)
    if xbmcvfs.exists(file_path):
        ok = xbmcgui.Dialog().yesno("Bild löschen", f"Wirklich löschen?\n{file_path}")
        if ok:
            xbmcvfs.delete(file_path)
            xbmcgui.Dialog().notification("Löschen", "Bild gelöscht.", xbmcgui.NOTIFICATION_INFO, 2500)
    else:
        xbmcgui.Dialog().notification("Löschen", "Datei nicht gefunden!", xbmcgui.NOTIFICATION_ERROR, 2500)

def move_image(param):
    fname, genre = param.split('|', 1)
    old_path = os.path.join(download_dir, genre.replace(' ', '_'), fname)
    dirs = [d for d in os.listdir(download_dir) if os.path.isdir(os.path.join(download_dir, d))]
    if not dirs:
        xbmcgui.Dialog().ok("Verschieben", "Keine Zielordner vorhanden!")
        return
    sel = xbmcgui.Dialog().select("Zielordner wählen:", dirs)
    if sel == -1:
        return
    new_genre = dirs[sel]
    new_path = os.path.join(download_dir, new_genre, fname)
    if xbmcvfs.exists(old_path):
        xbmcvfs.copy(old_path, new_path)
        xbmcvfs.delete(old_path)
        xbmcgui.Dialog().notification("Verschieben", f"Bild verschoben nach {new_genre}", xbmcgui.NOTIFICATION_INFO, 2500)
    else:
        xbmcgui.Dialog().ok("Fehler", "Datei nicht gefunden!")

def show_image_info(param, name):
    xbmcgui.Dialog().textviewer("Bildinfo", f"Name: {name}\nQuelle: {param}")

def set_as_background(param):
    xbmc.executebuiltin(f"Skin.SetString(CustomWallpaper,{param})")
    xbmcgui.Dialog().ok("Wallpaper", "Bild als Hintergrund gesetzt!")

def share_image(param):
    img_url, fname = param.split('|', 1)
    xbmcgui.Dialog().ok("Community-Feature (Demo)", f"Bild '{fname}' könnte an einen Server geteilt werden.")

def download_all_images(param):
    genre_url, genre_name = param.split('|', 1)
    html = open_url(genre_url).decode('utf-8', errors='replace')
    soup = bs(html, 'html.parser')
    imgs = [(a['href'].replace('%20', ' '), genre_url + a['href']) for a in soup.find_all('a', href=True)
            if any(a['href'].lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
    dp = xbmcgui.DialogProgress()
    dp.create("Batch-Download", "Lade alle Bilder...")
    total = len(imgs)
    for idx, (fname, img_url) in enumerate(imgs):
        genre_folder = os.path.join(download_dir, genre_name.replace(' ', '_'))
        if not xbmcvfs.exists(genre_folder):
            xbmcvfs.mkdirs(genre_folder)
        dest = os.path.join(genre_folder, os.path.basename(fname))
        dp.update(int((idx+1)/total*100), f"Lade {fname}  ({idx+1}/{total})")
        try:
            downloader.download(img_url, dest, dp)
        except Exception as e:
            xbmc.log(f"Fehler bei {img_url}: {e}", xbmc.LOGERROR)
        if dp.iscanceled():
            break
    dp.close()
    xbmcgui.Dialog().ok('Fertig', f'{total} Bilder gespeichert in: {genre_folder}')

def add_extra_url():
    new_url = xbmcgui.Dialog().input("URL hinzufügen (z.B. https://archive.org/...):")
    if new_url and new_url.startswith('http'):
        urls = get_extra_urls()
        if new_url in urls:
            xbmcgui.Dialog().ok("Schon vorhanden", "Diese Quelle ist schon eingetragen.")
            return
        nextidx = len(urls)+1
        addon.setSetting(f"extra_url_{nextidx}", new_url)
        xbmcgui.Dialog().ok("Gespeichert", "Die neue Quelle wurde hinzugefügt.")
    else:
        xbmcgui.Dialog().ok("Fehler", "Keine gültige URL.")

def manage_extra_urls():
    urls = get_extra_urls()
    if not urls:
        xbmcgui.Dialog().ok("Keine weiteren Quellen!", "")
        return
    idx = xbmcgui.Dialog().select("Quelle löschen", urls)
    if idx==-1:
        return
    if not xbmcgui.Dialog().yesno("Löschen", f"Wirklich diese Quelle entfernen?\n{urls[idx]}"):
        return
    for i in range(idx+1, len(urls)):
        addon.setSetting(f"extra_url_{i}", urls[i])
    addon.setSetting(f"extra_url_{len(urls)}","")
    xbmcgui.Dialog().ok("Quelle gelöscht", "Die Quelle wurde entfernt.")

def show_community_sources():
    url = 'https://raw.githubusercontent.com/skulls-wallpaper/community-wallpapersources/main/sources.json'
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            sources = json.loads(data)
    except Exception as e:
        xbmcgui.Dialog().ok("Fehler beim Laden der Community-Quellen", str(e))
        debug_log(f"Community-Import Error: {str(e)}")
        return
    labels = [f"{src['name']} — {src.get('description','')}" for src in sources]
    sel = xbmcgui.Dialog().select("Community-Quellen", labels)
    if sel == -1:
        return
    community_url = sources[sel]['url']
    existing = get_extra_urls()
    if community_url in existing:
        xbmcgui.Dialog().ok("Quelle schon vorhanden", "Die gewählte Quelle ist bereits in deiner Liste.")
        return
    nextidx = len(existing) + 1
    addon.setSetting(f"extra_url_{nextidx}", community_url)
    xbmcgui.Dialog().ok("Übernommen!", "Community-Quelle gespeichert.")

def wallpaper_context_router(mode, params):
    if mode == 2 and 'param' in params and 'name' in params:
        download_image(params['param'])
    elif mode == 3 and 'param' in params:
        delete_image(params['param'])
    elif mode == 4 and 'param' in params:
        move_image(params['param'])
    elif mode == 5 and 'param' in params and 'name' in params:
        show_image_info(params['param'], params['name'])
    elif mode == 50 and 'param' in params:
        from favorites import add_favorite
        add_favorite(params['param'])
    elif mode == 51 and 'param' in params:
        from favorites import remove_favorite
        remove_favorite(params['param'])
    elif mode == 52 and 'param' in params:
        set_as_background(params['param'].split('|', 1)[0])
    elif mode == 53 and 'param' in params:
        share_image(params['param'])
    elif mode == 55 and 'param' in params:
        download_all_images(params['param'])