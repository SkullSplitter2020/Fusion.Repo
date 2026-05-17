# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import time
from datetime import datetime, timedelta
import requests
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .provider import Client


HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
FAVORIT_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_MYSPASS.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_BUILD						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2])
BASE_URL							= 'https://www.myspass.de/'
API_VANILLA						= 'https://cms-myspass.vanilla-ott.com/api'
VANILLA_TOKEN				= '9a9c6eb82dd157aeaaaa62c3ac592ca5b9611f1bb2984396c1d62f9c73cccb312018f7ac45280fde34f7d4f171b0a4812cf2d9b41f83206e76bd4c6b417ced1dc577f408facfcad2674f9af9ccff6d964383942c12049e892f99229835b45f4a08dcffdef678d4840dad881ecd6ddf5389565555e89382b05091fc9365a4ff26 reraeB'
traversing							= Client(Client.CONFIG_MYSPASS)

xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

def py3_dec(d, nom='utf-8', ign='ignore'):
	if isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return addon.getLocalizedString(id)

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=xbmc.LOGINFO):
	return xbmc.log(f"[{addon_id} v.{addon_version}]{str(msg)}", level)

def build_mass(body):
	return f"{HOST_AND_PATH}?{urlencode(body)}"

def get_userAgent(REV='149.0', VER='149.0'):
	base = f"Mozilla/5.0 {{}} Gecko/20100101 Firefox/{VER}"
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format(f"(X11; Linux arm64; rv:{REV})") # ARM based Linux
		return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format(f"(Windows NT 10.0; Win64; x64; rv:{REV})") # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format(f"(Macintosh; Intel Mac OS X 10.15; rv:{REV})") # Mac OSX
	return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux

def _header(REFERRER=None, USERTOKEN=None):
	header = {} # !!! Accept-Language only set if browser should offer these languages !!!
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = '*/*'
	header['Content-Type'] = 'application/json; charset=utf-8'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	header['Origin'] = BASE_URL[:-1]
	if REFERRER: header['Referer'] = REFERRER
	if USERTOKEN: header['Authorization'] = USERTOKEN[::-1]
	return header

def getContent(url, method='GET', queries='JSON', REF=BASE_URL, AUTH=None, headers={}, redirects=True, verify=True, data=None, json=None, timeout=30):
	ANSWER, simple = None, requests.Session()
	try:
		response = simple.request(method, url, headers=_header(REF, AUTH), allow_redirects=redirects, verify=verify, data=data, json=json, timeout=timeout)
		response.raise_for_status()
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
		debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, AUTH)} ===")
	except Exception as exc: # No JSON object could be decoded
		failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
		return sys.exit(0)
	debug_MS("═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═ ═")
	return ANSWER

def plugin_operate(MARKING):
	check_uno = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{{"addonid":"{MARKING}","properties":["enabled"]}}}}')
	answer_uno, answer_due = json.loads(check_uno), json.loads(f'{{"error": "{MARKING} NOT FOUND"}}')
	if not "error" in answer_uno.keys() and answer_uno.get('result', '') and answer_uno['result'].get('addon', {}).get('enabled', False) is False:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{MARKING}","enabled":true}}}}')
			failing(f"(common.plugin_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
		del answer_due
		check_due = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{{"addonid":"{MARKING}","properties":["enabled"]}}}}')
		answer_due = json.loads(check_due)
	if (answer_uno.get('result', '') and answer_uno['result'].get('addon', {}).get('enabled', False) is True) or (answer_due.get('result', '') and answer_due['result'].get('addon', {}).get('enabled', False) is True):
		return True
	if answer_due.get('result', '') and answer_due['result'].get('addon', {}).get('enabled', False) is False:
		dialog.ok(addon_id, translation(30501).format(MARKING))
		failing(f"(common.plugin_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT aktiviert !!! #####\n##### Eine automatische Aktivierung ist leider NICHT möglich !!! #####")
	if "error" in answer_uno.keys() or "error" in answer_due.keys():
		dialog.ok(addon_id, translation(30502).format(MARKING))
		failing(f"(common.plugin_operate) ERROR - INSTALLED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT installiert !!! #####")
	return False

def get_sorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_EPISODE, xbmcplugin.SORT_METHOD_DATE]

def get_Description(info):
	if info.get('long_description', '') and len(info['long_description']) > 10:
		return cleaning(info['long_description'])
	elif info.get('medium_description', '') and len(info['medium_description']) > 10:
		return cleaning(info['medium_description'])
	elif info.get('short_description', '') and len(info['short_description']) > 10:
		return cleaning(info['short_description'])
	return ""

