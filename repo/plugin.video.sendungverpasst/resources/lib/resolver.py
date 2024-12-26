# -*- coding: utf-8 -*-

from .common import *


def ArdGetVideo(videoURL):
	debug_MS("(resolver.ArdGetVideo) ------------------------------------------------ START = ArdGetVideo -----------------------------------------------")
	MEDIAS = []
	player_PAGE, STREAM, FINAL_URL = (False for _ in range(3))
	ARD_QUALITIES = ['auto', 5, 4, 3, 2, 1, 0]
	docuID = re.compile('ardmediathek.de/video/([A-Za-z0-9_]+)', re.S).findall(videoURL)	# https://www.ardmediathek.de/video/Y3JpZDovL3JhZGlvYnJlbWVuLmRlLzgyYzhkMjE0LTFhM2YtNDU3NC1iOWMwLTdjODlmYWIzNDYyNi9lcGlzb2RlL3VybjphcmQ6c2hvdzo2MjA5YjVhYmQ4ODZhN2Fj
	player_PAGE = f"{API_ARD}ard/item/{docuID[0]}?devicetype=pc&embedded=false" if docuID else False
	if player_PAGE is False: #https://api.ardmediathek.de/page-gateway/pages/ard/item/Y3JpZDovL3JhZGlvYnJlbWVuLmRlLzgyYzhkMjE0LTFhM2YtNDU3NC1iOWMwLTdjODlmYWIzNDYyNi9lcGlzb2RlL3VybjphcmQ6c2hvdzo2MjA5YjVhYmQ4ODZhN2Fj?devicetype=pc&embedded=false
		content_one = getUrl(videoURL, method='LOAD')
		docuLINK = re.compile(r'<script id="fetchedContextValue" type="application/json">.+?"href":"(https?://.*?/item/.*?)".+?</script>', re.S).findall(content_one)
		player_PAGE = docuLINK[0] if docuLINK else False
	debug_MS(f"(resolver.ArdGetVideo[1]) ##### videoPAGE : {str(player_PAGE)} #####")
	if player_PAGE:
		content_two = getUrl(player_PAGE, method='TRACK')
		if content_two.status_code in [200, 201, 202]:
			DATA_VIDEO = content_two.json()
			debug_MS("++++++++++++++++++++++++")
			debug_MS(f"(resolver.ArdGetVideo[2]) XXXXX CONTENT-02 : {str(DATA_VIDEO)} XXXXX")
			debug_MS("++++++++++++++++++++++++")
			if DATA_VIDEO is not None and DATA_VIDEO.get('widgets', '') and len(DATA_VIDEO['widgets']) > 0:
				for elem in DATA_VIDEO.get('widgets', []):
					if elem.get('type', '') == 'player_ondemand' and elem.get('mediaCollection', ''):
						SHORT = elem['mediaCollection']['embedded']['_mediaArray'][1] if len(elem['mediaCollection']['embedded']['_mediaArray']) > 1 else elem['mediaCollection']['embedded']['_mediaArray'][0]
						for found in ARD_QUALITIES:
							for quality in SHORT.get('_mediaStreamArray', []):
								if quality['_quality'] == found and quality.get('_stream', ''):
									if (enableINPUTSTREAM or prefSTREAM == '0') and quality['_quality'] == 'auto' and 'm3u8' in quality['_stream']:
										STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
										FINAL_URL = f"https:{quality['_stream']}" if quality['_stream'][:4] != 'http' else quality['_stream']
										debug_MS("(resolver.ArdGetVideo[3]) ***** TAKE - {} - FILE (Ard.de+3) *****".format('Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'))
									if quality['_quality'] != 'auto' and '.mp4' in quality['_stream']:
										MEDIAS.append({'url': quality['_stream'], 'quality': quality['_quality'], 'mimeType': 'mp4', 'height': quality.get('_height', 'Unknown')})
					elif elem.get('blockedByFsk', '') is True:
						log("(resolver.ArdGetVideo[3]) AbspielLink-00 (ARD+3) : *ARD-Intern* Der angeforderte -VideoLink- wurde auf Grund von Alterbeschränkungen geblockt !!!")
						return dialog.notification(translation(30529), translation(30530), icon, 8000)
					elif elem.get('geoblocked', '') is True:
						log("(resolver.ArdGetVideo[3]) AbspielLink-00 (ARD+3) : *ARD-Intern* Der angeforderte -VideoLink- wurde auf Grund von Geo-Sperren geblockt !!!")
						return dialog.notification(translation(30529), translation(30531), icon, 8000)
	if not FINAL_URL and MEDIAS:
		ARD_URL = f"https:{MEDIAS[0]['url']}" if MEDIAS[0]['url'][:4] != 'http' else MEDIAS[0]['url']
		debug_MS(f"(resolver.ArdGetVideo[4]) SORTED_LIST | MP4 ### MEDIAS : {str(MEDIAS)} ###")
		debug_MS(f"(resolver.ArdGetVideo[4]) ***** TAKE - (mp4) - FILE (Ard.de+3) : {ARD_URL} *****")
		STREAM, FINAL_URL = 'MP4', VideoBEST(ARD_URL, improve='DasErste') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	return playRESOLVED(FINAL_URL, STREAM, 'ARD+3', 'ARD - Intern')

