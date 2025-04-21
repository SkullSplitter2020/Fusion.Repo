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
from urllib.parse import parse_qsl, urlencode, quote, quote_plus, unquote, unquote_plus
from urllib.request import urlopen, Request, URLError, HTTPError
from itertools import zip_longest
from concurrent.futures import *
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
FAVORIT_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_SDTV.json'))
MENUES_FILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_MENU.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
nowlive								= addon.getSetting('nowlive') == 'true'
upcoming							= addon.getSetting('upcoming') == 'true'
newest								= addon.getSetting('newest') == 'true'
topping								= addon.getSetting('topping') == 'true'
sporting								= addon.getSetting('sporting') == 'true'
channeling							= addon.getSetting('channeling') == 'true'
teamsearch						= addon.getSetting('teamsearch') == 'true'
videosearch						= addon.getSetting('videosearch') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
enableBACK						= addon.getSetting('show_homebutton') == 'true'
PLACEMENT						= int(addon.getSetting('button_place'))
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
IMG_categories					= 'https://img.sportdeutschland.tv/{}/300x300.webp'
IMG_assets							= 'https://img.sportdeutschland.tv/{}/1920x1080.webp'
API_PLAYER						= 'https://api.sportdeutschland.tv/api/web/personal/asset-token/'
API_LOGINS						= 'https://api.sportdeutschland.tv/api/web/auth/login'
API_LOGOUT						= 'https://api.sportdeutschland.tv/api/web/auth/logout'
BASE_URL							= 'https://sportdeutschland.tv/'
agent_WEB							= 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:130.0) Gecko/20100101 Firefox/130.0'
head_DET							= {'User-Agent': agent_WEB, 'Origin': BASE_URL[:-1], 'Referer': BASE_URL, 'DNT': '1', 'Accept-Encoding': 'gzip', 'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'}
head_WEB							= {**head_DET, **{'Cache-Control': 'public, max-age=300', 'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/json; charset=utf-8'}}
traversing							= Client(Client.CONFIG_SPORTDEUTSCHLAND)

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

