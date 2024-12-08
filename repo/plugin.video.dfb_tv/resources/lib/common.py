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
from calendar import timegm as TGM
import xml.etree.ElementTree as ETCON
import requests
from urllib.parse import parse_qsl, urlencode, quote, quote_plus, unquote, unquote_plus
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addon_desc						= addon.getAddonInfo('description')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
SEARCHFILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'search_string'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableYOUTUBE				= addon.getSetting('youtube_channel') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
prefQUALITY						= {0: 720, 1: 480, 2: 360}[int(addon.getSetting('prefer_quality'))]
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
CHANNEL_CODE				= 'UCfMo0xj-sbdzHuzxvKdu1hw'
CHANNEL_NAME				= '@DFB'
BASE_YT								= 'plugin://plugin.video.youtube/channel/{}/playlist/{}/'
COMPANY_ID					= '2180'
STREAM_ACCESS				= 'https://tv.dfb.de/server/videoConfig.php?redirect=1&aaccepted=true&videoid={}&partnerid={}&language=de&format=iphone' # SID and COMPANY_ID
BASE_URL							= 'https://www.dfb.de/'

xbmcplugin.setContent(ADDON_HANDLE, 'videos')

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

def get_userAgent(REV='122.0', VER='122.0'):
	base = 'Mozilla/5.0 {} Gecko/20100101 Firefox/'+VER
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format(f'(X11; Linux arm64; rv:{REV})') # ARM based Linux
		return base.format(f'(X11; Linux x86_64; rv:{REV})') # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format(f'(Windows NT 10.0; Win64; x64; rv:{REV})') # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format(f'(Macintosh; Intel Mac OS X 10.15; rv:{REV})') # Mac OSX
	return base.format(f'(X11; Linux x86_64; rv:{REV})') # x64 Linux

def _header(REFERRER=None):
	header = {}
	header['Pragma'] = 'no-cache'
	header['Cache-Control'] = 'no-cache'
	header['Accept'] = 'application/json, application/x-www-form-urlencoded, text/plain, */*'
	header['documentLifecycle'] = 'active'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Origin'] = BASE_URL[:-1]
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	if REFERRER:
		header['Referer'] = REFERRER
	return header

def getUrl(url, method='GET', REF=None, headers=None, cookies=None, allow_redirects=True, verify=False, stream=None, data=None, json=None, timeout=30):
	simple = requests.Session()
	ANSWER = None
	try:
		response = simple.get(url, headers=_header(REF), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=timeout)
		ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
		debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {_header(REF)} ===")
	except requests.exceptions.RequestException as e:
		failing(f"(common.getUrl) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 12000)
		return sys.exit(0)
	return ANSWER

def ADDON_operate(IDD):
	check_1 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	check_2 = 'undone'
	if '"enabled":false' in check_1:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{IDD}", "enabled":true}}}}')
			failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
		check_2 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	if '"error":' in check_1 or '"error":' in check_2:
		dialog.ok(addon_id, translation(30501).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT installiert !!! #####")
		return False
	if '"enabled":true' in check_1 or '"enabled":true' in check_2:
		return True
	if '"enabled":false' in check_2:
		dialog.ok(addon_id, translation(30502).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Eine automatische Aktivierung ist leider NICHT möglich !!! #####")
	return False

def cleaning(text, CUSTOMISE=False):
	if text is not None: # Remove Emojis and other unwanted Symbols in JSON-Text on the Website of "ProSieben.de"
		if CUSTOMISE is True:
			for ex in (('<strong>', 'fatstart'), ('</strong>', 'fatend'), ('<em>', 'slanstart'), ('</em>', 'slanend'), ('<br>', 'breakone'), ('\\n', '\n'), ('\n', 'breakone'), ('</p><p>', 'breakdouble'),
						(',', 'comcom'), (';', 'semisemi'), (':', 'doubledot'), ('.', 'nomdot'), ('!', 'markmark'), ('?', 'questquest'), ('=', 'equalequal'), ('&', 'andand'), ("'", 'quotone'), ('"', 'quotdouble'), ('-', 'dashdash'), (' | ', 'pipepipe'),
						('~', 'swunswun'), ('*', 'starstar'), ('+', 'crosscross'), ('(', 'brackstart'), (')', 'brackend'), ('//', 'verticvertic'), ('/', 'slashslash'), ('#', 'atrhomb'), ('@', 'atmonkey'), ('§', 'parapara'), ('$', 'dolldoll'), ('%', 'perper')):
						text = text.replace(*ex)
			text = re.sub(r'(\<.*?\>|[^\w])', ' ', text) # FIRST: Remove text between arrow-signs (Links etc.) // SECOND: Remove anything that's not alphanumeric or underscore
		for n in (('fatstart', '[B]'), ('fatend', '[/B]'), ('slanstart', '[I]'), ('slanend', '[/I]'), ('breakone   ', '[CR]'), ('breakone  ', '[CR]'), ('breakone', '[CR]'), ('breakdouble', '[CR][CR]'),
					('comcom', ','), ('semisemi', ';'), ('doubledot', ':'), ('nomdot', '.'), ('markmark', '!'), ('questquest', '?'), ('equalequal', '='), ('andand', '&'), ('quotone', "'"), ('quotdouble', '"'), ('dashdash', '-'), ('pipepipe', ' | '),
					('swunswun', '~'), ('starstar', '*'), ('crosscross', '+'), ('brackstart', '('), ('brackend', ')'), ('verticvertic', '|'), ('slashslash', '/'), ('atrhomb', '#'), ('atmonkey', '@'), ('parapara', '§'), ('dolldoll', '$'), ('perper', '%'),
					('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&apos;', "'"), ("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('\\u0026', '&'), ('&quot;', '"'), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '),
					('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''), ('\xc2\xb7', '-'),
					('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&yuml;', 'ÿ'),
					('&agrave;', 'à'), ('&aacute;', 'á'), ('&acirc;', 'â'), ('&egrave;', 'è'), ('&eacute;', 'é'), ('&ecirc;', 'ê'), ('&igrave;', 'ì'), ('&iacute;', 'í'), ('&icirc;', 'î'),
					('&ograve;', 'ò'), ('&oacute;', 'ó'), ('&ocirc;', 'ô'), ('&ugrave;', 'ù'), ('&uacute;', 'ú'), ('&ucirc;', 'û'), ('\\"', '"'), ('\t', ''), ('   ', ''), ('  ', ' ')):
					text = text.replace(*n)
		if CUSTOMISE is True:
			if text[:4] == 'LIVE': text = f"[B][COLOR chartreuse]≡ ≡ ≡ UP-{text[:4]} ≡ ≡ ≡[/COLOR][/B] [I]{text[4:]}[/I]"
			if 'Abonnier' in text or 'Subscribe' in text or 'English ' in text or 'http' in text:
				text = re.sub(r'(?:(?:\[CR]?-? ?)*Abonnier[\s\S]+|(?:\[CR]?-? ?)*Subscribe now [\s\S]+|(?:\[CR]?(?:#dfb)?-? ?)*English [\s\S]+|https?:(?:\S+\[CR]|\S+))', '', text)
			text = text.replace('[CR][CR]...', '').replace('!.', '!')
		text = text.strip()
	return text

params = dict(parse_qsl(sys.argv[2][1:]))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
searching = unquote_plus(params.get('searching', 'NOTHING'))
category = unquote_plus(params.get('category', ''))
page = unquote_plus(params.get('page', '1'))
limit = unquote_plus(params.get('limit', '10'))
extras = unquote_plus(params.get('extras', 'standard'))
