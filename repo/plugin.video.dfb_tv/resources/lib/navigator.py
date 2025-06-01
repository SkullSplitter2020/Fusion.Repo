# -*- coding: utf-8 -*-

from .common import *
from .external.scrapetube import *


def mainMenu(EXTRA=None):
	debug_MS("(navigator.mainMenu) ------------------------------------------------ START = mainMenu -----------------------------------------------")
	if EXTRA is None:
		addDir({'mode': 'listVideos', 'extras': 'YOUT_STREAMS'}, create_entries({'Title': translation(30621), 'Plot': 'Live-Events und Aktuelles: Deutscher Fußball-Bund (DFB)'}))
		addDir({'url': BASE_YT.format(CHANNEL_CODE, 'UUfMo0xj-sbdzHuzxvKdu1hw'), 'extras': 'YT_FOLDER'}, create_entries({'Title': translation(30622), 'Plot': 'Neue Uploads: Deutscher Fußball-Bund (DFB)'}))
		TARGET = f"https://youtube.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&channelId={CHANNEL_CODE}&maxResults=50&key={PERS_TOKEN}"
		PAGE_NUMBER, NEXT_PAGE = 1, None
		while PAGE_NUMBER > 0:
			content = getContent(TARGET) if PAGE_NUMBER == 1 else getContent(NEXT_PAGE)
			for item in content.get('items', []):
				if item.get('kind', '') == 'youtube#playlist':
					debug_MS(f"(navigator.mainMenu[1]) xxxxx ENTRY-01 : {item} xxxxx")
					debug_MS("---------------------------------------------")
					title = cleaning(item['snippet']['title'])
					plot = (cleaning(item['snippet'].get('description', '')) or 'Offizieller YouTube Kanal des Deutschen Fußball-Bundes (DFB)')
					PYID = item.get('id', None)
					photo = (item['snippet']['thumbnails'].get('maxres', {}).get('url', '') or item['snippet']['thumbnails'].get('standard', {}).get('url', ''))
					numbers = item['contentDetails']['itemCount'] if item.get('contentDetails', '') and str(item['contentDetails'].get('itemCount')).isdecimal() else None
					name = translation(30623).format(title) if numbers is None else translation(30624).format(title, numbers)
					FETCH_UNO = create_entries({'Title': name, 'Plot': f'Playlist: {plot}', 'Image': photo})
					addDir({'url': BASE_YT.format(CHANNEL_CODE, PYID), 'extras': 'YT_FOLDER'}, FETCH_UNO)
			if content.get('nextPageToken', None):
				NEXT_PAGE, PAGE_NUMBER = f"{TARGET}&pageToken={content['nextPageToken']}", PAGE_NUMBER.__add__(1)
				debug_MS(f"(navigator.mainMenu[2]) PAGES ### NOW GET NEXTPAGE : {NEXT_PAGE} ###")
			else: 
				PAGE_NUMBER = 0
				break
	else:
		content = get_channel(channel_username=CHANNEL_NAME.split('@')[1], limit=40, sleep=1, content_type='streams') # mit 'get_channel' hier die Streams eines Channels abrufen
		for item in content:
			debug_MS(f"(navigator.mainMenu[2]) XXXXX ENTRY-02 : {item} XXXXX")
			debug_MS("---------------------------------------------")
			title, plot, running, announced = cleaning(item['title']['runs'][0]['text'], True), "", None, False
			PYID = item.get('videoId', None)
			try: running = item['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['text']['accessibility']['accessibilityData']['label']
			except: pass
			if running and running[:4] == 'LIVE':
				announced = True
				plot += translation(30625)
			elif item.get('upcomingEventData', '') and str(item['upcomingEventData'].get('startTime')).isdecimal():
				CIPHER = datetime(1970,1,1) + timedelta(seconds=TGM(time.localtime(int(item['upcomingEventData']['startTime']))))
				startCOMPLETE = CIPHER.strftime('%a{0} %d{0}%m{0}%Y {1} %H{2}%M').format( '.', '•', ':')
				for tt in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
					startCOMPLETE = startCOMPLETE.replace(*tt)
				announced = True
				plot +=  translation(30626).format(startCOMPLETE)
			elif item.get('publishedTimeText', '') and item['publishedTimeText'].get('simpleText', ''):
				plot += translation(30627).format(str(item['publishedTimeText']['simpleText']).replace(' gestreamt', '').replace('Streamed ', '').replace('vor ', 'Vor '))
			plot += cleaning(item['descriptionSnippet']['runs'][0]['text'], True)
			if announced is True and title[:4] == 'LIVE':
				name = translation(30628).format(title[4:])
			else: name = title[4:] if title[:4] == 'LIVE' else title
			photo = f"https://i.ytimg.com/vi/{PYID}/sddefault.jpg"
			addDir({'mode': 'playVideo', 'url': PYID}, create_entries({'Title': name, 'Plot': plot, 'Mediatype': 'episode', 'Image': photo, 'Reference': 'Single'}), False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playVideo(PLID):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	FINAL_URL, TEST_URL = (False for _ in range(2))
	debug_MS(f"(navigator.playVideo[1]) ***** TESTING - REDIRECTED : https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v={PLID} || (Youtube-Redirect-Test) *****")
	FINAL_URL = f"plugin://plugin.video.youtube/play/?video_id={PLID}"
	VERIFY = getContent(f"https://www.youtube.com/oembed?format=json&url=http://www.youtube.com/watch?v={PLID}", queries='TRACK', timeout=15)
	if VERIFY and VERIFY.status_code in [200, 201, 202] and re.search(r'''["']provider_url["']:["']https://www.youtube.com/["']''', VERIFY.text): TEST_URL = True
	if FINAL_URL and TEST_URL:
		log(f"(navigator.playVideo) StreamURL : {FINAL_URL}")
		LSM = xbmcgui.ListItem(path=FINAL_URL, offscreen=True)
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
	else:
		failing(f"(navigator.playVideo[2]) ##### Abspielen des Streams NICHT möglich #####\n ##### IDD : {PLID} || FINAL_URL : {FINAL_URL} #####\n ########## Das Youtube-Video wurde nicht gefunden !!! ##########")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
		xbmc.PlayList(1).clear()
		return dialog.notification(translation(30521).format('VIDEO'), translation(30524), icon, 10000)

def addDir(params, listitem, folder=True):
	if params.get('extras') == 'YT_FOLDER': uws = params.get('url')
	else: uws = build_mass(params)
	listitem.setPath(uws)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