def DwGetVideo(videoURL):
	debug_MS("(resolver.DwGetVideo) ------------------------------------------------ START = DwGetVideo -----------------------------------------------")
	FINAL_URL, STREAM = (False for _ in range(2))
	content_one = getUrl(videoURL, method='LOAD')
	docuID = re.compile(r'<source src="([^"]+)" type="(?:video/mp4|application/x-mpegURL|audio/mpeg)"', re.S).findall(content_one) # https://radiodownloaddw-a.akamaihd.net/Events/dwelle/dira/mp3/deu/FEE8E841_2.mp3
	FINAL_URL = docuID[0] if docuID else False # https://api.dw.com/api/detail/video/65556146 // Anforderung geht auch
	if FINAL_URL:
		STREAM ='HLS' if enableINPUTSTREAM and 'm3u8' in FINAL_URL else 'M3U8' if not enableINPUTSTREAM and 'm3u8' in FINAL_URL else 'MP3' if 'mp3' in FINAL_URL else 'UNKNOWN'
	return playRESOLVED(FINAL_URL, STREAM, 'DeutscheWelle', 'DW - Intern')

def JoynGetVideo(videoURL):
	debug_MS("(resolver.JoynGetVideo) ------------------------------------------------ START = JoynGetVideo -----------------------------------------------")
	# ORIGINAL = https://www.joyn.de/play/serien/sweet-easy-on-tour/2-5-schwarzwaelder-himbeertorte-aus-mailand
	# FINAL_URL = plugin://plugin.video.joyn/?mode=play_video&video_id=a_pbbt48zdo6a&client_data=%7B%22genre%22%3A+%5B%5D%2C+%22startTime%22%3A+0%2C+%22videoId%22%3A+%22a_pbbt48zdo6a%22%2C+%22npa%22%3A+false%2C+%22duration%22%3A+1490000%2C+%22brand%22%3A+%22%22%7D&stream_type=VOD&title=Schwarzw%C3%A4lder+Himbeertorte+aus+Mailand&movie_id=None&path=%2Fserien%2Fsweet-easy-on-tour%2F2-5-schwarzwaelder-himbeertorte-aus-mailand
	vid_id, mov_id, route, FINAL_URL = (None for _ in range(4))
	sweep = urlparse(videoURL)
	DATA_ONE = getUrl(f"JOYN_REDIRECT@@{sweep.path.replace('play/', '')}.json", REF=videoURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(resolver.JoynGetVideo[1]) XXXXX CONTENT-01 : {str(DATA_ONE)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('pageProps', ''):
		if DATA_ONE['pageProps'].get('__N_REDIRECT', ''):
			DATA_VIDEO = getUrl(f"JOYN_REDIRECT@@{DATA_ONE['pageProps']['__N_REDIRECT']}.json", REF=videoURL)
		else: DATA_VIDEO = DATA_ONE
		if DATA_VIDEO is not None and DATA_VIDEO.get('pageProps', '') and DATA_VIDEO['pageProps'].get('initialData', '') and DATA_VIDEO['pageProps']['initialData'].get('page', ''):
			SHORT = DATA_VIDEO['pageProps']['initialData']['page']
			if SHORT.get('movie', ''):
				vid_id = SHORT['movie']['video']['id']
				runtime = SHORT['movie']['video']['duration'] if SHORT['movie']['video'].get('duration', '') else 0
				mov_id = SHORT['movie']['id']
				route = SHORT['movie']['path']
				title = SHORT['movie']['title'] if SHORT['movie'].get('title', '') else 'Unknown'
			elif SHORT.get('episode', ''):
				vid_id = SHORT['episode']['video']['id']
				runtime = SHORT['episode']['video']['duration'] if SHORT['episode']['video'].get('duration', '') else 0
				route = SHORT['episode']['path']
				title = SHORT['episode']['title'] if SHORT['episode'].get('title', '') else 'Unknown'
			if vid_id and route:
				CLIENT = json.dumps({'genre': [], 'startTime': 0, 'videoId': '{}'.format(vid_id), 'npa': False, 'duration': int(runtime) * 1000, 'brand': ''})
				debug_MS(f"(resolver.JoynGetVideo[2]) ##### CLIENT_DATA : {quote_plus(CLIENT)} #####")
				FINAL_URL = '{0}?{1}'.format('plugin://plugin.video.joyn/', urlencode({'mode': 'play_video', 'video_id': vid_id, 'client_data': CLIENT, 'stream_type': 'VOD', 'title': title, 'movie_id': mov_id, 'path': route}))
	return playRESOLVED(FINAL_URL, 'TRANSMIT', 'JOYN - Mediathek', 'Joyn - Plugin')

def KikaGetVideo(videoURL):
	debug_MS("(resolver.KikaGetVideo) ------------------------------------------------ START = KikaGetVideo -----------------------------------------------")
	KiKA_QUALITIES = [5, 4, 3, 2, 1, 0, 'uhd', 'fhd', 'hd', 'veryhigh', 'high', 'med', 'low', 3840, 2560, 1920, 1280, 1024, 960, 852, 720, 640, 512, 480, 320]
	video_id, M3U8, FINAL_URL, STREAM = (False for _ in range(4))
	MEDIAS, bestMEDIA = ([] for _ in range(2))
	content_one = getUrl(videoURL, method='LOAD')
	target_KiKA = re.compile(r'</div></div></div><script id="__NEXT_DATA__" type="application/json">(?P<json>{.+?})</script></body></html>', re.S).findall(content_one)
	if target_KiKA:
		DATA_ONE = json.loads(target_KiKA[0])
		if DATA_ONE is not None and DATA_ONE.get('props', '') and DATA_ONE['props'].get('pageProps', '') and DATA_ONE['props']['pageProps'].get('docResponse', ''):
			if DATA_ONE['props']['pageProps']['docResponse'].get('videos', '') and len(DATA_ONE['props']['pageProps']['docResponse']['videos']) > 0:
				video_id = DATA_ONE['props']['pageProps']['docResponse']['videos'][0]['api']['id']
			elif DATA_ONE['props']['pageProps']['docResponse'].get('featuredVideo', '') and len(DATA_ONE['props']['pageProps']['docResponse']['featuredVideo']) > 0:
				video_id = DATA_ONE['props']['pageProps']['docResponse']['featuredVideo']['api']['id']
			debug_MS(f"(resolver.KikaGetVideo[1]) EXTRACTED ##### videoFOUND : {str(video_id)} #####")
			DATA_TWO = getUrl(f"https://www.kika.de/_next-api/proxy/v1/videos/{video_id}/assets")
			for entry in DATA_TWO.get('assets', []):
				AUTO = (entry.get('quality', '') or entry.get('type', '') or 'Unknown')
				if AUTO == 'auto' and 'm3u8' in entry.get('url'):
					M3U8 = entry['url']
				MP4 = (entry.get('url', None) or None)
				TYPE = (entry.get('delivery', '') or entry.get('type', '') or 'Unknown')
				QUAL = (entry.get('width', None) or entry.get('frameWidth', None))
				if MP4 and QUAL:
					MEDIAS.append({'url': MP4, 'delivery': TYPE, 'quality': QUAL, 'document': 'API_WEB'})
	if MEDIAS:
		debug_MS(f"(resolver.KikaGetVideo[1]) ORIGINAL_MP4 ### unsorted_LIST : {str(MEDIAS)} ###")
		order_dict = {qual: index for index, qual in enumerate(KiKA_QUALITIES)}
		bestMEDIA = sorted(MEDIAS, key=lambda x: order_dict.get(x['quality'], float('inf')))
		debug_MS(f"(resolver.KikaGetVideo[1]) SORTED_MP4 ###### sorted_LIST : {str(bestMEDIA)} ###")
	if (enableINPUTSTREAM or prefSTREAM == '0') and M3U8:
		STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
		FINAL_URL = M3U8
		debug_MS("(resolver.KikaGetVideo[2])  ~~~~~ TRY NUMBER ONE TO GET THE FINALURL TAKE - {} - FILE (Kika.de) ~~~~~".format('Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'))
	if not FINAL_URL and bestMEDIA:
		debug_MS("(resolver.KikaGetVideo[2]) ~~~~~ TRY NUMBER TWO TO GET THE FINALURL TAKE - (mp4) - FILE (Kika.de) ~~~~~")
		MP4_END = f"https:{bestMEDIA[0]['url']}" if bestMEDIA[0]['url'][:4] != 'http' else bestMEDIA[0]['url']
		STREAM, FINAL_URL = 'MP4', VideoBEST(MP4_END) # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	return playRESOLVED(FINAL_URL, STREAM, 'KiKA', 'KiKA - Intern')

def ZdfGetVideo(videoURL):
	debug_MS("(resolver.ZdfGetVideo) ------------------------------------------------ START = ZdfGetVideo -----------------------------------------------")
	DATA_ONE, TEASER, SECRET, videoFOUND = (False for _ in range(4))
	if videoURL.startswith('https://www.phoenix.de'):
		PHOEN_IDD = re.compile('-a-([0-9]+).', re.S).findall(videoURL) # https://www.phoenix.de/sendungen/ereignisse/phoenix-plus/gefahren-der-ki-a-3179773.html?ref=3163173
		if PHOEN_IDD:
			debug_MS(f"(resolver.ZdfGetVideo[1]) PHOENIX ##### TARGET : {str(PHOEN_IDD[0])} #####")
			FIRST = getUrl(f"https://www.phoenix.de/response/id/{PHOEN_IDD[0]}/refid/suche") # https://www.phoenix.de/response/id/3179773/refid/suche
			CODING = FIRST['absaetze'][0]['content'] if FIRST.get('absaetze', '') and FIRST.get('absaetze', {})[0].get('content', '') and str(FIRST['absaetze'][0]['content'])[:4].isdigit() else None
			if CODING:
				NEW_URL = f"https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?id={str(CODING)}&profile=player2"
				debug_MS(f"(resolver.ZdfGetVideo[2]) ##### REQUEST_URL : {NEW_URL} #####")
				DATA_ONE = getUrl(NEW_URL) # https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?id=3180917&profile=player2
	else:
		content_one = getUrl(videoURL, method='LOAD').replace('\\', '')
		ZDF_OLD = re.compile(r'''(?s)data-zdfplayer-jsb=["'](?P<json>{.+?})["']''', re.S).findall(content_one)
		if ZDF_OLD:
			FIRST = json.loads(ZDF_OLD[0])
			TEASER, SECRET = FIRST['content'], FIRST['apiToken']
			debug_MS(f"(resolver.ZdfGetVideo[1]) ZDF_OLD ##### TEASER : {TEASER} || SECRET : {SECRET} #####")
		elif not ZDF_OLD:
			CONTENT = re.compile(r'''["']config["']:\{["']content["']:["']([^"']+)["'],''', re.S).findall(content_one)
			CODING = re.compile(r'''["']tokens["']:\{["']videoToken["']:\{["']apiToken["']:["']([^"']+)["'],''', re.S).findall(content_one)
			if CONTENT and CODING:
				debug_MS(f"(resolver.ZdfGetVideo[1]) ZDF_NEW ##### TEASER : {API_ZDF}/content/documents/{CONTENT[0]}.json || SECRET : {CODING[0]} #####")
				TEASER, SECRET = f"{API_ZDF}/content/documents/{CONTENT[0]}.json", CODING[0]
		if TEASER and SECRET:
			NEW_URL = API_ZDF+TEASER if TEASER[:4] != 'http' else TEASER
			debug_MS(f"(resolver.ZdfGetVideo[2]) ##### REQUEST_URL : {NEW_URL} #####")
			DATA_ONE = getUrl(NEW_URL, WAY='Api-Auth', AUTH=f"Bearer {SECRET}")
	if DATA_ONE and DATA_ONE.get('contentType', '') in ['clip', 'episode'] and not DATA_ONE.get('profile') == 'http://zdf.de/rels/not-found':
		START_URL = 'https://api.3sat.de' if TEASER and TEASER.startswith('https://api.3sat.de') else 'https://api.zdf.de' if TEASER and TEASER.startswith('https://api.zdf.de') else ""
		BASIS = DATA_ONE['mainVideoContent']['http://zdf.de/rels/target']
		TOPICS = DATA_ONE['mainVideoContent']['http://zdf.de/rels/target']['streams']['default'] if BASIS.get('streams', '') and BASIS['streams'].get('default', '') else BASIS
		videoFOUND = START_URL+TOPICS['http://zdf.de/rels/streams/ptmd-template'].replace('{playerId}', 'ngplayer_2_5').replace('\/', '/')
		debug_MS(f"(resolver.ZdfGetVideo[3]) ##### videoFOUND : {videoFOUND} #####")
		return ZdfExtractQuality(videoFOUND, 'Api-Auth', f"Bearer {SECRET}") if START_URL != "" else ZdfExtractQuality(videoFOUND, None, None)
	if videoFOUND is False:
		failing("(resolver.ZdfGetVideo[4]) AbspielLink-00 (ZDF+3) : *ZDF-Intern* Der angeforderte -VideoLink- existiert NICHT !!!")
		log("(resolver.ZdfGetVideo[4]) --- ENDE WIEDERGABE ANFORDERUNG ---")
		dialog.notification(translation(30521).format('ZDF - ', 'Intern'), translation(30528), icon, 8000)

def ZdfExtractQuality(content_three, PREFIX, TOKEN):
	debug_MS("(resolver.ZdfExtractQuality) ------------------------------------------------ START = ZdfExtractQuality -----------------------------------------------")
	DATA_TWO = getUrl(content_three) if TOKEN is None else getUrl(content_three, WAY=PREFIX, AUTH=TOKEN)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(resolver.ZdfExtractQuality[1]) XXXXX CONTENT-01 : {str(DATA_TWO)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	MEDIAS = []
	STREAM, FINAL_URL = (False for _ in range(2))
	M3U8_QUALITIES = ['auto', 'veryhigh', 'high', 'med']
	MP4_QUALITIES = ['uhd', 'fhd', 'hd', 'veryhigh', 'high', 'low']
	if DATA_TWO is not None:
		for each in DATA_TWO.get('priorityList', []):
			formitaeten = each.get('formitaeten')
			if not isinstance(formitaeten, list):
				continue
			for item in formitaeten:
				if (enableINPUTSTREAM or prefSTREAM == '0') and item.get('type') == 'h264_aac_ts_http_m3u8_http' and item.get('mimeType').lower() == 'application/x-mpegurl':
					for found in M3U8_QUALITIES:
						for quality in item.get('qualities', []):
							if quality['quality'] == found:
								MEDIAS.append({'url': quality['audio']['tracks'][0]['uri'], 'quality': quality['quality'], 'mimeType': item.get('mimeType').lower(), 'language': quality['audio']['tracks'][0]['language']})
					debug_MS(f"(resolver.ZdfExtractQuality[2]) SORTED_LIST | M3U8 ### MEDIAS : {str(MEDIAS)} ###")
					STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
					FINAL_URL = MEDIAS[0]['url']
					debug_MS("(resolver.ZdfExtractQuality[2]) ***** TAKE - {} - FILE (Zdf.de+3) *****".format('Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'))
				if not FINAL_URL and item.get('type') == 'h264_aac_mp4_http_na_na' and 'progressive' in item.get('facets', []) and item.get('mimeType').lower() == 'video/mp4':
					for found in MP4_QUALITIES:
						for quality in item.get('qualities', []):
							if quality['quality'] == found:
								MEDIAS.append({'url': quality['audio']['tracks'][0]['uri'], 'quality': quality['quality'], 'mimeType': item.get('mimeType').lower(), 'language': quality['audio']['tracks'][0]['language']})
					debug_MS(f"(resolver.ZdfExtractQuality[3]) SORTED_LIST | MP4 ### MEDIAS : {str(MEDIAS)} ###")
					debug_MS(f"(resolver.ZdfExtractQuality[3]) ***** TAKE - (mp4) - FILE (Zdf.de+3) : {MEDIAS[0]['url']} *****")
					STREAM, FINAL_URL = 'MP4', VideoBEST(MEDIAS[0]['url'], improve='DasZweite') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	return playRESOLVED(FINAL_URL, STREAM, 'ZDF+3', 'ZDF - Intern')

def VideoBEST(highest, improve=False):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen // aktualisiert am 28.03.2023
	standards = [highest, '', '', ''] # Seite zur Überprüfung : https://github.com/mediathekview/MServer/blob/master/src/main/java/mServer/crawler/sender/zdf/ZdfVideoUrlOptimizer.java
	if improve == 'DasErste':
		route_one = (('/960', '/1280'), ('.hq.mp4', '.hd.mp4'), ('.l.mp4', '.xl.mp4'), ('_C.mp4', '_X.mp4'))
		route_two = (('/1280', '/1920'), ('.xl.mp4', '.xxl.mp4'))
		route_tree = (('/1920', '/3840'), ('.xl.mp4', '.xxl.mp4'))
	elif improve == 'DasZweite':
		route_one = (('808k_p11v15', '2360k_p35v15'), ('1456k_p13v11', '2328k_p35v11'), ('1456k_p13v12', '2328k_p35v12'), ('1496k_p13v13', '2328k_p35v13'), ('1496k_p13v14', '2328k_p35v14'), ('1628k_p13v15', '2360k_p35v15'),
								('1628k_p13v17', '2360k_p35v17'), ('2256k_p14v11', '2328k_p35v11'), ('2256k_p14v12', '2328k_p35v12'), ('2296k_p14v13', '2328k_p35v13'), ('2296k_p14v14', '2328k_p35v14'))
		route_two = (('2328k_p35v12', '3328k_p36v12'), ('2328k_p35v13', '3328k_p36v13'), ('2328k_p35v14', '3328k_p36v14'), ('2360k_p35v15', '3360k_p36v15'), ('2360k_p35v17', '3360k_p36v17'))
		route_tree = (('3360k_p36v15', '4692k_p72v16'), ('3360k_p36v17', '6660k_p37v17'))
	standards[1] = reduce(lambda m, kv: m.replace(*kv), route_one, standards[0])
	standards[2] = reduce(lambda n, kv: n.replace(*kv), route_two, standards[1])
	standards[3] = reduce(lambda o, kv: o.replace(*kv), route_tree, standards[2])
	if standards[0] not in [standards[1], standards[2], standards[3]]:
		for xy, element in enumerate(reversed(standards), 1):
			try:
				code = urlopen(element, timeout=6).getcode()
				if code in [200, 201, 202]:
					return element
			except: pass
	return highest

def playRESOLVED(END_URL, VERS, MARKING, NOTE, MIME='application/vnd.apple.mpegurl', LICE=None):
	if END_URL and VERS:
		LSM = xbmcgui.ListItem(path=END_URL)
		if ADDON_operate('inputstream.adaptive') and VERS in ['HLS', 'MPD']:
			LSM.setMimeType(MIME)
			LSM.setProperty('inputstream', 'inputstream.adaptive')
			if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
				LSM.setProperty('inputstream.adaptive.manifest_type', VERS.lower())
			if KODI_ov20:
				LSM.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={get_userAgent()}") # On KODI v20 and above
			else:
				LSM.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={get_userAgent()}") # On KODI v19 and below
			if LICE:
				LSM.setProperty('inputstream.adaptive.license_key', LICE)
				debug_MS(f"(resolver.playRESOLVED) LICENSE : {LICE}")
				LSM.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log(f"(resolver.playRESOLVED) END-AbspielLink ({MARKING}) : {VERS}_stream : {END_URL}")
	else:
		failing(f"(resolver.playRESOLVED) AbspielLink-00 ({MARKING}) : *{NOTE}* Der angeforderte -VideoLink- existiert NICHT !!!")
		dialog.notification(translation(30521).format(NOTE, ''), translation(30528), icon, 8000)
	log("(resolver.playRESOLVED) --- ENDE WIEDERGABE ANFORDERUNG ---")
