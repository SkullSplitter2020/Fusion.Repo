import xbmcaddon
import xbmcgui
import urllib.request
from bs4 import BeautifulSoup as bs

addon = xbmcaddon.Addon()

def pin_prompt(msg="Für diese Aktion ist ein PIN erforderlich."):
    pin = addon.getSetting('adult_pin')
    if not pin:
        xbmcgui.Dialog().ok("Kein PIN", "Bitte zuerst einen Adult-PIN setzen.")
        return False
    entered = xbmcgui.Dialog().numeric(0, msg)
    return entered == pin

def open_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0','Connection': 'keep-alive'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def edit_adult_keywords():
    if not pin_prompt("PIN zum Bearbeiten der Filterwörter eingeben:"):
        xbmcgui.Dialog().ok("Falscher PIN", "Keine Änderung möglich.")
        return
    ak = addon.getSetting('adult_keywords')
    new_value = xbmcgui.Dialog().input("Adult-Filter-Wörter (mit Kommas)", defaultt=ak if ak else "")
    if new_value is not None:
        addon.setSetting('adult_keywords', new_value)
        xbmcgui.Dialog().ok("Gespeichert!", "Adult-Filter/Keywords aktualisiert.")

def edit_active_genres():
    archive_urls = [addon.getSetting('archive_org_url').strip()]
    i = 1
    while True:
        val = addon.getSetting(f"extra_url_{i}")
        if val:
            archive_urls.append(val.strip())
            i += 1
        else:
            break
    all_genres_set = set()
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
                    all_genres_set.add(name)
        except Exception:
            continue
    all_genres = sorted(list(all_genres_set))
    prev_selected = [g.strip() for g in addon.getSetting('genres').split(',') if g.strip()]
    selected = [g in prev_selected for g in all_genres]
    preselect_idx = [i for i, v in enumerate(selected) if v]
    ret = xbmcgui.Dialog().multiselect("Aktive Genres wählen", all_genres, preselect=preselect_idx)
    if ret is not None:
        selected_names = [all_genres[i] for i in ret]
        addon.setSetting('genres', ','.join(selected_names))
        xbmcgui.Dialog().ok("Gespeichert!", f"{len(selected_names)} Genres gespeichert.")