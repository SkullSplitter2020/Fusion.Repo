# -*- coding: utf-8 -*-

from .common import *
from .external.scrapetube import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

def mainMenu(): # Auflistung der Kategorien zur Überprüfung: https://search.dfb.de/categories.json?
	addDir(translation(30601), icon, {'mode': 'listBroadcasts'})
	addDir(translation(30602), icon, {'mode': 'listSports_Men'})
	addDir(translation(30603), icon, {'mode': 'listSports_Women'})
	addDir(translation(30604), icon, {'mode': 'listBroadcasts', 'category': 'Amateurfußball'})
	addDir(translation(30605), icon, {'mode': 'listBroadcasts', 'category': 'Beachsoccer'})
	addDir(translation(30606), icon, {'mode': 'listBroadcasts', 'category': 'Futsal'})
	addDir(translation(30607), icon, {'mode': 'listBroadcasts', 'category': 'Fan Club'})
	addDir(translation(30608), icon, {'mode': 'listBroadcasts', 'category': 'English Videos'})
	addDir(translation(30609), icon, {'mode': 'listBroadcasts', 'category': 'Sportlich'})
	addDir(translation(30610), icon, {'mode': 'listBroadcasts', 'category': 'Talentförderung'})
	addDir(translation(30611), f"{artpic}basesearch.png", {'mode': 'SearchDFBTV'})
	if enableYOUTUBE:
		addDir(translation(30612), f"{artpic}youtube.png", {'mode': 'listPlaylists'})
	if enableADJUSTMENT:
		addDir(translation(30613), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30614), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSports_Men():
	debug_MS("(navigator.listSports_Men) -------------------------------------------------- START = listSports_Men --------------------------------------------------")
	addDir(translation(30701), icon, {'mode': 'listBroadcasts', 'category': 'Männer'})
	addDir(translation(30702), icon, {'mode': 'listBroadcasts', 'category': 'Männer - Ligen'})
	addDir(translation(30703), icon, {'mode': 'listBroadcasts', 'category': 'Männer-Nationalmannschaft'})
	addDir(translation(30704), icon, {'mode': 'listBroadcasts', 'category': 'Die Mannschaft'})
	addDir(translation(30705), icon, {'mode': 'listBroadcasts', 'category': 'Bundesliga'})
	addDir(translation(30706), icon, {'mode': 'listBroadcasts', 'category': '3. Liga'})
	addDir(translation(30707), icon, {'mode': 'listBroadcasts', 'category': 'A-Junioren-Bundesliga'})
	addDir(translation(30708), icon, {'mode': 'listBroadcasts', 'category': 'B-Junioren-Bundesliga'})
	addDir(translation(30709), icon, {'mode': 'listBroadcasts', 'category': 'DFB-Pokal'})
	addDir(translation(30710), icon, {'mode': 'listBroadcasts', 'category': 'U 21-Männer'})
	addDir(translation(30711), icon, {'mode': 'listBroadcasts', 'category': 'U20-Männer'})
	addDir(translation(30712), icon, {'mode': 'listBroadcasts', 'searching': 'junioren'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSports_Women():
	debug_MS("(navigator.listSports_Women) -------------------------------------------------- START = listSports_Women --------------------------------------------------")
	addDir(translation(30721), icon, {'mode': 'listBroadcasts', 'category': 'Frauen'})
	addDir(translation(30722), icon, {'mode': 'listBroadcasts', 'category': 'Frauen - Ligen'})
	addDir(translation(30723), icon, {'mode': 'listBroadcasts', 'category': 'Frauen Nationalmannschaft'})
	addDir(translation(30724), icon, {'mode': 'listBroadcasts', 'category': 'Google Pixel Frauen-Bundesliga'})
	addDir(translation(30725), icon, {'mode': 'listBroadcasts', 'category': 'FLYERALARM Frauen-Bundesliga'})
	addDir(translation(30726), icon, {'mode': 'listBroadcasts', 'category': 'DFB-Pokal der Frauen'})
	addDir(translation(30727), icon, {'mode': 'listBroadcasts', 'searching': 'juniorinnen'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(QUERY, CAT, PAGE, LIMIT):
	debug_MS("(navigator.listBroadcasts) -------------------------------------------------- START = listBroadcasts --------------------------------------------------")
	SWAPPED = f"q={QUERY}" if QUERY != 'NOTHING' else f"categories={quote(CAT)}"
	debug_MS(f"(navigator.listBroadcasts) ### TARGET = https://search.dfb.de/search/videos.json?{SWAPPED}&page={PAGE} ### CATEGORY = {CAT} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ###")
	plot, FOUND, PAGE_NUMBER, MAXIMUM = None, 0, int(PAGE), int(PAGE)+3
	while PAGE_NUMBER > 0:
		DATA_ONE = getUrl(f"https://search.dfb.de/search/videos.json?{SWAPPED}&page={PAGE_NUMBER}")
		for item in DATA_ONE.get('results', []):
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listBroadcasts[1]) XXXXX ENTRY-01 : {str(item)} XXXXX")
			FOUND += 1
			episID = str(item.get('guid', '00')).replace('video-', '')
			name = cleaning(item['title'])
			desc = cleaning(item.get('description', ''))
			genre = ' / '.join([cleaning(cto) for cto in item.get('category', '').split(',')]) if item.get('category', '') else 'Fußball'
			thumb = unquote(item.get('image_url', icon))
			photo = thumb[thumb.find('url=')+4:] if thumb != icon else thumb
			if str(item.get('pub_date'))[7:10].isdigit():
				plot = translation(30741).format(name, str(item['pub_date']), desc) if desc not in [None, ""] and desc != name else translation(30742).format(name, str(item['pub_date']))
				name = f"{item.get('pub_date')} - {name}"
			if plot is None: plot = desc
			debug_MS(f"(navigator.listBroadcasts[2]) ##### TITLE : {name} || episID : {episID} || FOTO : {photo} #####")
			if episID != '00': addLink(name, photo, {'mode': 'playVideo', 'url': episID}, plot, genre)
		debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
		if DATA_ONE.get('results', '') and len(DATA_ONE['results']) > 0 and DATA_ONE.get('total', '') and str(DATA_ONE['total']).isdigit() and int(DATA_ONE['total']) > int(PAGE_NUMBER+1)*int(LIMIT) and int(PAGE_NUMBER+1) <= int(MAXIMUM):
			NEXT_PAGE = f"https://search.dfb.de/search/videos.json?{SWAPPED}&page={int(PAGE_NUMBER)+1}"
			debug_MS(f"(navigator.listBroadcasts[3]) PAGES ### NOW GET NEXTPAGE FROM MAXIMUM : {NEXT_PAGE} ###")
			PAGE_NUMBER += 1
		else:
			if DATA_ONE.get('results', '') and len(DATA_ONE['results']) > 0 and DATA_ONE.get('total', '') and str(DATA_ONE['total']).isdigit() and int(DATA_ONE['total']) > int(PAGE_NUMBER)*int(LIMIT) and int(PAGE_NUMBER) == int(MAXIMUM):
				debug_MS(f"(navigator.listBroadcasts[4]) PAGES ### NOW SHOW NEXTPAGE ENTRY ... No.{int(PAGE_NUMBER)+1} ... ###")
				addDir(translation(30743).format(int(MAXIMUM) // 4 + 1), f"{artpic}nextpage.png", {'mode': 'listBroadcasts', 'searching': QUERY, 'category': CAT, 'page': int(PAGE_NUMBER)+1})
			PAGE_NUMBER = 0
			break
	if FOUND == 0:
		return dialog.notification(translation(30524).format('Einträge'), translation(30526).format(CAT), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchDFBTV():
	debug_MS("(navigator.SearchDFBTV) ------------------------------------------------ START = SearchDFBTV -----------------------------------------------")
	keyword = None
	if xbmcvfs.exists(SEARCHFILE):
		with open(SEARCHFILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30751), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote(keyword)
			with open(SEARCHFILE, 'w') as record:
				record.write(keyword)
	if keyword: return listBroadcasts(keyword, keyword, page, limit)
	return None

def listPlaylists(EXTRA):
	debug_MS("(navigator.listPlaylists) ------------------------------------------------ START = listPlaylists -----------------------------------------------")
	if EXTRA[:12] != 'YOUT_STREAMS':
		addDir(translation(30771), icon, {'mode': 'listPlaylists', 'extras': 'YOUT_STREAMS'}, plot='Live-Events und Aktuelles: Deutscher Fußball-Bund (DFB)')
		addDir(translation(30772), icon, {'url': BASE_YT.format(CHANNEL_CODE, 'UUfMo0xj-sbdzHuzxvKdu1hw'), 'extras': 'YT_FOLDER'}, plot='Neue Uploads: Deutscher Fußball-Bund (DFB)')
		DATA_ONE = get_videos(f"https://www.youtube.com/{CHANNEL_NAME}/playlists", 'https://www.youtube.com/youtubei/v1/browse', 'gridPlaylistRenderer', None, 1) # mit "get_videos" die Playlisten eines Channels abrufen
	else:
		DATA_ONE = get_videos(f"https://www.youtube.com/{CHANNEL_NAME}/streams", 'https://www.youtube.com/youtubei/v1/browse', 'videoRenderer', 40, 1) # mit "get_videos" hier die Streams eines Channels abrufen
	for item in DATA_ONE:
		debug_MS(f"(navigator.listPlaylists[1]) XXXXX ENTRY-01 : {str(item)} XXXXX")
		debug_MS("---------------------------------------------")
		title, plot, running = cleaning(item['title']['runs'][0]['text'], True), "", None
		PID = item.get('playlistId', None) if EXTRA[:12] != 'YOUT_STREAMS' else item.get('videoId', None)
		if EXTRA[:12] == 'YOUT_STREAMS':
			try: running = item['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['text']['accessibility']['accessibilityData']['label']
			except: pass
			if running and running[:4] == 'LIVE': plot += translation(30773)
			elif item.get('upcomingEventData', '') and str(item['upcomingEventData'].get('startTime')).isdigit():
				CIPHER = datetime(1970,1,1) + timedelta(seconds=TGM(time.localtime(int(item['upcomingEventData']['startTime']))))
				startCOMPLETE = CIPHER.strftime('%a{0} %d{0}%m{0}%Y {1} %H{2}%M').format( '.', '•', ':')
				for tt in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
					startCOMPLETE = startCOMPLETE.replace(*tt)
				plot +=  translation(30774).format(startCOMPLETE)
			elif item.get('publishedTimeText', '') and item['publishedTimeText'].get('simpleText', ''):
				plot += translation(30775).format(str(item['publishedTimeText']['simpleText']).replace(' gestreamt', '').replace('Streamed ', '').replace('vor ', 'Vor '))
			plot += cleaning(item['descriptionSnippet']['runs'][0]['text'], True)
		photo = item['thumbnail']['thumbnails'][0]['url'].split('?sqp=')[0].replace('hqdefault', 'maxresdefault')
		if title.lower().startswith(('allianz ', 'sporting')):
			photo = item['thumbnail']['thumbnails'][0]['url'].split('?sqp=')[0]
		numbers = str(item['videoCountShortText']['simpleText']) if item.get('videoCountShortText', '') and item['videoCountShortText'].get('simpleText', '') else None
		name = translation(30776).format(title, numbers) if numbers is not None else translation(30777).format(title)
		if EXTRA[:12] != 'YOUT_STREAMS' and PID:
			addDir(name, photo, {'url': BASE_YT.format(CHANNEL_CODE, PID), 'extras': 'YT_FOLDER'}, plot='Playlist: Offizieller YouTube Kanal des Deutschen Fußball-Bundes (DFB)')
		elif EXTRA[:12] == 'YOUT_STREAMS' and PID:
			addLink(title, photo, {'mode': 'playVideo', 'url': PID, 'extras': 'YOUT_PLAY'}, plot)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playVideo(SID, EXTRA):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	FINAL_URL, TEST_URL = (False for _ in range(2))
	if EXTRA[:9] == 'YOUT_PLAY':
		debug_MS(f"(navigator.playCODE[3]) ***** TESTING - REDIRECTED : https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v={SID} || (Youtube-Redirect-Test) *****")
		FINAL_URL = f"plugin://plugin.video.youtube/play/?video_id={SID}"
		VERIFY = getUrl(f"https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v={SID}", 'TRACK', timeout=15)
		if VERIFY and VERIFY.status_code in [200, 201, 202] and re.search(r'''["']provider_url["']:["']https://www.youtube.com/["']''', VERIFY.text): TEST_URL = True
	else:
		FINAL_URL = DfbGetVideo(SID, EXTRA)
		VERIFY = getUrl(FINAL_URL, 'TRACK', timeout=10) if FINAL_URL else None
		if VERIFY and VERIFY.status_code in [200, 201, 202]: TEST_URL = True # Test ob das Video abspielbar ist !!!
	if FINAL_URL and TEST_URL:
		log(f"(navigator.playVideo) FILTER : {EXTRA} || StreamURL : {FINAL_URL}")
		LSM = xbmcgui.ListItem(path=FINAL_URL)
		if EXTRA[:9] != 'YOUT_PLAY' and enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and 'm3u8' in FINAL_URL:
			LSM.setMimeType('application/vnd.apple.mpegurl')
			LSM.setProperty('inputstream', 'inputstream.adaptive')
			LSM.setProperty('inputstream.adaptive.manifest_type', 'hls')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
	elif FINAL_URL and not TEST_URL:
		failing(f"(navigator.playVideo[1]) ##### Abspielen des Streams NICHT möglich #####\n ##### IDD : {SID} || FINAL_URL : {FINAL_URL} #####\n ########## Der generierte Stream von *tv.dfb.de* ist DEFEKT !!! ##########")
		return dialog.notification(translation(30521).format('VIDEO'), translation(30527), icon, 10000)
	else:
		failing(f"(navigator.playVideo[2]) ##### Abspielen des Streams NICHT möglich ##### IDD : {SID} #####\n ########## KEINEN Stream-Eintrag auf der Webseite von *tv.dfb.de* gefunden !!! ##########")
		return dialog.notification(translation(30521).format('VIDEO'), translation(30528), icon, 8000)

def DfbGetVideo(TID, FILTER):
	VIDEO, TOKEN = (None for _ in range(2))
	'''
	LINK_UNO = https://tv.dfb.de/server/videoConfig.php?redirect=1&aaccepted=true&videoid=40552&partnerid=2180&language=de&format=iphone
	LINK_DUE = https://tv.dfb.de/server/streamAccess.php?videoId=38866&target=2&partner=2180&label=web_dfbtv&area=testarea&format=iphone
	LINK_TRE = https://streamaccess.unas.tv/hdflash2/vod/2180/38866.xml?streamid=38866&partnerid=2180&label=web_dfbtv&area=testarea&ident=1675600920240528173241×tamp=20240528153241&format=iphone&auth=2f3935df553ac0f8e653e9e6611e07bb
	CONTENT:
		auth = exp=1716917115~acl=*~hmac=9562172477215a003cec9023bf608400c43faefc05c122fa8d041e862d951d94&p=2180&u=&t=hdvideo&l=web_dfbtv&a=testarea&c=DE&e=38866&i=1675600920240528173241×tamp=20240528153241&k=&q=
		url = https://dsdfbvod.akamaized.net/i/hdflash/2023/231120_dfb_pk_,300,500,800,1200,.mp4.csmil/master.m3u8
	START_URL = https://dsdfbvod.akamaized.net/i/hdflash/2023/231120_dfb_pk_,
	END_URL = '?hdnea=exp=1716917115~acl=*~hmac=9562172477215a003cec9023bf608400c43faefc05c122fa8d041e862d951d94&p=2180&u=&t=hdvideo&l=web_dfbtv&a=testarea&c=DE&e=38866&i=1675600920240528173241×tamp=20240528153241&k=&q=
	'''
	LINK_UNO = STREAM_ACCESS.format(TID, COMPANY_ID)
	debug_MS(f"(navigator.DfbGetVideo[1]) ### LINK_ONE = {LINK_UNO} ### FILTER = {FILTER} ###")
	CHECK_ONE = getUrl(LINK_UNO)
	LINK_DUE = f"https:{CHECK_ONE['streamAccess']}" if CHECK_ONE.get('streamAccess', '') else None
	debug_MS(f"(navigator.DfbGetVideo[2]) ### LINK_TWO : {LINK_DUE} ###")
	if LINK_DUE:
		CHECK_TWO = getUrl(LINK_DUE)
		LINK_TRE = f"https:{CHECK_TWO['data']['stream-access'][0]}" if CHECK_TWO.get('status', '') == 'success' else None
		debug_MS(f"(navigator.DfbGetVideo[3]) ### LINK_THREE : {LINK_TRE} ###")
		if LINK_TRE:
			CHECK_THREE = getUrl(LINK_TRE, method='LOAD')
			for elem in ETCON.fromstring(CHECK_THREE).iter('token'):
				VIDEO, TOKEN = elem.attrib.get('url'), elem.attrib.get('auth')
			debug_MS(f"(navigator.DfbGetVideo[4]) ### RECEIVED_URL : {VIDEO} || RECEIVED_TOKEN : {TOKEN} ###")
	if VIDEO in [None, 'error']: return False
	START_URL = VIDEO[:VIDEO.find('_,')+2]
	END_URL = f"?hdnea={TOKEN}" if TOKEN not in [None, 'error'] else ""
	debug_MS(f"(navigator.DfbGetVideo[5]) ### COMPLETE_STREAM : {START_URL}XXX,.mp4.csmil/master.m3u8{END_URL} ###")
	if ',1200' in VIDEO and enableINPUTSTREAM: # _,300,500,800,1200,.mp4.csmil/master.m3u8?hdnea=
		return f'{START_URL}1200,.mp4.csmil/master.m3u8{END_URL}'
	elif ',1200' in VIDEO and prefQUALITY == 720:
		return f'{START_URL}1200,.mp4.csmil/master.m3u8{END_URL}'
	elif ',800' in VIDEO and prefQUALITY == 480:
		return f'{START_URL}800,.mp4.csmil/master.m3u8{END_URL}'
	elif ',500' in VIDEO and prefQUALITY == 360:
		return f'{START_URL}500,.mp4.csmil/master.m3u8{END_URL}'
	return False

def addDir(name, image, params={}, plot=None, folder=True):
	uws = params.get('url') if params.get('extras') == 'YT_FOLDER' else build_mass(params)
	LDM = xbmcgui.ListItem(name, offscreen=True)
	if plot in ['', 'None', None]: plot = ' '
	if KODI_ov20:
		vinfo = LDM.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setGenres(['Fußball']), vinfo.setStudios(['DFB-TV'])
	else:
		LDM.setInfo('Video', {'Title': name, 'Plot': plot, 'Genre': 'Fußball', 'Studio': 'DFB-TV'})
	LDM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and image != icon and not artpic in image:
		LDM.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, LDM, folder)

def addLink(name, image, params={}, plot=None, genre='Fußball'):
	uvz = build_mass(params)
	LEM = xbmcgui.ListItem(name)
	if plot in ['', 'None', None]: plot = ' '
	if KODI_ov20:
		vinfo = LEM.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setGenres([genre]), vinfo.setStudios(['DFB-TV']), vinfo.setMediaType('episode')
	else:
		LEM.setInfo('Video', {'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': 'DFB-TV', 'Mediatype': 'episode'})
	LEM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and image != icon and not artpic in image:
		LEM.setArt({'fanart': image})
	LEM.setProperty('IsPlayable', 'true')
	LEM.setContentLookup(False)
	LEM.addContextMenuItems([(translation(30654), 'Action(Queue)')])
	xbmcplugin.setPluginCategory(ADDON_HANDLE, 'Videos')
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uvz, LEM)
