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
SEARCHFILE						= xbmcvfs.translatePath(os.path.join(dataPath, 'search_string'))
WORKFILE							= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
channelFavsFile					= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_SDTV.json'))
menuFavsFile						= xbmcvfs.translatePath(os.path.join(dataPath, 'favorites_MENU.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
nowlive								= addon.getSetting('nowlive') == 'true'
upcoming							= addon.getSetting('upcoming') == 'true'
newest								= addon.getSetting('newest') == 'true'
sporting								= addon.getSetting('sporting') == 'true'
channeling							= addon.getSetting('channeling') == 'true'
teamsearch						= addon.getSetting('teamsearch') == 'true'
videosearch						= addon.getSetting('videosearch') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
enableBACK						= addon.getSetting('show_homebutton') == 'true'
PLACEMENT						= addon.getSetting('button_place')
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
IMG_categories					= 'https://img.sportdeutschland.tv/{}/300x300.webp'
IMG_assets						= 'https://img.sportdeutschland.tv/{}/1920x1080.webp'
API_BASE							= 'https://api.sportdeutschland.tv/api/stateless/frontend/'
API_PLAYER						= 'https://api.sportdeutschland.tv/api/frontend/asset-token/'
API_SEARCH						= 'https://search.sportdeutschland.tv/api/v1/'
BASE_URL							= 'https://sportdeutschland.tv/'
traversing							= Client(Client.CONFIG_SPORTDEUTSCHLAND)
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
			MESSAGE = '{"recordNotFound":true}' if 'not found' in str(py3_dec(response.data)).lower() else '{"ERROR_occurred":true}'
			if MESSAGE != '{"recordNotFound":true}': failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {str(pos)} === STATUS : {str(response.status)} === URL : {url} === DATA : {str(py3_dec(response.data))} #####")
			return MESSAGE
	with ThreadPoolExecutor() as executor:
		connector = urllib3.PoolManager(maxsize=15, block=True)
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
			if len(matching) == number or len(matching) > 10:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return json.dumps(COMBI_NEW, indent=2)

def getUrl(url, method='GET', ORI_REF=True, headers=None, cookies=None, allow_redirects=True, verify=True, stream=None, data=None, json=None):
	simple = requests.Session()
	ANSWER = None
	try:
		response = simple.get(url, headers=_header(ORI_REF), cookies=cookies, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
		ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
		debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {response.request.headers} ===")
		debug_MS("---------------------------------------------")
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

def get_CentralTime(info): # 2024-05-10T17:10:05.000000Z
	UTC_DATE = datetime(*(time.strptime(info[:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6]))
	try:
		LOCAL_DATE = datetime.fromtimestamp(TGM(UTC_DATE.timetuple()))
		assert UTC_DATE.resolution >= timedelta(microseconds=1)
		LOCAL_DATE = LOCAL_DATE.replace(microsecond=UTC_DATE.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		LOCAL_DATE = datetime.fromtimestamp(0) + timedelta(seconds=TGM(UTC_DATE.timetuple()))
		LOCAL_DATE = LOCAL_DATE - timedelta(hours=datetime.timetuple(LOCAL_DATE).tm_isdst)
	return LOCAL_DATE

def get_Number(DATA, FILTER, METER_ONE, LINK):
	COMPLETE, DEAD_ONE, FREE_ONE, PAY_ONE, FREE_TWO, PAY_TWO, METER_TWO = (0 for _ in range(7))
	ORIGINAL, PID, CAT = 'UNKNOWN', '00', 'Sport'
	if FILTER in LINK:
		if 'page=1' in LINK and DATA.get('meta', '') and str(DATA['meta'].get('total')).isdigit():
			ORIGINAL, COMPLETE = LINK, int(DATA['meta']['total'])
		for each in DATA.get('data', []):
			if FILTER == 'livestreams' and each.get('currently_live', False) is True:
				if not str(each.get('price_in_cents')).isdigit() and len([aa for aa in each.get('monetizations', '')]) == 0:
					FREE_ONE += 1
					if str(each.get('content_start_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdigit():
						if datetime.now() > get_CentralTime(each['content_start_date']) + timedelta(hours=12): # Forgotten dead Links
							DEAD_ONE += 1 # 22:30 > 10:15+12h = 22:15
				if str(each.get('price_in_cents')).isdigit() or len([cc for cc in each.get('monetizations', '')]) > 0:
					PAY_ONE += 1
			if FILTER == 'livestreams' and each.get('currently_live', False) is False:
				if not str(each.get('price_in_cents')).isdigit() and len([dd for dd in each.get('monetizations', '')]) == 0:
					FREE_TWO += 1
				if str(each.get('price_in_cents')).isdigit() or len([ee for ee in each.get('monetizations', '')]) > 0:
					PAY_TWO += 1
			if FILTER not in ['livestreams', 'sport-types']:
				if not str(each.get('price_in_cents')).isdigit() and len([gg for gg in each.get('monetizations', '')]) == 0:
					FREE_ONE += 1
				if str(each.get('price_in_cents')).isdigit() or len([hh for hh in each.get('monetizations', '')]) > 0:
					PAY_ONE += 1
			METER_TWO += 1
			PID = each.get('id', '00')
			CAT = cleaning(each['name'])
		debug_MS(f"(common.get_Number[1]) COMBINATION XXX PAGE_NUMBER = {METER_ONE} || ENTRIES_SUM = {METER_TWO} XXX")
	return METER_ONE, ORIGINAL, COMPLETE, METER_TWO, DEAD_ONE, FREE_ONE, PAY_ONE, FREE_TWO, PAY_TWO, PID, CAT

def charge(num, CATALOG):
	return sum([rate[num] for rate in CATALOG[:]])

def repair_umlaut(wrong):
	if wrong is not None:
		for n in (('ä', 'ae'), ('Ä', 'Ae'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'oe'), ('ß', 'ss')):
					wrong = wrong.replace(*n)
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
					('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '),
					("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
					('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ("\\'", "'")):
					text = text.replace(*tx)
		if STATEMENT and '#' in text or '@' in text or 'Facebook' in text:
			text = re.sub('(?:@[A-Za-z0-9äöü;,-_&   ]+|#[A-Za-z0-9äöü;,-_&   ]+)', '', text)
		text = text.strip()
	return text

params = dict(parse_qsl(sys.argv[2][1:]))
name = unquote_plus(params.get('name', ''))
pict = unquote_plus(params.get('pict', ''))
url = unquote_plus(params.get('url', ''))
code = unquote_plus(params.get('code', ''))
plot = unquote_plus(params.get('plot', ''))
section = unquote_plus(params.get('section', 'Sport'))
page = unquote_plus(params.get('page', '1'))
limit = unquote_plus(params.get('limit', '20'))
position = unquote_plus(params.get('position', '0'))
excluded = unquote_plus(params.get('excluded', '0'))
wanted = unquote_plus(params.get('wanted', '3'))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', ''))
extras = unquote_plus(params.get('extras', 'standard'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
