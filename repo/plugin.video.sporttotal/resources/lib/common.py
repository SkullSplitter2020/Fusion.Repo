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
import socket
import shutil
import time
from datetime import datetime, timedelta
from calendar import timegm as TGM
import requests
import ssl
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
from urllib.request import urlopen, Request, URLError, HTTPError
from concurrent.futures import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .provider import Client
from .external import *


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
SEARCHFILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'search_string'))
WORKFILE							= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
channelFavsFile					= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_STTV.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
advices								= addon.getSetting('advices') == 'true'
nowlive								= addon.getSetting('nowlive') == 'true'
upcoming							= addon.getSetting('upcoming') == 'true'
basedates							= addon.getSetting('basedates') == 'true'
basesearch							= addon.getSetting('basesearch') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
enableBACK						= addon.getSetting('show_homebutton') == 'true'
PLACEMENT						= addon.getSetting('button_place')
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
STTV_staticCODE				= addon.getSetting('sttv_staticCODE')
GENLANG							= [{'old': 'americanfootball', 'new': 'American Football'},{'old': 'fieldhockey', 'new': 'Feldhockey'},{'old': 'icehockey', 'new': 'Eishockey'},{'old': 'indoorhockey', 'new': 'Hallenhockey'},{'old': 'soccer', 'new': 'Fußball'}]
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
API_NEXT							= 'https://sporttotal.tv/_next/data/' # DcFuGrlYNH7l7OvM38AZj # CODE of the Webpage
API_BASE							= 'https://sporttotal.tv/api/v2/'
BASE_URL							= 'https://sporttotal.tv/en/sports/soccer'
traversing							= Client(Client.CONFIG_SPORTTOTAL)
defaultAgent						= 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:122.0) Gecko/20100101 Firefox/122.0'

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

def _header(REFERRER=None):
	header, config = {}, traversing.get_config()
	header['Pragma'] = 'no-cache'
	header['Accept'] = 'application/json, application/x-www-form-urlencoded, text/plain, */*'
	header['documentLifecycle'] = 'active'
	header['User-Agent'] = defaultAgent
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8'
	if REFERRER:
		header.update(config['header'])
	return header

def getMultiData(MURLS, method='GET', ORI_REF=True, fields=None):
	COMBI_NEW = []
	number = len(MURLS)
	def download(pos, url, manager):
		response = manager.request(method, url, fields, headers=_header(ORI_REF), timeout=5, retries=2)
		if response and response.status in [200, 201, 202]:
			debug_MS(f"(common.getMultiData[1]) === POS : {str(pos)} === REQUESTED URL : {url} === REQUESTED HEADER : {_header(ORI_REF)} ===")
			return f'{{"Position":{str(pos)},"Demand":"{url}",{py3_dec(response.data[1:-1])}}}'
		else:
			MESSAGE = '{"recordNotFound":true}' if '"recordNotFound"' in str(py3_dec(response.data)) else '{"ERROR_occurred":true}'
			if MESSAGE != '{"recordNotFound":true}': failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {str(pos)} === STATUS : {str(response.status)} === URL : {url} === DATA : {str(py3_dec(response.data))} #####")
			return MESSAGE
	with ThreadPoolExecutor() as executor:
		connector = urllib3.PoolManager(maxsize=10, block=True)
		debug_MS("---------------------------------------------")
		picker = [executor.submit(download, pos, url, connector) for pos, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(json.loads(future.result()))
			except Exception as e:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {str(e)} #####")
				dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			matching = [flop for flop in COMBI_NEW[:] if flop.get('ERROR_occurred', '') is True]
			if len(matching) == number:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return json.dumps(COMBI_NEW, indent=2)

def getUrl(url, method='GET', ORI_REF=True, headers=None, cookies=None, allow_redirects=True, verify=False, stream=None, data=None, json=None, timeout=30):
	(ANSWER, NEW_CODING), retries = (None for _ in range(2)), 0
	UNCHECK = ssl.create_default_context()
	UNCHECK.check_hostname = False
	UNCHECK.verify_mode = ssl.CERT_NONE
	simple = create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False}, ssl_context=UNCHECK)
	if url.startswith('http'):
		try:
			response = simple.get(url, headers=_header(ORI_REF), cookies=cookies, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=timeout)
			VALID_JSON = response.json() if method == 'GET' else None
			ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
			debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {response.request.headers} ===")
			debug_MS("---------------------------------------------")
		except Exception as e: # No JSON object could be decoded
			failing(f"(common.getUrl) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
			dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 10000)
			return sys.exit(0)
	else:
		def getCollected(suffix_URL, token_TRANSFER=None):
			debug_MS(f"(common.getCollected) === suffix_URL : {suffix_URL} || token_TRANSFER : {str(token_TRANSFER)} ===")
			recentURL = API_NEXT+token_TRANSFER+suffix_URL if token_TRANSFER else API_NEXT+STTV_staticCODE+suffix_URL
			return recentURL
		while not ANSWER and retries < 3: # 2 x Wiederholungen (gesamt=3) für den URL-Request ::: da der Code für die API_BASE evtl. wieder geändert wurde
			retries += 1
			try:
				endURL = getCollected(url, NEW_CODING)
				response = simple.get(endURL, headers=_header(ORI_REF), cookies=cookies, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=timeout)
				response.raise_for_status()
				VALID_JSON = response.json() if method in ['GET', 'TRACK'] else None
				ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
				debug_MS(f"(common.getUrl) === CALLBACK === RETRIES_no : {str(retries)} === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {response.request.headers} ===")
				debug_MS("---------------------------------------------")
			except Exception as e: # Request-Status_Code is not 200 or No JSON object could be decoded
				failing(f"(common.getUrl) ERROR - CURRENT_TOKEN - ERROR ##### RETRIES_no : {str(retries)} === URL : {url} === FAILURE : {str(e)} #####")
				CONTENT = simple.get(BASE_URL, headers=_header(ORI_REF), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=15)
				SCAN_REQ = re.compile(r'''</script><script src=["']/_next/static/([^/]+?)/_ssgManifest.js''', re.S).findall(CONTENT.text)
				#SCAN_REQ = re.compile(r'''["']query["']:.*?,["']buildId["']:["']([^"']+)["'],["']isFallback["']''', re.S).findall(CONTENT.text)
				if SCAN_REQ:
					NEW_CODING = SCAN_REQ[0]
					addon.setSetting('sttv_staticCODE', NEW_CODING)
				elif retries > 2 and not SCAN_REQ:
					dialog.notification(translation(30521).format('URL'), translation(30525), icon, 12000)
					break
				time.sleep(2)
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

