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
from urllib.parse import parse_qsl, urlparse, urlencode, quote_plus, unquote_plus
from urllib.request import urlopen
from functools import reduce
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
SEARCHFILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'search_string'))
WORKFILE							= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
channelFavsFile					= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_SEVER.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
alppic									= os.path.join(addonPath, 'resources', 'media', 'alphabet', '').encode('utf-8').decode('utf-8')
genpic									= os.path.join(addonPath, 'resources', 'media', 'genre', '').encode('utf-8').decode('utf-8')
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
prefSTREAM						= addon.getSetting('prefer_stream')
showCHANFOLD				= addon.getSetting('show_chanFOLD') == 'true'
showCHANLINK				= addon.getSetting('show_chanLINK') == 'true'
showARTE							= (True if addon.getSetting('show_ARTE') == 'true' else False)
showJOYN							= (True if addon.getSetting('show_JOYN') == 'true' else False)
showRTL							= (True if addon.getSetting('show_TVNOW') == 'true' else False)
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
JOYN_staticCODE				= addon.getSetting('joyn_staticCODE')
SEVER_staticCODE			= addon.getSetting('sever_staticCODE')
ARTEEX								= ['ARTE']
JOYNEX								= ['KABEL 1', 'PRO7', 'PRO7 MAXX', 'SAT1', 'SIXX']
RTLEX									= ['N-TV', 'NOW!', 'RTL', 'RTL NITRO', 'RTL2', 'RTLPLUS', 'SUPER RTL', 'VOX']
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
IMG_cover							= 'https://sendungen.fra1.cdn.digitaloceanspaces.com/{}'
API_BASE							= 'https://www.sendungverpasst.de/_next/data/' # cl7AR8ToJErdg4wnRFYGT # CODE of the Webpage
API_COMP							= 'https://www.sendungverpasst.de/_next/data/'+SEVER_staticCODE
BASE_URL							= 'https://www.sendungverpasst.de/'
BASE_JOYN						= 'https://www.joyn.de/'
API_ARD							= 'https://api.ardmediathek.de/page-gateway/pages/'
API_ZDF								= 'https://api.zdf.de'
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

def build_mass(body):
	return f"{HOST_AND_PATH}?{urlencode(body)}"

def get_userAgent(REV='109.0', VER='112.0'):
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

def _header(REFERRER=None, CODE=None, USERTOKEN=None):
	header = {}
	header['Pragma'] = 'no-cache'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.8,en;q=0.7'
	if REFERRER:
		header['Referer'] = REFERRER
	if CODE and USERTOKEN:
		header[CODE] = USERTOKEN
	return header

def getUrl(url, method='GET', REF=None, WAY=None, AUTH=None, headers=None, cookies=None, allow_redirects=True, verify=False, stream=None, data=None, json=None):
	simple = requests.Session()
	ANSWER, NEW_CODING = (None for _ in range(2))
	retries = 0
	if url.startswith('http'):
		try:
			response = simple.get(url, headers=_header(REF, WAY, AUTH), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
			ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
			debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {_header(REF, WAY, AUTH)} ===")
		except requests.exceptions.RequestException as e:
			failing(f"(common.getUrl) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
			dialog.notification(translation(30521).format('URL', ''), translation(30523).format(str(e)), icon, 10000)
			return sys.exit(0)
	else:
		def getCollected(suffix_URL, token_TRANSFER=None):
			debug_MS(f"(common.getCollected) === suffix_URL : {suffix_URL} || token_TRANSFER : {str(token_TRANSFER)} ===")
			if url.startswith('JOYN_REDIRECT'):
				recentURL = API_JOYN+token_TRANSFER+suffix_URL.split('@@')[1] if token_TRANSFER else API_JOYN+JOYN_staticCODE+suffix_URL.split('@@')[1]
			else:
				recentURL = API_BASE+token_TRANSFER+suffix_URL if token_TRANSFER else API_BASE+SEVER_staticCODE+suffix_URL
			return recentURL
		while not ANSWER and retries < 3: # 2 x Wiederholungen (gesamt=3) für den URL-Request ::: da der Code für die API_BASE evtl. wieder geändert wurde
			retries += 1
			try:
				endURL = getCollected(url, NEW_CODING)
				response = simple.get(endURL, headers=_header(REF, WAY, AUTH), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
				response.raise_for_status()
				VALID_JSON = response.json() if method in ['GET', 'TRACK'] else None
				ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
				debug_MS(f"(common.getUrl) === CALLBACK === RETRIES_no : {str(retries)} === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {_header(REF, WAY, AUTH)} ===")
			except Exception as e: # No JSON object could be decoded
				failing(f"(common.getUrl) ERROR - CURRENT_TOKEN - ERROR ##### RETRIES_no : {str(retries)} === URL : {url} === FAILURE : {str(e)} #####")
				SURVEY = BASE_JOYN if url.startswith('JOYN_REDIRECT') else BASE_URL
				CONTENT = simple.get(SURVEY, headers=_header(REF, WAY, AUTH), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=10)
				SCAN_REQ = re.compile(r'''</script><script src=["']/_next/static/([^/]+?)/_ssgManifest.js''', re.S).findall(CONTENT.text)
				#SCAN_REQ = re.compile(r'''["']query["']:.*?,["']buildId["']:["']([^"']+)["'],["']isFallback["']''', re.S).findall(CONTENT.text)
				if SCAN_REQ:
					NEW_CODING = SCAN_REQ[0]
					if url.startswith('JOYN_REDIRECT'): addon.setSetting('joyn_staticCODE', NEW_CODING)
					else: addon.setSetting('sever_staticCODE', NEW_CODING)
				elif retries > 1 and not SCAN_REQ:
					retries += 2
					dialog.notification(translation(30521).format('URL', ''), translation(30524), icon, 12000)
					break
				time.sleep(2)
	return ANSWER

def ADDON_operate(IDD):
	check_1 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	check_2 = 'undone'
	if '"enabled":false' in check_1:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{IDD}", "enabled":true}}}}')
			failing(f"(common.ADDON_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
		check_2 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	if '"error":' in check_1 or '"error":' in check_2:
		dialog.ok(addon_id, translation(30501).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - INSTALLED - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT installiert !!! #####")
		return False
	if '"enabled":true' in check_1 or '"enabled":true' in check_2:
		return True
	if '"enabled":false' in check_2:
		dialog.ok(addon_id, translation(30502).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Eine automatische Aktivierung ist leider NICHT möglich !!! #####")
	return False

def get_Sorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_EPISODE, xbmcplugin.SORT_METHOD_DATE]

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

def repair_umlaut(wrong):
	if wrong is not None:
		for n in (('ä', 'ae'), ('Ä', 'Ae'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'oe'), ('ß', 'ss')):
					wrong = wrong.replace(*n)
		wrong = wrong.strip()
	return wrong

params = dict(parse_qsl(sys.argv[2][1:]))
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
pict = unquote_plus(params.get('pict', ''))
plot = unquote_plus(params.get('plot', ''))
genre = unquote_plus(params.get('genre', ''))
studio = unquote_plus(params.get('studio', ''))
ident = unquote_plus(params.get('ident', '0'))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', 'DEFAULT'))
page = unquote_plus(params.get('page', '1'))
limit = unquote_plus(params.get('limit', '10'))
position = unquote_plus(params.get('position', '0'))
extras = unquote_plus(params.get('extras', 'standard'))
transmit = unquote_plus(params.get('transmit', 'Unbekannt'))
wanted = unquote_plus(params.get('wanted', 'standard'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
