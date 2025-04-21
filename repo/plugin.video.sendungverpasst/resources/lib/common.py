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
import socket
import time
import base64
from datetime import datetime, timedelta
import requests
from urllib.parse import parse_qsl, urlparse, urlencode, quote_plus, unquote_plus
from urllib.request import urlopen
from functools import reduce
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .provider import Client


socket.setdefaulttimeout(30)
HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
SEARCH_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'search_string'))
WORKS_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
FAVORIT_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_SEVER.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
alppic									= os.path.join(addonPath, 'resources', 'media', 'alphabet', '').encode('utf-8').decode('utf-8')
genpic									= os.path.join(addonPath, 'resources', 'media', 'genre', '').encode('utf-8').decode('utf-8')
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
prefSTREAM						= int(addon.getSetting('prefer_stream'))
showCHANFOLD				= addon.getSetting('show_chanFOLD') == 'true'
showCHANLINK				= addon.getSetting('show_chanLINK') == 'true'
showARTE							= (True if addon.getSetting('show_ARTE') == 'true' else False)
showJOYN							= (True if addon.getSetting('show_JOYN') == 'true' else False)
showRTL								= (True if addon.getSetting('show_TVNOW') == 'true' else False)
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
JOYN_staticCODE				= addon.getSetting('joyn_staticCODE')
SEVER_staticCODE				= addon.getSetting('sever_staticCODE')
ARTEEX								= ['ARTE']
JOYNEX								= ['KABEL 1', 'PRO7', 'PRO7 MAXX', 'SAT1', 'SIXX']
RTLEX									= ['N-TV', 'NOW!', 'RTL', 'RTL NITRO', 'RTL2', 'RTLPLUS', 'SUPER RTL', 'VOX']
KODI_ov20							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
IMG_cover							= 'https://sendungen.fra1.cdn.digitaloceanspaces.com/{}'
API_BASE							= 'https://www.sendungverpasst.de/_next/data/' # cl7AR8ToJErdg4wnRFYGT # CODE of the Webpage
API_COMP							= f"https://www.sendungverpasst.de/_next/data/{SEVER_staticCODE}"
BASE_URL							= 'https://www.sendungverpasst.de/'
BASE_JOYN						= 'https://www.joyn.de/'
API_ARD								= 'https://api.ardmediathek.de/page-gateway/pages/'
API_ZDF_OLD						= 'https://api.zdf.de'
API_ZDF_NEW					= 'https://zdf-prod-futura.zdf.de/mediathekV2'
API_JOYN							= 'https://www.joyn.de/_next/data/' # bSD_wV8RvFrdlX8nHD5vh # CODE of the Webpage
traversing							= Client(Client.CONFIG_SEVER)

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

def build_mass(plugin, body):
	return f"{plugin}?{urlencode(body)}"

def get_userAgent(REV='135.0', VER='135.0'):
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

def _header(REFERRER=None, WORD=None, USERTOKEN=None):
	header = {}
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	if REFERRER: header['Referer'] = REFERRER
	if WORD and USERTOKEN:
		header[WORD] = USERTOKEN
	return header

def getContent(url, method='GET', queries='JSON', REF=None, WAY=None, AUTH=None, headers={}, redirects=True, verify=False, data=None, json=None, timeout=30):
	retries, (ANSWER, NEW_CODING) = 0, (None for _ in range(2))
	if url.startswith('http'):
		try:
			response = requests.request(method, url, headers=_header(REF, WAY, AUTH), allow_redirects=redirects, verify=verify, timeout=timeout)
			ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
			debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, WAY, AUTH)} ===")
		except requests.exceptions.RequestException as exc:
			failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
			dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
			return sys.exit(0)
	else:
		def getCollected(suffix_URL, token_TRANSFER=None):
			debug_MS(f"(common.getCollected) === suffix_URL : {suffix_URL} || token_TRANSFER : {token_TRANSFER} ===")
			if url.startswith('JOYN_REDIRECT'):
				recentURL = API_JOYN+token_TRANSFER+suffix_URL.split('@@')[1] if token_TRANSFER else API_JOYN+addon.getSetting('joyn_staticCODE')+suffix_URL.split('@@')[1]
			else:
				recentURL = API_BASE+token_TRANSFER+suffix_URL if token_TRANSFER else API_BASE+addon.getSetting('sever_staticCODE')+suffix_URL
			return recentURL
		while not ANSWER and retries < 3: # 2 x Wiederholungen (gesamt=3) für den URL-Request ::: da der Code für die API_BASE evtl. wieder geändert wurde
			retries += 1
			try:
				endURL = getCollected(url, NEW_CODING)
				response = requests.request(method, endURL, headers=_header(REF, WAY, AUTH), allow_redirects=redirects, verify=verify, timeout=timeout)
				response.raise_for_status()
				VALID_JSON = response.json() if queries == 'JSON' else None
				ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
				debug_MS(f"(common.getContent) === CALLBACK === RETRIES_no : {retries} === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, WAY, AUTH)} ===")
			except Exception as exc: # No JSON object could be decoded
				failing(f"(common.getContent) ERROR - CURRENT_TOKEN - ERROR ##### RETRIES_no : {retries} === URL : {url} === FAILURE : {exc} #####")
				SURVEY, SIMPLEX = f"{BASE_JOYN}mediatheken" if url.startswith('JOYN_REDIRECT') else BASE_URL, BASE_JOYN if url.startswith('JOYN_REDIRECT') else REF
				CONTENT = requests.get(SURVEY, headers=_header(SIMPLEX), allow_redirects=redirects, verify=verify, timeout=10)
				SCAN_REQ = re.compile(r'''</script><script src=["']/_next/static/([^/]+)/_ssgManifest.js["']''', re.S).findall(CONTENT.text)
				#SCAN_REQ = re.compile(r'''["']query["']:.*?,["']buildId["']:["']([^"']+)["'],["']isFallback["']''', re.S).findall(CONTENT.text)
				if SCAN_REQ:
					NEW_CODING = SCAN_REQ[0]
					if url.startswith('JOYN_REDIRECT'): addon.setSetting('joyn_staticCODE', NEW_CODING)
					else: addon.setSetting('sever_staticCODE', NEW_CODING)
				elif retries > 1 and not SCAN_REQ:
					retries += 2
					dialog.notification(translation(30521).format('URL'), translation(30524), icon, 12000)
					break
				time.sleep(2)
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