def get_CentralTime(info):
	if info.endswith('+01:00'): # Stimmt nicht mit Zeitzone überein, daher plus 1 Stunde
		SEGMENT = datetime(*(time.strptime(info[:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6]))
		LOCAL_DATE = (SEGMENT + timedelta(hours=1))
	elif info.endswith('+02:00'): # Stimmt mit Zeitzone überein, daher ohne Umwandlung zurück
		LOCAL_DATE = datetime(*(time.strptime(info[:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6]))
	else: # Ist UTC-Zeit, daher hier umwandeln zu LOCAL-Zeit
		UTC_DATE = datetime(*(time.strptime(info[:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6]))
		try: # 2024-05-10T22:55:00.000+02:00
			LOCAL_DATE = datetime.fromtimestamp(TGM(UTC_DATE.timetuple()))
			assert UTC_DATE.resolution >= timedelta(microseconds=1)
			LOCAL_DATE = LOCAL_DATE.replace(microsecond=UTC_DATE.microsecond)
		except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
			LOCAL_DATE = datetime.fromtimestamp(0) + timedelta(seconds=TGM(UTC_DATE.timetuple()))
			LOCAL_DATE = LOCAL_DATE - timedelta(hours=datetime.timetuple(LOCAL_DATE).tm_isdst)
	return LOCAL_DATE

def get_Picture(elem_id, resources, elem_type):
	img_type = next(filter(lambda x: x.get('imageType', '') and elem_type in x.get('imageType', ''), resources), None)
	if img_type:
		return img_type['url'].replace(' ', '%20')
	return None

def get_Number(DATA, LINK):
	PAYING = 0
	for each in DATA.get('data', []):
		FREE = each['event'].get('free', True) if each.get('event', '') and 'highlights' in LINK else each.get('free', True)
		if ('live' in LINK or 'upcoming' in LINK or 'latest' in LINK or 'highlights' in LINK) and FREE is False:
			PAYING += 1
	return PAYING

def repair_umlaut(wrong):
	if wrong is not None:
		for n in (('ä', 'ae'), ('Ä', 'Ae'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'oe'), ('ß', 'ss')):
					wrong = wrong.replace(*n)
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
					('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '), ('\r\n', '[CR]'),
					("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
					('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ("\\'", "'")):
					text = text.replace(*tx)
		text = text.strip()
	return text

params = dict(parse_qsl(sys.argv[2][1:]))
name = unquote_plus(params.get('name', ''))
pict = unquote_plus(params.get('pict', icon))
url = unquote_plus(params.get('url', ''))
category = unquote_plus(params.get('category', ''))
plot = unquote_plus(params.get('plot', ''))
section = unquote_plus(params.get('section', 'Sport'))
page = unquote_plus(params.get('page', '1'))
limit = unquote_plus(params.get('limit', '40'))
position = unquote_plus(params.get('position', '0'))
excluded = unquote_plus(params.get('excluded', '0'))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', ''))
extras = unquote_plus(params.get('extras', 'DEFAULT'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
