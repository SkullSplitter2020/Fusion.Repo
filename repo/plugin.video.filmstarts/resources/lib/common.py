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
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
WORKS_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
BEFORE_AND_AFTER			= addon.getSetting('forward_backward') == 'true'
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableBACK						= addon.getSetting('show_homebutton') == 'true'
PLACEMENT						= int(addon.getSetting('button_place'))
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
BASE_URL							= 'https://www.filmstarts.de'
BASE_DAILY						= 'https://geo.dailymotion.com'
API_DAILY							= 'https://www.dailymotion.com/player/metadata/video/'

xbmcplugin.setContent(ADDON_HANDLE, 'movies')

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

def get_userAgent(REV='136.0', VER='136.0'):
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

def _header(ORIGIN=None, REFERRER=None):
	header = {}
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	if ORIGIN: header['Origin'] = ORIGIN
	if REFERRER: header['Referer'] = REFERRER
	return header

def getMultiData(MURLS, method='GET', ORI=None, REF=f"{BASE_URL}/", timeout=5, retries=2):
	COMBI_NEW, number = [], len(MURLS)
	def download(pos, extra, link, url):
		UNCHECK = ssl.create_default_context()
		UNCHECK.check_hostname = False
		UNCHECK.verify_mode = ssl.CERT_NONE
		connector = urllib3.PoolManager(block=True, ssl_context=UNCHECK, maxsize=20)
		with connector.request(method, f"{BASE_URL}/kritiken/", headers=_header(ORI, REF), preload_content=False, redirect=True, timeout=timeout, retries=retries) as mrs:
			if mrs.status in [200, 201, 202]:
				response = connector.request(method, url, headers=_header(ORI, REF), redirect=True, timeout=timeout, retries=retries)
				if response.status in [200, 201, 202]:
					debug_MS(f"(common.getMultiData[1]) === POS : {pos} === REQUESTED URL : {url} === REQUESTED HEADER : {_header(ORI, REF)} ===")
					return [pos, extra, link, url, py3_dec(response.data)]
				else:
					failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {pos} === STATUS : {response.status} === URL : {url} === DATA : {py3_dec(response.data)} #####")
					return [pos, extra, link, url, None]
		connector.clear()
	with ThreadPoolExecutor() as executor:
		picker = [executor.submit(download, pos, extra, link, url) for pos, extra, link, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(future.result())
			except Exception as exc:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {exc} #####")
				dialog.notification(translation(30521).format('DETAILS'), translation(30523).format(exc), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			matching = [flop for flop in COMBI_NEW[:] if flop[4] is None]
			if len(matching) == number or len(matching) > 5:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return COMBI_NEW

def getContent(url, method='GET', queries='TEXT', ORI=None, REF=None, headers={}, redirects=True, verify=False, data=None, json=None, timeout=30):
	simple, ANSWER = requests.Session(), None
	try:
		response = simple.request(method, url, headers=_header(ORI, REF), allow_redirects=redirects, verify=verify, timeout=timeout)
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
		debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(ORI, REF)} ===")
	except requests.exceptions.RequestException as exc:
		failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 12000)
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
		secs = info
		if not str(info).isdecimal():
			info = re.sub('[a-zA-Z]', '', info)
			secs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(info.split(':'))))
		return secs
	except: return None

def preserve(store, data=None):
	if data is not None:
		with open(store, 'w') as topics:
			json.dump(data, topics, indent=2, sort_keys=True)
	else:
		with open(store, 'r') as topics:
			arrive = json.load(topics)
		return arrive