def preserve(storage, content=None):
	if content is not None:
		with open(storage, 'w') as topics:
			json.dump(content, topics, indent=2, sort_keys=True)
	else:
		with open(storage, 'r') as topics:
			arrive = json.load(topics)
		return arrive

def clear_umlaut(changes):
	if changes is not None:
		for cm in (('Ä', 'Ae'), ('ä', 'ae'), ('Ö', 'Oe'), ('ö', 'oe'), ('Ü', 'Ue'), ('ü', 'ue'), ('ß', 'ss')):
			changes = changes.replace(*cm)
		changes = changes.strip()
	return changes

def cleaning(text):
	if text is not None:
		for tx in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
			("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
			('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
			('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
			('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
			('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
			('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
			('u00c4', 'Ä'), ('u00e4', 'ä'), ('u00d6', 'Ö'), ('u00f6', 'ö'), ('u00dc', 'Ü'), ('u00fc', 'ü'), ('u00df', 'ß'), ('u00e0', 'à'), ('u00e1', 'á'), ('u00e9', 'é'), # Line = php-Codes clear
			('u00b4', '´'), ('u0060', '`'), ('u201c', '“'), ('u201d', '”'), ('u201e', '„'), ('u201f', '‟'), ('u2013', '-'), ("u2018", "‘"), ("u2019", "’"), # Line = php-Codes clear
			('Ã¤', 'ä'), ('Ã„', 'Ä'), ('Ã¶', 'ö'), ('Ã–', 'Ö'), ('Ã¼', 'ü'), ('Ãœ', 'Ü'), ('ÃŸ', 'ß'), ('â€ž', '„'), ('â€œ', '“'), ('â€™', '’'), ('â€“', '–'), ('Ã¡', 'á'), ('Ã©', 'é'), ('Ã¨', 'è')): # Line = xml-writing-Umlaut clear
			text = text.replace(*tx)
		text = text.strip()
	return text

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_BUILD >= 20 else {}
	if KODI_BUILD >= 20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
	if metadata.get('TvShowTitle', ''):
		if KODI_BUILD >= 20: vinfo.setTvShowTitle(metadata['TvShowTitle'])
		else: vinfo['Tvshowtitle'] = metadata['TvShowTitle']
	description = metadata['Plot'] if metadata.get('Plot') not in ['', 'None', None] else ' '
	if KODI_BUILD >= 20: vinfo.setPlot(description)
	else: vinfo['Plot'] = description
	if str(metadata.get('Duration')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setDuration(int(metadata['Duration']))
		else: vinfo['Duration'] = metadata['Duration']
	if str(metadata.get('Season')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setSeason(int(metadata['Season']))
		else: vinfo['Season'] = metadata['Season']
	if str(metadata.get('Episode')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setEpisode(int(metadata['Episode']))
		else: vinfo['Episode'] = metadata['Episode']
	if metadata.get('Date', ''):
		if KODI_BUILD >= 20: listitem.setDateTime(metadata['Date'])
		else: vinfo['Date'] = metadata['Date']
	if metadata.get('Aired', ''):
		if KODI_BUILD >= 20: vinfo.setFirstAired(metadata['Aired'])
		else: vinfo['Aired'] = metadata['Aired']
	if str(metadata.get('Aired'))[6:10].isdecimal():
		if KODI_BUILD >= 20: vinfo.setYear(int(metadata['Aired'][6:10]))
		else: vinfo['Year'] = metadata['Aired'][6:10]
	if metadata.get('Mediatype', ''):
		if KODI_BUILD >= 20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	if KODI_BUILD >= 20: vinfo.setGenres(['Unterhaltung']), vinfo.setStudios(['myspass.de'])
	else: vinfo['Genre'], vinfo['Studio'] = 'Unterhaltung', 'myspass.de'
	picture, portrait = metadata.get('Image', icon), (metadata.get('Poster', '') or metadata.get('Image', icon))
	listitem.setArt({'icon': icon, 'thumb': picture, 'poster': portrait, 'fanart': defaultFanart})
	if useThumbAsFanart and picture and not artpic in picture:
		listitem.setArt({'fanart': picture})
	if metadata.get('Reference') == 'Single':
		listitem.setProperty('IsPlayable', 'true')
	if KODI_BUILD < 20: listitem.setInfo('Video', vinfo)
	return listitem
