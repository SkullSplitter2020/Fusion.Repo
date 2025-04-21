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
import _strptime
from datetime import datetime, date, timedelta
import requests
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
try: import StorageServer
except: from . import storageserverdummy as StorageServer
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HOST_AND_PATH                 = sys.argv[0]
ADDON_HANDLE                  = int(sys.argv[1])
dialog                                     = xbmcgui.Dialog()
addon                                     = xbmcaddon.Addon()
addon_id                               = addon.getAddonInfo('id')
addon_name                         = addon.getAddonInfo('name')
addon_version                      = addon.getAddonInfo('version')
addonPath                             = xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                                = xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
tempSPOT                              = xbmcvfs.translatePath(os.path.join(dataPath, 'tempSPOT', '')).encode('utf-8').decode('utf-8')
spotFile                                  = os.path.join(tempSPOT, 'SECRET')
defaultFanart                        = os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon                                        = os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic                                      = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
region                                     = xbmc.getLanguage(xbmc.ISO_639_1, region=True).split('-')[1]
myTOKEN                               = str(addon.getSetting('pers_apiKey'))
blackList                                = addon.getSetting('blacklist').split(',')
cachePERIOD                        = int(addon.getSetting('cache_rhythm'))
cache                                      = StorageServer.StorageServer(addon_id, cachePERIOD) # (Your plugin name, Cache time in hours)
showDETAILS                        = addon.getSetting('show_details') == 'true'
enableINFOS                         = addon.getSetting('showInfo') == 'true'
infoType                                 = addon.getSetting('infoType')
infoDelay                               = int(addon.getSetting('infoDelay'))
infoDuration                          = int(addon.getSetting('infoDuration'))
useThumbAsFanart               = addon.getSetting('useThumbAsFanart') == 'true'
itunesShowSubGenres         = addon.getSetting('itunesShowSubGenres') == 'true'
itunesForceCountry              = addon.getSetting('itunesForceCountry') == 'true'
itunesCountry                       = addon.getSetting('itunesCountry')
spotifyForceCountry             = addon.getSetting('spotifyForceCountry') == 'true'
spotifyCountry                      = addon.getSetting('spotifyCountry')
deezerSearchDisplay            = str(addon.getSetting('deezerSearch_count'))
deezerVideosDisplay            = str(addon.getSetting('deezerVideos_count'))
forceView                              = addon.getSetting('forceView') == 'true'
viewIDGenres                       = str(addon.getSetting('viewIDGenres'))
viewIDPlaylists                     = str(addon.getSetting('viewIDPlaylists'))
viewIDVideos                        = str(addon.getSetting('viewIDVideos'))
verify_ssl_connect               = (True if addon.getSetting('verify_ssl') == 'true' else False)
enableADJUSTMENT             = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                            = (xbmc.LOGINFO if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BPT_staticCODE                    = addon.getSetting('new_staticCODE')
KODI_ov20                           = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21                           = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
API_BEAT                              = 'https://www.beatport.com/_next/data/' # NdtdJGkpmK6qY_YvtucCs # CODE of the Webpage
BASE_URL_BP                      = 'https://www.beatport.com'
BASE_URL_BB                      = 'https://www.billboard.com'
BASE_URL_DDP                    = 'https://www.deutsche-dj-playlist.de'
BASE_URL_HM                      = 'https://hypem.com'
BASE_URL_OC                      = 'https://www.officialcharts.com'
BASE_URL_SZ                      = 'https://www.shazam.com/shazam/v3/en/GB/web/-/tracks'
BASE_URL_SY                      = 'https://api.spotify.com/v1'
BASE_URL_DZ                      = 'https://api.deezer.com/search'

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
	return xbmc.log('[{} v.{}]{}'.format(addon_id, addon_version, str(msg)), level)

def get_userAgent(REV='109.0', VER='112.0'):
	base = 'Mozilla/5.0 {} Gecko/20100101 Firefox/'+VER
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format('(X11; Linux arm64; rv:'+REV+')') # ARM based Linux
		return base.format('(X11; Linux x86_64; rv:'+REV+')') # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format('(Windows NT 10.0; Win64; x64; rv:'+REV+')') # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format('(Macintosh; Intel Mac OS X 10.15; rv:'+REV+')') # Mac OSX
	return base.format('(X11; Linux x86_64; rv:'+REV+')') # x64 Linux

def clearCache():
	debug_MS("(common.clearCache) -------------------------------------------------- START = clearCache --------------------------------------------------")
	debug_MS("(common.clearCache) ========== Lösche jetzt den Addon-Cache ==========")
	cache.delete('%')
	xbmc.sleep(1000)
	dialog.ok(addon_id, translation(30501))

def TitleCase(s):
	convert = re.sub(r"['\w]+", lambda word: word.group(0).capitalize(), quote_plus(s))
	return unquote_plus(convert)

def cleanPlaylist():
	playlist = xbmc.PlayList(1)
	playlist.clear()
	return playlist

def fitme(text):
	return text.replace(' - ', ' ')

def cleaning(text):
	if text is not None:
		for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
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
					text = text.replace(*n)
		text = text.strip()
	return text

params = dict(parse_qsl(sys.argv[2][1:]))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
target = unquote_plus(params.get('target', 'browse'))
limit = unquote_plus(params.get('limit', '0'))
extras = unquote_plus(params.get('extras', 'DEFAULT'))
transmit = unquote_plus(params.get('transmit', icon))