def getMultiData(MURLS, method='GET', heading=head_WEB, timeout=5, retries=2):
	COMBI_NEW, number = [], len(MURLS)
	def download(pos, url):
		UNCHECK = ssl.create_default_context()
		UNCHECK.check_hostname = False
		UNCHECK.verify_mode = ssl.CERT_NONE
		connector = urllib3.PoolManager(block=True, ssl_context=UNCHECK, maxsize=15)
		with connector.request(method, BASE_URL, headers=heading, preload_content=False, redirect=True, timeout=timeout, retries=retries) as mrs:
			if mrs.status in [200, 201, 202]:
				response = connector.request(method, url, headers=heading, redirect=True, timeout=timeout, retries=retries)
				if response.status in [200, 201, 202]:
					debug_MS(f"(common.getMultiData[1]) === POS : {pos} === URL : {url} === HEADER : {heading} ===")
					return f'{{"Position":{pos},"Demand":"{url}",{py3_dec(response.data[1:-1])}}}'
				else:
					MESSAGE = '{"recordNotFound":true}' if 'not found' in str(py3_dec(response.data)).lower() else '{"ERROR_occurred":true}'
					if MESSAGE != '{"recordNotFound":true}':
						failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {pos} === STATUS : {response.status} === URL : {url} === DATA : {py3_dec(response.data)} #####")
					return MESSAGE
		connector.clear()
	with ThreadPoolExecutor() as executor:
		debug_MS("---------------------------------------------")
		picker = [executor.submit(download, pos, url) for pos, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(json.loads(future.result()))
			except Exception as exc:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {exc} #####")
				dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			matching = [flop for flop in COMBI_NEW[:] if flop.get('ERROR_occurred', '') is True]
			if len(matching) == number or len(matching) > 10:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return json.dumps(COMBI_NEW, indent=2)

def getContent(url, method='GET', queries='JSON', headers={}, redirects=True, verify=False, data=None, json=None, timeout=30):
	ANSWER = None
	try:
		response = requests.request(method, url, headers=head_WEB, allow_redirects=redirects, verify=verify, data=data, json=json, timeout=timeout)
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
		debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {response.request.headers} ===")
		debug_MS("---------------------------------------------")
	except Exception as exc: # No JSON object could be decoded
		failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
		return sys.exit(0)
	return ANSWER

def getNumeros(DATA, FILTER, METER_ONE, LINK):
	COMPLETE, DEAD_ONE, FREE_ONE, PAY_ONE, FREE_TWO, PAY_TWO, METER_TWO = (0 for _ in range(7))
	ORIGINAL, PID, CAT = 'UNKNOWN', '00', 'Sport'
	if FILTER in LINK:
		if 'page=1' in LINK and DATA.get('meta', '') and str(DATA['meta'].get('total')).isdecimal():
			ORIGINAL, COMPLETE = LINK, int(DATA['meta']['total'])
		for each in DATA.get('data', []):
			if FILTER == 'livestreams' and each.get('currently_live', False) is True:
				if not str(each.get('price_in_cents')).isdecimal() and len([aa for aa in each.get('monetizations', '')]) == 0:
					FREE_ONE += 1
					if str(each.get('content_start_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdecimal():
						if datetime.now() > get_CentralTime(each['content_start_date']) + timedelta(hours=12): # Forgotten dead Links
							DEAD_ONE += 1 # 22:30 > 10:15+12h = 22:15
				if str(each.get('price_in_cents')).isdecimal() or len([cc for cc in each.get('monetizations', '')]) > 0:
					PAY_ONE += 1
			if FILTER == 'livestreams' and each.get('currently_live', False) is False:
				if not str(each.get('price_in_cents')).isdecimal() and len([dd for dd in each.get('monetizations', '')]) == 0:
					FREE_TWO += 1
				if str(each.get('price_in_cents')).isdecimal() or len([ee for ee in each.get('monetizations', '')]) > 0:
					PAY_TWO += 1
			if FILTER not in ['livestreams', 'sport-types']:
				if not str(each.get('price_in_cents')).isdecimal() and len([gg for gg in each.get('monetizations', '')]) == 0:
					FREE_ONE += 1
				if str(each.get('price_in_cents')).isdecimal() or len([hh for hh in each.get('monetizations', '')]) > 0:
					PAY_ONE += 1
			METER_TWO += 1
			PID = each.get('id', '00')
			CAT = cleaning(each['name'])
		debug_MS(f"(common.getNumeros[1]) COMBINATION XXX PAGE_NUMBER = {METER_ONE} || ENTRIES_SUM = {METER_TWO} XXX")
	return METER_ONE, ORIGINAL, COMPLETE, METER_TWO, DEAD_ONE, FREE_ONE, PAY_ONE, FREE_TWO, PAY_TWO, PID, CAT

def plugin_operate(MARKING):
	check_uno = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{{"addonid":"{MARKING}","properties":["enabled"]}}}}')
	answer_uno, answer_due = json.loads(check_uno), json.loads(f'{{"error": "{MARKING} NOT FOUND"}}')
	if not "error" in answer_uno.keys() and answer_uno.get('result', '') and answer_uno['result'].get('addon', {}).get('enabled', False) is False:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{MARKING}","enabled": true}}}}')
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

def get_CentralTime(info): # 2024-05-10T17:10:05.000000Z
	CONVERTED = datetime(*(time.strptime(info[:19], '%Y-%m-%dT%H:%M:%S')[0:6]))
	try:
		LOCAL_DATE = datetime.fromtimestamp(TGM(CONVERTED.timetuple()))
		assert CONVERTED.resolution >= timedelta(microseconds=1)
		LOCAL_DATE = LOCAL_DATE.replace(microsecond=CONVERTED.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		LOCAL_DATE = datetime.fromtimestamp(0) + timedelta(seconds=TGM(CONVERTED.timetuple()))
		LOCAL_DATE = LOCAL_DATE - timedelta(hours=datetime.timetuple(LOCAL_DATE).tm_isdst)
	return LOCAL_DATE

def charge(num, CATALOG):
	return sum([rate[num] for rate in CATALOG[:]])

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
		for wg in (('ä', 'ae'), ('Ä', 'Ae'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'oe'), ('ß', 'ss')):
			wrong = wrong.replace(*wg)
		wrong = wrong.strip()
	return wrong

def cleaning(text, STATEMENT=False):
	if text is not None:
		text = re.sub('\<.*?\>', '', text)
		for tx in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
			("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
			('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
			('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
			('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
			('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
			('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
			('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
			('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
			('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('+++', ''), ('++', ''),
			("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
			('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ("\\'", "'"), ('....', '')):
			text = text.replace(*tx)
		if STATEMENT and '#' in text or '@' in text or 'Facebook' in text:
			text = re.sub('(?:@[A-Za-z0-9äöü;,-_&   ]+|(?: - )?#[A-Za-z0-9äöü;,-_&   ]+)', '', text)
		text = text.strip()
	return text

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_ov20 else {}
	if KODI_ov20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
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
	if str(metadata.get('Aired'))[6:10].isdecimal():
		if KODI_ov20: vinfo.setYear(int(metadata['Aired'][6:10]))
		else: vinfo['Year'] = metadata['Aired'][6:10]
	if metadata.get('Genre', ''):
		if KODI_ov20: vinfo.setGenres([metadata['Genre']])
		else: vinfo['Genre'] = metadata['Genre']
	if metadata.get('Mediatype', ''):
		if KODI_ov20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	if KODI_ov20: vinfo.setStudios(['Sportdeutschland.tv'])
	else: vinfo['Studio'] = 'Sportdeutschland.tv'
	picture = metadata['Image'] if metadata.get('Image') not in ['', 'None', None] else icon
	listitem.setArt({'icon': icon, 'thumb': picture, 'poster': picture, 'fanart': defaultFanart})
	if metadata.get('Fanback', '') and not artpic in metadata['Fanback']:
		listitem.setArt({'fanart': metadata['Fanback']})
	if metadata.get('Reference') == 'Single':
		listitem.setProperty('IsPlayable', 'true')
	if not KODI_ov20: listitem.setInfo('Video', vinfo)
	return listitem
