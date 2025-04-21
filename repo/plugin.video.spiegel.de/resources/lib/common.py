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
from calendar import timegm as TGM
import requests
import ssl
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
from concurrent.futures import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


socket.setdefaulttimeout(30)
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
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
genpic									= os.path.join(addonPath, 'resources', 'media', 'genre', '').encode('utf-8').decode('utf-8')
PAGINATION						= int(addon.getSetting('max_pages'))+1
enableYOUTUBE				= addon.getSetting('youtube_channel') == 'true'
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableAUDIO						= addon.getSetting('audiostreams') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
prefSTREAM						= int(addon.getSetting('prefer_stream'))
prefQUALITY						= {0: 1080, 1: 720, 2: 576, 3: 360}[int(addon.getSetting('prefer_quality'))]
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
COMPANY_ID						= '5ac1e950-45c7-4eb7-87c0-aa0f018441b8' # https://omny.fm/api/orgs/5ac1e950-45c7-4eb7-87c0-aa0f018441b8/clips/6a92c18a-3ce2-49a4-9c87-b01a0144dadc
CHANNEL_CODE				= 'UC1w6pNGiiLdZgyNpXUnA4Zw'
CHANNEL_NAME				= '@derspiegel'
BASE_YT								= 'plugin://plugin.video.youtube/channel/{}/playlist/{}/'
BASE_URL							= 'https://www.spiegel.de/'

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

def _header(REFERRER=None):
	header = {}
	header['Connection'] = 'keep-alive'
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	if REFERRER: header['Referer'] = REFERRER
	return header

def getMultiData(MURLS, method='GET', queries='TEXT', REF=BASE_URL, timeout=5, retries=2):
	COMBI_NEW, number = [], len(MURLS)
	def download(pos, clip, link, url):
		UNCHECK = ssl.create_default_context()
		UNCHECK.check_hostname = False
		UNCHECK.verify_mode = ssl.CERT_NONE
		connector = urllib3.PoolManager(block=True, ssl_context=UNCHECK, maxsize=20)
		with connector.request(method, f"{BASE_URL}video/", headers=_header(REF), preload_content=False, redirect=True, timeout=timeout, retries=retries) as mrs:
			if mrs.status in [200, 201, 202]:
				CONPLUS = REF if queries == 'TEXT' else None
				response = connector.request(method, url, headers=_header(CONPLUS), redirect=True, timeout=timeout, retries=retries)
				if response.status in [200, 201, 202]:
					debug_MS(f"(common.getMultiData[1]) === POS : {pos} === REQUESTED URL : {url} === REQUESTED HEADER : {_header(CONPLUS)} ===")
					if queries == 'TEXT':
						return [pos, clip, link, url, py3_dec(response.data)]
					elif queries == 'JSON':
						return f'{{"Position":{pos},"PlayForm":"{clip}","NaviLink":"{link}","Demand":"{url}",{py3_dec(response.data[1:-1])}}}'
				else:
					failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {pos} === STATUS : {response.status} === URL : {url} === DATA : {py3_dec(response.data)} #####")
					return [pos, clip, link, url, None] if queries == 'TEXT' else '{"ERROR_occurred":true}'
		connector.clear()
	with ThreadPoolExecutor() as executor:
		picker = [executor.submit(download, pos, clip, link, url) for pos, clip, link, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(future.result()) if queries == 'TEXT' else COMBI_NEW.append(json.loads(future.result()))
			except Exception as exc:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {exc} #####")
				dialog.notification(translation(30521).format('DETAILS'), translation(30523).format(exc), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			debug_MS("* * * * * * * * * * * * * * * * * * * * * * *")
			matching = [flop for flop in COMBI_NEW[:] if flop[4] is None] if queries == 'TEXT' else [flop for flop in COMBI_NEW[:] if flop.get('ERROR_occurred', '') is True]
			if len(matching) == number or len(matching) > 15:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return COMBI_NEW if queries == 'TEXT' else json.dumps(COMBI_NEW, indent=2)

def getContent(url, method='GET', queries='JSON', REF=BASE_URL, headers={}, redirects=True, verify=False, data=None, json=None, timeout=30):
	simple, ANSWER = requests.Session(), None
	try:
		response = simple.request(method, url, headers=_header(REF), allow_redirects=redirects, verify=verify, timeout=timeout)
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
		debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF)} ===")
	except requests.exceptions.RequestException as exc:
		failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
		return sys.exit(0)
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

def get_RunTime(info):
	try:
		if 'min' in info.lower():
			info = re.sub('[a-zA-Z]', '', info)
			secs = int(info) * 60
		else:
			info = re.sub('[a-zA-Z]', '', info)
			secs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(info.split(':'))))
		return "{0:.0f}".format(secs)
	except: return 0

def get_CentralTime(indicator, event='EPOCHTIME'):
	CONVERTED = indicator if event == 'EPOCHTIME' else datetime(*(time.strptime(indicator[:19], '%Y-%m-%dT%H:%M:%S')[0:6]))
	try: # 1702235640 or 2024-02-23T04:17:00.000Z
		LOCAL_DATE = datetime.fromtimestamp(TGM(CONVERTED.timetuple()))
		assert CONVERTED.resolution >= timedelta(microseconds=1)
		LOCAL_DATE = LOCAL_DATE.replace(microsecond=CONVERTED.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		LOCAL_DATE = datetime.fromtimestamp(0) + timedelta(seconds=TGM(CONVERTED.timetuple()))
		LOCAL_DATE = LOCAL_DATE - timedelta(hours=datetime.timetuple(LOCAL_DATE).tm_isdst)
	return LOCAL_DATE

def getSorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_DATE]

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
			('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '),
			("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
			('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ('\\"', '"'), ('🔴 ', '')):
			text = text.replace(*tx)
		text = text.strip()
	return text

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_ov20 else {}
	if KODI_ov20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
	if metadata.get('Tagline', ''):
		if KODI_ov20: vinfo.setTagLine(metadata['Tagline'])
		else: vinfo['Tagline'] = metadata['Tagline']
	description = metadata['Plot'] if metadata.get('Plot') not in ['', 'None', None] else ' '
	if KODI_ov20: vinfo.setPlot(description)
	else: vinfo['Plot'] = description
	if str(metadata.get('Duration')).isdecimal():
		if KODI_ov20: vinfo.setDuration(int(metadata['Duration']))
		else: vinfo['Duration'] = metadata['Duration']
	if metadata.get('Date', ''):
		if KODI_ov20: listitem.setDateTime(metadata['Date'])
		else: vinfo['Date'] = metadata['Date']
	if metadata.get('Aired', ''):
		if KODI_ov20: vinfo.setFirstAired(metadata['Aired'])
		else: vinfo['Aired'] = metadata['Aired']
	if str(metadata.get('Year')).isdecimal():
		if KODI_ov20: vinfo.setYear(int(metadata['Year']))
		else: vinfo['Year'] = metadata['Year']
	if metadata.get('Genre', ''):
		if KODI_ov20: vinfo.setGenres([metadata['Genre']])
		else: vinfo['Genre'] = metadata['Genre']
	if KODI_ov20: vinfo.setStudios(['Spiegel.de'])
	else: vinfo['Studio'] = 'Spiegel.de'
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