def get_Sorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_EPISODE, xbmcplugin.SORT_METHOD_DATE]

def preserve(store, action='JSON', data=None):
	if data is not None:
		with open(store, 'w') as topics:
			json.dump(data, topics, indent=2, sort_keys=True) if action == 'JSON' else topics.write(data)
	else:
		with open(store, 'r') as topics:
			arrive = json.load(topics) if action == 'JSON' else topics.read()
		return arrive

def cleanUmlaut(wrong):
	if wrong is not None:
		for wg in (('ä', 'ae'), ('Ä', 'Ae'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'Oe'), ('ß', 'ss')):
			wrong = wrong.replace(*wg)
		wrong = wrong.strip()
	return wrong

def cleaning(text):
	if text is not None:
		for tx in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
			("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
			('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
			('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
			('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
			('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
			('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
			('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
			('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
			('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '), ('\n\r\n\r\n', '\n\r\n'), ('\n\n\n', '\n'),
			("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
			('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ("\\'", "'")):
			text = text.replace(*tx)
		text = text.strip()
	return text

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_ov20 else {}
	if KODI_ov20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
	if metadata.get('TvShowTitle', ''):
		if KODI_ov20: vinfo.setTvShowTitle(metadata['TvShowTitle'])
		else: vinfo['Tvshowtitle'] = metadata['TvShowTitle']
	if metadata.get('Tagline', ''):
		if KODI_ov20: vinfo.setTagLine(metadata['Tagline'])
		else: vinfo['Tagline'] = metadata['Tagline']
	description = metadata['Plot'] if metadata.get('Plot') not in ['', 'None', None] else ' '
	if KODI_ov20: vinfo.setPlot(description)
	else: vinfo['Plot'] = description
	if str(metadata.get('Duration')).isdecimal():
		if KODI_ov20: vinfo.setDuration(int(metadata['Duration']))
		else: vinfo['Duration'] = metadata['Duration']
	if str(metadata.get('Season')).isdecimal():
		if KODI_ov20: vinfo.setSeason(int(metadata['Season']))
		else: vinfo['Season'] = metadata['Season']
	if str(metadata.get('Episode')).isdecimal():
		if KODI_ov20: vinfo.setEpisode(int(metadata['Episode']))
		else: vinfo['Episode'] = metadata['Episode']
	if metadata.get('Date', ''):
		if KODI_ov20: listitem.setDateTime(metadata['Date'])
		else: vinfo['Date'] = metadata['Date']
	if metadata.get('Aired', ''):
		if KODI_ov20: vinfo.setFirstAired(metadata['Aired'])
		else: vinfo['Aired'] = metadata['Aired']
	if metadata.get('Genre', '') and len(metadata['Genre']) > 3:
		if KODI_ov20: vinfo.setGenres([metadata['Genre']])
		else: vinfo['Genre'] = metadata['Genre']
	if metadata.get('Studio', ''):
		if KODI_ov20: vinfo.setStudios([metadata['Studio']])
		else: vinfo['Studio'] = metadata['Studio']
	if metadata.get('Mediatype', ''):
		if KODI_ov20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	picture = metadata.get('Image', icon)
	listitem.setArt({'icon': icon, 'thumb': picture, 'poster': picture, 'fanart': defaultFanart})
	if useThumbAsFanart and not artpic in picture:
		listitem.setArt({'fanart': picture})
	if metadata.get('Reference') == 'Single':
		listitem.setProperty('IsPlayable', 'true')
	if not KODI_ov20: listitem.setInfo('Video', vinfo)
	return listitem