def cleaning(text, DEEPCLEAN=False):
	if text is not None:
		if DEEPCLEAN is True:
			text = re.sub(r'\<.*?\>', '', text)
		for tx in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&nbsp;', ' '), ("&quot;", "\""), ("&Quot;", "\""), ('&reg;', ''), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('–', '-'), ('&hellip;', '...'), ('&sup2;', '²'),
			('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'),
			('&Auml;', 'Ä'), ('Ä', 'Ä'), ('&auml;', 'ä'), ('ä', 'ä'), ('&Euml;', 'Ë'), ('&euml;', 'ë'), ('&Iuml;', 'Ï'), ('&iuml;', 'ï'), ('&Ouml;', 'Ö'), ('Ö', 'Ö'), ('&ouml;', 'ö'), ('ö', 'ö'), ('&Uuml;', 'Ü'), ('Ü', 'Ü'), ('&uuml;', 'ü'), ('ü', 'ü'), ('&yuml;', 'ÿ'),
			('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'),
			('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'ó'), ('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
			('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'),
			('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'),
			('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
			('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'),
			("\\'", "'"), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&rsquo;', '’'), ('&lsquo;', '‘'), ('&sbquo;', '’'), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
			('&#9;', ''), ("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#196;', 'Ä'), ('&#214;', 'Ö'), ('&#220;', 'Ü'), ('&#228;', 'ä'), ('&#246;', 'ö'), ('&#252;', 'ü'), ('&#223;', 'ß'), ('&#160;', ' '),
			('&#192;', 'À'), ('&#193;', 'Á'), ('&#194;', 'Â'), ('&#195;', 'Ã'), ('&#197;', 'Å'), ('&#199;', 'Ç'), ('&#200;', 'È'), ('&#201;', 'É'), ('&#202;', 'Ê'),
			('&#203;', 'Ë'), ('&#204;', 'Ì'), ('&#205;', 'Í'), ('&#206;', 'Î'), ('&#207;', 'Ï'), ('&#209;', 'Ñ'), ('&#210;', 'Ò'), ('&#211;', 'Ó'), ('&#212;', 'Ô'),
			('&#213;', 'Õ'), ('&#215;', '×'), ('&#216;', 'Ø'), ('&#217;', 'Ù'), ('&#218;', 'Ú'), ('&#219;', 'Û'), ('&#221;', 'Ý'), ('&#222;', 'Þ'), ('&#224;', 'à'),
			('&#225;', 'á'), ('&#226;', 'â'), ('&#227;', 'ã'), ('&#229;', 'å'), ('&#231;', 'ç'), ('&#232;', 'è'), ('&#233;', 'é'), ('&#234;', 'ê'), ('&#235;', 'ë'),
			('&#236;', 'ì'), ('&#237;', 'í'), ('&#238;', 'î'), ('&#239;', 'ï'), ('&#240;', 'ð'), ('&#241;', 'ñ'), ('&#242;', 'ò'), ('&#243;', 'ó'), ('&#244;', 'ô'),
			('&#245;', 'õ'), ('&#247;', '÷'), ('&#248;', 'ø'), ('&#249;', 'ù'), ('&#250;', 'ú'), ('&#251;', 'û'), ('&#253;', 'ý'), ('&#254;', 'þ'), ('&#255;', 'ÿ'), ('&#287;', 'ğ'),
			('&#304;', 'İ'), ('&#305;', 'ı'), ('&#350;', 'Ş'), ('&#351;', 'ş'), ('&#352;', 'Š'), ('&#353;', 'š'), ('&#376;', 'Ÿ'), ('&#402;', 'ƒ'),
			('&#8211;', '–'), ('&#8212;', '—'), ('&#8226;', '•'), ('&#8230;', '…'), ('&#8240;', '‰'), ('&#8364;', '€'), ('&#8482;', '™'), ('&#169;', '©'), ('&#174;', '®'), ('&#183;', '·')):
			text = text.replace(*tx)
		text = text.strip()
	return text

def enlargeIMG(cover):
	#log(f"(common.enlargeIMG) ### 1.Original-COVER : {cover} ###")
	imgCode = ['commons/', 'medias', 'pictures', 'seriesposter', 'videothumbnails']
	for XL in imgCode:
		if XL in cover:
			try: cover = f"{cover.split('.net/')[0]}.net/{XL}{cover.split(XL)[1]}"
			except: pass
	cover = re.sub(r'/c_[0-9]+_[0-9]+', '/c_500_750', cover)
	#log(f"(common.enlargeIMG) ### 2.Converted-COVER : {cover} ###")
	return cover

def convert64(url, nom='utf-8', ign='ignore'):
	debug_MS("(common.convert64) -------------------------------------------------- START = convert64 --------------------------------------------------")
	debug_MS(f"(common.convert64) ### 1.Original-URL : {url} ###")
	b64_string = url.replace('ACr', '')
	b64_string += "=" * ((4 - len(b64_string) % 4) % 4) # FIX for = TypeError: Incorrect padding
	result = base64.b64decode(b64_string).decode(nom, ign)
	debug_MS(f"(common.convert64) ### 2.Converted-URL : {result} ###")
	return result

def decodeURL(url):
	debug_MS("(common.decodeURL) -------------------------------------------------- START = decodeURL --------------------------------------------------")
	debug_MS(f"(common.decodeURL) ### 1.Original-URL : {url} ###")
	normalstring = ['3F', '2D', '13', '1E', '19', '1F', '20', '2A', '21', '22', '2B', '23', '24', '2C', '25', '26', 'BA', 'B1', 'B2', 'BB', 'B3', 'B4', 'BC', 'B5', 'B6', 'BD', 'B7', 'B8', 'BE', 'B9', 'BF', '30', '31', '32', '3B', '33', '34', '3C', '35', '3D', '4A', '41', '42', '4B', '43', '44', '4C', '45', '46', '4D', '47', '48', '4E', '49', '4F', 'C0', 'C1', 'C2', 'CB', 'C3', 'C4', 'CC', 'C5', 'C6', 'CD']
	decodestring = ['_', ':', '%', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	result = ""
	for i in range(0, len(url), 2):
		signs = normalstring.index(url[i:i+2])
		result += decodestring[signs]
	debug_MS(f"(common.decodeURL) ### 2.Decoded-URL : {result} ###")
	return result

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_ov20 else {}
	if KODI_ov20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
	if metadata.get('Original', ''):
		if KODI_ov20: vinfo.setOriginalTitle(metadata['Original'])
		else: vinfo['OriginalTitle'] = metadata['Original']
	description = metadata['Plot'] if metadata.get('Plot') not in ['', 'None', None] else ' '
	if KODI_ov20: vinfo.setPlot(description)
	else: vinfo['Plot'] = description
	if str(metadata.get('Duration')).isdecimal():
		if KODI_ov20: vinfo.setDuration(int(metadata['Duration']))
		else: vinfo['Duration'] = metadata['Duration']
	if metadata.get('Genre', ''):
		if KODI_ov20: vinfo.setGenres([metadata['Genre']])
		else: vinfo['Genre'] = metadata['Genre']
	if metadata.get('Country', ''):
		if KODI_ov20: vinfo.setCountries([metadata['Country']])
		else: vinfo['Country'] = metadata['Country']
	if metadata.get('Director', ''):
		if KODI_ov20: vinfo.setDirectors([metadata['Director']])
		else: vinfo['Director'] = metadata['Director']
	if metadata.get('Writer', ''):
		if KODI_ov20: vinfo.setWriters([metadata['Writer']])
		else: vinfo['Writer'] = metadata['Writer']
	if metadata.get('Cast', ''):
		CASTING = []
		for index, person in enumerate(metadata['Cast'].split(','), 1):
			actor = {'name': person, 'role': '', 'order': index, 'thumb': ''}
			if actor['name'] not in ['' , None]:
				CASTING.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], actor['thumb'])) if KODI_ov20 else CASTING.append(actor)
		if CASTING and len(CASTING) > 0 and KODI_ov20: vinfo.setCast(CASTING)
		elif CASTING and len(CASTING) > 0 and not KODI_ov20: listitem.setCast(CASTING)
	if str(metadata.get('Rating')).replace('.', '').isdecimal():
		if KODI_ov20: vinfo.setRating(float(metadata['Rating']), 0, 'userrating', True) # vinfo.setRating(4.6, 8940, "imdb", True) since NEXUS and UP
		else: listitem.setRating('userrating', float(metadata['Rating']), 0, True) # listitem.setRating("imdb", 4.6, 8940, True) below NEXUS (MATRIX)
	if metadata.get('Mpaa', ''):
		if KODI_ov20: vinfo.setMpaa(str(metadata['Mpaa']))
		else: vinfo['Mpaa'] = str(metadata['Mpaa'])
	if metadata.get('Mediatype', ''):
		if KODI_ov20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	picture = metadata.get('Image', icon)
	listitem.setArt({'icon': icon, 'thumb': picture, 'poster': picture})
	if useThumbAsFanart: listitem.setArt({'fanart': defaultFanart})
	if metadata.get('Reference') == 'Single': listitem.setProperty('IsPlayable', 'true')
	if not KODI_ov20: listitem.setInfo('Video', vinfo)
	return listitem
