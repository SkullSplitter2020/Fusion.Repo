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
import random
import time
from datetime import datetime, date, timedelta
import requests
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
tempAPPLE						= xbmcvfs.translatePath(os.path.join(dataPath, 'tempAPPLE', '')).encode('utf-8').decode('utf-8')
appleFile								= xbmcvfs.translatePath(os.path.join(tempAPPLE, 'FREE_SECRET'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
regionPreset						= xbmc.getLanguage(xbmc.ISO_639_1, region=True)[-2:] # us
languagePreset					= xbmc.getLanguage(xbmc.ISO_639_1, region=True) # en-us
PERS_TOKEN						= str(addon.getSetting('pers_apiKey'))
BLACK_LISTING					= addon.getSetting('exclusion_words').split(',')
showDETAILS						= addon.getSetting('show_details') == 'true'
enableINFOS						= addon.getSetting('show_infos') == 'true'
infoStyle								= addon.getSetting('infoStyle')
infoDelay							= int(addon.getSetting('infoDelay'))
infoDuration						= int(addon.getSetting('infoDuration'))
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
applePushCountry				= addon.getSetting('apple_pushCountry') == 'true'
appleCountry						= addon.getSetting('apple_country')
deezerFoldersDisplay		= str(addon.getSetting('deezerFolders_count'))
deezerVideosDisplay			= str(addon.getSetting('deezerVideos_count'))
forceView							= addon.getSetting('force_viewing') == 'true'
viewIDGenres						= str(addon.getSetting('viewIDGenres'))
viewIDPlaylists					= str(addon.getSetting('viewIDPlaylists'))
viewIDVideos						= str(addon.getSetting('viewIDVideos'))
verify_connection				= (True if addon.getSetting('verify_ssl') == 'true' else False)
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
BPT_staticCODE					= addon.getSetting('new_staticCODE')
KODI_ov20							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21							= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
API_BEAT							= 'https://www.beatport.com/_next/data/' # NdtdJGkpmK6qY_YvtucCs # CODE of the Webpage
BASE_URL_BP						= 'https://www.beatport.com'
BASE_URL_BB						= 'https://www.billboard.com'
BASE_URL_DP					= 'https://www.deutsche-dj-playlist.de'
BASE_URL_HM					= 'https://hypem.com'
BASE_URL_MA					= 'https://amp-api.music.apple.com/v1'
BASE_URL_OC					= 'https://www.officialcharts.com'
BASE_URL_SZ						= 'https://www.shazam.com'
BASE_URL_DZ						= 'https://api.deezer.com/search'

appleRegion = appleCountry.lower() if applePushCountry and appleCountry != '' else regionPreset.lower() if len(regionPreset) > 1 else 'us'
appleLocale = languagePreset[:3].lower()+languagePreset[3:].upper() if len(languagePreset) > 3 else 'en-US'
shazamRegion = 'de' if regionPreset.upper() == 'DE' else 'en'

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

def TitleCase(nx):
	convert = re.sub(r"['\w]+", lambda word: word.group(0).capitalize(), quote_plus(nx))
	return unquote_plus(convert)

def cleanPlaylist():
	playlist = xbmc.PlayList(1)
	playlist.clear()
	return playlist

def fittme(text):
	return text.replace(' - ', ' ')

def preserve(store, data=None):
	if data is not None:
		with open(store, 'w') as topics:
			json.dump(data, topics, indent=2, sort_keys=True)
	else:
		with open(store, 'r') as topics:
			arrive = json.load(topics)
		return arrive

def cleanUmlaut(wrong):
	if wrong is not None:
		for wg in (('ä', 'ae'), ('Ä', 'Ae'), ('ã', 'a'), ('ü', 'ue'), ('Ü', 'Ue'), ('ö', 'oe'), ('Ö', 'Oe'), ('ß', 'ss')):
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
			('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '), ('<wbr>', ''),
			("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
			('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ('\\"', '"'),
			(' ft ', ' feat. '), (' FT ', ' feat. '), ('Ft.', 'feat.'), ('ft.', 'feat.'), (' FEAT ', ' feat. '), (' Feat ', ' feat. '), ('Feat.', 'feat.'), ('Featuring', 'feat.'), ('&reg;', '®'), ('™', '')):
			text = text.replace(*tx)
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
	if metadata.get('Mediatype', ''):
		if KODI_ov20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	picture = metadata.get('Image', icon)
	listitem.setArt({'icon': icon, 'thumb': picture, 'poster': picture})
	if useThumbAsFanart: listitem.setArt({'fanart': defaultFanart})
	if metadata.get('Reference') == 'Single': listitem.setProperty('IsPlayable', 'true')
	if not KODI_ov20: listitem.setInfo('Video', vinfo)
	return listitem
