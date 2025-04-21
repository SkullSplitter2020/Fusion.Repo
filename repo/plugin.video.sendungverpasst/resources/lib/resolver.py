# -*- coding: utf-8 -*-

from .common import *


def ArdGetVideo(video_origin):
	debug_MS("(resolver.ArdGetVideo) ------------------------------------------------ START = ArdGetVideo -----------------------------------------------")
	(MASTERS, MEDIAS), (code_one, STREAM, FINAL_URL) = ([] for _ in range(2)), (False for _ in range(3))
	LANGUAGES = ['deu', 'ov']
	ARD_QUALITIES = ['Auto', 2560, 1920, 1280, 960, 640] # ARD_QUALITIES = ['auto', 5, 4, 3, 2, 1, 0]
	for code_one in video_origin.split('/'):
		try:
			testing = base64.urlsafe_b64decode(code_one + '=' * (len(code_one) % 4)).decode()
			if code_one and len(testing) > 5: break
		except: pass
	# https://api.ardmediathek.de/page-gateway/pages/ard/item/Y3JpZDovL3JhZGlvYnJlbWVuLmRlLzgyYzhkMjE0LTFhM2YtNDU3NC1iOWMwLTdjODlmYWIzNDYyNi9lcGlzb2RlL3VybjphcmQ6c2hvdzo2MjA5YjVhYmQ4ODZhN2Fj?devicetype=pc&embedded=true = Nicht immer Videoeinträge vorhanden !!!
	# https://api.ardmediathek.de/page-gateway/pages/ard/item/Y3JpZDovL3JhZGlvYnJlbWVuLmRlLzgyYzhkMjE0LTFhM2YtNDU3NC1iOWMwLTdjODlmYWIzNDYyNi9lcGlzb2RlL3VybjphcmQ6c2hvdzo2MjA5YjVhYmQ4ODZhN2Fj?embedded=true&mcV6=true = Alle Videoeinträge = Fremdsprachen, Deutsch Standard, Deutsch mit Audiodescription, Deutsch mit Unterttiteln
	debug_MS(f"(resolver.ArdGetVideo[1]) ##### REQUEST_ONE : {API_ARD}ard/item/{code_one}?embedded=true&mcV6=true #####")
	if code_one:
		content_one = getContent(f"{API_ARD}ard/item/{code_one}?embedded=true&mcV6=true", queries='TRACK')
		if content_one.status_code in [200, 201, 202]:
			DATA_ONE = content_one.json()
			debug_MS("++++++++++++++++++++++++")
			debug_MS(f"(resolver.ArdGetVideo[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
			debug_MS("++++++++++++++++++++++++")
			if DATA_ONE is not None and DATA_ONE.get('widgets', '') and len(DATA_ONE['widgets']) > 0:
				if DATA_ONE.get('coreAssetType', '') == 'SECTION' and len(DATA_ONE['widgets']) > 1 and 'teasers' in str(DATA_ONE['widgets'][1]):
					broadcast = DATA_ONE['widgets'][0].get('broadcastedOn', 'UNKNOWN')
					code_two = next(filter(lambda cx: cx.get('coreAssetType', '') == 'EPISODE' and broadcast in cx.get('broadcastedOn', ''), DATA_ONE['widgets'][1].get('teasers', [])), None)
					debug_MS(f"(resolver.ArdGetVideo[1]) ##### DETECTED CODE FOR REQUEST_TWO : {code_two['id'] if code_two else '!!! ERROR !!! NO RESULTS !!! ERROR !!!'} #####")
					if code_two:
						content_two = getContent(f"{API_ARD}ard/item/{code_two['id']}?embedded=false&mcV6=true", queries='TRACK')
						if content_two.status_code in [200, 201, 202]:
							DATA_TWO = content_two.json()
							debug_MS("++++++++++++++++++++++++")
							debug_MS(f"(resolver.ArdGetVideo[2]) XXXXX CONTENT-02 : {DATA_TWO} XXXXX")
							debug_MS("++++++++++++++++++++++++")
							if DATA_TWO is not None and DATA_TWO.get('widgets', '') and len(DATA_TWO['widgets']) > 0:
								full_video = DATA_TWO.get('widgets', [])
							else: full_video = DATA_ONE.get('widgets', [])
						else: full_video = DATA_ONE.get('widgets', [])
					else: full_video = DATA_ONE.get('widgets', [])
				else: full_video = DATA_ONE.get('widgets', [])
				for elem in full_video:
					if elem.get('mediaCollection', '') and len(elem['mediaCollection']) > 0:
						for each in elem['mediaCollection']['embedded']['streams']:
							formitaeten = each.get('media')
							if not isinstance(formitaeten, list):
								continue
							for item in formitaeten:
								if item.get('forcedLabel').lower() == 'auto' and item.get('mimeType').lower() in ['application/x-mpegurl', 'application/vnd.apple.mpegurl']:
									for found in LANGUAGES:
										for shorties in item.get('audios', {}):
											if shorties.get('languageCode').lower() == found and shorties.get('kind').lower() == 'standard':
												MASTERS.append({'url': item['url'], 'quality': item['maxHResolutionPx'], 'mimeType': item.get('mimeType').lower(), 'language': shorties['languageCode']})
								if item.get('forcedLabel').lower() != 'auto' and item.get('mimeType').lower() == 'video/mp4':
									for found in LANGUAGES:
										for shorties in item.get('audios', {}):
											if shorties.get('languageCode').lower() == found and shorties.get('kind').lower() == 'standard':
												numbers = 22 if shorties.get('languageCode').lower() == 'deu' else 11
												MEDIAS.append({'pos': numbers, 'url': item['url'], 'quality': item['maxHResolutionPx'], 'mimeType': item.get('mimeType').lower(), 'language': shorties['languageCode']})
												MEDIAS = sorted(MEDIAS, key=lambda px: (int(px['pos']), int(px['quality'])), reverse=True)
						debug_MS(f"(resolver.ArdGetVideo[3]) SORTED_LIST | M3U8 ### MASTER : {MASTERS} ###")
						debug_MS(f"(resolver.ArdGetVideo[3]) SORTED_LIST | MPP4 ### MEDIAS : {MEDIAS} ###")
					elif elem.get('blockedByFsk', '') is True:
						log("(resolver.ArdGetVideo[3]) AbspielLink-00 (ARD+3) : *ARD-Intern* Der angeforderte -VideoLink- wurde auf Grund von Alterbeschränkungen geblockt !!!")
						return dialog.notification(translation(30529), translation(30530), icon, 8000)
					elif elem.get('geoblocked', '') is True:
						log("(resolver.ArdGetVideo[3]) AbspielLink-00 (ARD+3) : *ARD-Intern* Der angeforderte -VideoLink- wurde auf Grund von Geo-Sperren geblockt !!!")
						return dialog.notification(translation(30529), translation(30531), icon, 8000)
	if (enableINPUTSTREAM or prefSTREAM == 0) and MASTERS:
		STREAM, FINAL_URL = 'HLS' if enableINPUTSTREAM else 'M3U8', MASTERS[0]['url']
		debug_MS(f"(resolver.ArdGetVideo[4]) ***** TAKE - {'Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'} - FILE (Ard.de+3) *****")
	if not FINAL_URL and MEDIAS:
		ARD_URL = f"https:{MEDIAS[0]['url']}" if MEDIAS[0]['url'][:4] != 'http' else MEDIAS[0]['url']
		STREAM, FINAL_URL = 'MP4', VideoBEST(ARD_URL, improve='DasErste') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		debug_MS(f"(resolver.ArdGetVideo[4]) ***** TAKE - (mp4) - FILE (Ard.de+3) : {ARD_URL} *****")
	return playRESOLVED(FINAL_URL, STREAM, 'ARD+3', 'ARD - Intern')

def DwGetVideo(video_origin):
	debug_MS("(resolver.DwGetVideo) ------------------------------------------------ START = DwGetVideo -----------------------------------------------")
	FINAL_URL, STREAM = (False for _ in range(2))
	content_one = getContent(video_origin, queries='TEXT')
	DW_PLAYER = re.compile(r'<source src="([^"]+)" type="(?:video/mp4|application/x-mpegURL|audio/mpeg)"', re.S).findall(content_one) # https://radiodownloaddw-a.akamaihd.net/Events/dwelle/dira/mp3/deu/FEE8E841_2.mp3
	if DW_PLAYER and len(DW_PLAYER[0]) > 0: # https://api.dw.com/api/detail/video/65556146 // Anforderung geht auch
		FINAL_URL, STREAM = DW_PLAYER[0], 'HLS' if enableINPUTSTREAM and 'm3u8' in DW_PLAYER[0] else 'M3U8' if not enableINPUTSTREAM and 'm3u8' in DW_PLAYER[0] else 'MP3' if 'mp3' in DW_PLAYER[0] else 'UNKNOWN'
	return playRESOLVED(FINAL_URL, STREAM, 'DeutscheWelle', 'DW - Intern')

def JoynGetVideo(video_origin):
	debug_MS("(resolver.JoynGetVideo) ------------------------------------------------ START = JoynGetVideo -----------------------------------------------")
	# ORIGINAL = https://www.joyn.de/play/serien/sweet-easy-on-tour/2-5-schwarzwaelder-himbeertorte-aus-mailand
	# FINAL_URL = plugin://plugin.video.joyn/?mode=play_video&video_id=a_pbbt48zdo6a&client_data=%7B%22genre%22%3A+%5B%5D%2C+%22startTime%22%3A+0%2C+%22videoId%22%3A+%22a_pbbt48zdo6a%22%2C+%22npa%22%3A+false%2C+%22duration%22%3A+1490000%2C+%22brand%22%3A+%22%22%7D&stream_type=VOD&title=Schwarzw%C3%A4lder+Himbeertorte+aus+Mailand&movie_id=None&path=%2Fserien%2Fsweet-easy-on-tour%2F2-5-schwarzwaelder-himbeertorte-aus-mailand
	video_id, movie_id, route, FINAL_URL = (None for _ in range(4))
	sweep = urlparse(video_origin)
	DATA_ONE = getContent(f"JOYN_REDIRECT@@{sweep.path.replace('play/', '')}.json", REF=video_origin)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(resolver.JoynGetVideo[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('pageProps', ''):
		if DATA_ONE['pageProps'].get('__N_REDIRECT', ''):
			DATA_VIDEO = getContent(f"JOYN_REDIRECT@@{DATA_ONE['pageProps']['__N_REDIRECT']}.json", REF=video_origin)
		else: DATA_VIDEO = DATA_ONE
		if DATA_VIDEO is not None and DATA_VIDEO.get('pageProps', '') and DATA_VIDEO['pageProps'].get('initialData', '') and DATA_VIDEO['pageProps']['initialData'].get('page', ''):
			SHORT = DATA_VIDEO['pageProps']['initialData']['page']
			if SHORT.get('movie', ''):
				video_id = SHORT['movie']['video']['id']
				runtime = SHORT['movie']['video']['duration'] if SHORT['movie']['video'].get('duration', '') else 0
				movie_id = SHORT['movie']['id']
				route = SHORT['movie']['path']
				title = SHORT['movie']['title'] if SHORT['movie'].get('title', '') else 'Unknown'
			elif SHORT.get('episode', ''):
				video_id = SHORT['episode']['video']['id']
				runtime = SHORT['episode']['video']['duration'] if SHORT['episode']['video'].get('duration', '') else 0
				route = SHORT['episode']['path']
				title = SHORT['episode']['title'] if SHORT['episode'].get('title', '') else 'Unknown'
			if video_id and route:
				CLIENT = f'{{"genre": [], "startTime": 0, "videoId": "{video_id}", "npa": false, "duration": {int(runtime) * 1000}, "brand": ""}}'
				debug_MS(f"(resolver.JoynGetVideo[2]) ##### CLIENT_DATA : {quote_plus(CLIENT)} #####")
				FINAL_URL = build_mass('plugin://plugin.video.joyn/', {'mode': 'play_video', 'movie_id': movie_id, 'video_id': video_id, 'stream_type': 'VOD', 'title': title, 'client_data': CLIENT, 'path': route})
				# JOYN-TRANSMIT : plugin://plugin.video.joyn/?mode=play_video&movie_id=&video_id=a_plf6fi6v9wq&stream_type=VOD&title=Young+Monaco&client_data=%7B%22genre%22%3A+%5B%5D%2C+%22startTime%22%3A+0%2C+%22videoId%22%3A+%22a_plf6fi6v9wq%22%2C+%22npa%22%3A+false%2C+%22duration%22%3A+2966000%2C+%22brand%22%3A+%22%22%7D&path=%2Fserien%2Fgalileo-stories%2F2024-32-young-monaco
	return playRESOLVED(FINAL_URL, 'TRANSMIT', 'JOYN - Mediathek', 'Joyn - Plugin')

def KikaGetVideo(video_origin):
	debug_MS("(resolver.KikaGetVideo) ------------------------------------------------ START = KikaGetVideo -----------------------------------------------")
	KiKA_QUALITIES = [5, 4, 3, 2, 1, 0, 'uhd', 'fhd', 'hd', 'veryhigh', 'high', 'med', 'low', 3840, 2560, 1920, 1280, 1024, 960, 852, 720, 640, 512, 480, 320]
	(M3U8, STREAM, FINAL_URL), (MEDIAS, SELECTION) = (False for _ in range(3)), ([] for _ in range(2))
	content_one = getContent(video_origin, queries='TEXT', REF='https://www.kika.de/').replace('\\', '')
	KiKA_PLAYER = re.compile(r'''["']featuredVideo["']:\{["']docType["']:["'](?:video|externalVideo)["'],["']id["']:["']([^"']+)["'],["']uuid["']''', re.S).findall(content_one)
	if KiKA_PLAYER and len(KiKA_PLAYER[0]) > 0:
		debug_MS(f"(resolver.KikaGetVideo[1]) EXTRACTED ##### videoFOUND : {KiKA_PLAYER[0]} #####")
		DATA_ONE = getContent(f"https://www.kika.de/_next-api/proxy/v1/videos/{KiKA_PLAYER[0]}/assets", REF=video_origin)
		for entry in DATA_ONE.get('assets', []):
			AUTO = (entry.get('quality', '') or entry.get('type', '') or 'Unknown')
			if AUTO == 'auto' and 'm3u8' in entry.get('url'):
				M3U8 = entry['url']
			MP4 = (entry.get('url', None) or None)
			TYPE = (entry.get('delivery', '') or entry.get('type', '') or 'Unknown')
			QUAL = (entry.get('width', None) or entry.get('frameWidth', None))
			if MP4 and QUAL:
				MEDIAS.append({'url': MP4, 'delivery': TYPE, 'quality': QUAL, 'document': 'WEB_VERSION'})
	if MEDIAS:
		debug_MS(f"(resolver.KikaGetVideo[2]) ORIGINAL_MP4 ### unsorted_LIST : {MEDIAS} ###")
		order_dict = {qual: index for index, qual in enumerate(KiKA_QUALITIES)}
		SELECTION = sorted(MEDIAS, key=lambda x: order_dict.get(x['quality'], float('inf')))
		debug_MS(f"(resolver.KikaGetVideo[2]) SORTED_MP4 ###### sorted_LIST : {SELECTION} ###")
	if (enableINPUTSTREAM or prefSTREAM == '0') and M3U8:
		STREAM, FINAL_URL = 'HLS' if enableINPUTSTREAM else 'M3U8', M3U8
		debug_MS(f"(resolver.KikaGetVideo[3]) ***** TAKE - {'Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'} - FILE (Kika.de) *****")
	if not FINAL_URL and SELECTION:
		KiKA_URL = f"https:{SELECTION[0]['url']}" if SELECTION[0]['url'][:4] != 'http' else SELECTION[0]['url']
		STREAM, FINAL_URL = 'MP4', KIKA_URL
		debug_MS(f"(resolver.KikaGetVideo[3]) ***** TAKE - (mp4) - FILE (Kika.de) : {KiKA_URL} *****")
	return playRESOLVED(FINAL_URL, STREAM, 'KiKA', 'KiKA - Intern')

def ZdfGetVideo(video_origin):
	debug_MS("(resolver.ZdfGetVideo) ------------------------------------------------ START = ZdfGetVideo -----------------------------------------------")
	DATA_ONE, TEASER, SECRET, videoFOUND = (False for _ in range(4))
	if video_origin.startswith('https://www.phoenix.de'):
		PHOE_PLAYER = re.compile('-a-([0-9]+).', re.S).findall(video_origin) # https://www.phoenix.de/sendungen/ereignisse/phoenix-plus/gefahren-der-ki-a-3179773.html?ref=3163173
		if PHOE_PLAYER and len(PHOE_PLAYER[0]) > 0:
			debug_MS(f"(resolver.ZdfGetVideo[1]) PHOENIX ##### TARGET : {PHOE_PLAYER[0]} #####")
			content_one = getContent(f"https://www.phoenix.de/response/id/{PHOE_PLAYER[0]}/refid/suche") # https://www.phoenix.de/response/id/3179773/refid/suche
			ABSAETZE = content_one['absaetze'][0]['content'] if content_one.get('absaetze', '') and content_one.get('absaetze', {})[0].get('content', '') and str(content_one['absaetze'][0]['content'])[:4].isdecimal() else None
			if ABSAETZE:
				NEW_URL = f"https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?id={ABSAETZE}&profile=player2"
				debug_MS(f"(resolver.ZdfGetVideo[2]) ##### REQUEST_URL : {NEW_URL} #####")
				DATA_ONE = getContent(NEW_URL) # https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?id=3180917&profile=player2
	else:
		content_one = getContent(video_origin, queries='TEXT').replace('\\', '')
		ZDF_PLAYER = re.compile(r'''(?s)data-zdfplayer-jsb=["'](?P<json>{.+?})["']''', re.S).findall(content_one)
		if ZDF_PLAYER:
			FIRST = json.loads(ZDF_PLAYER[0])
			TEASER, SECRET = FIRST['content'], FIRST['apiToken']
			NEW_URL = API_ZDF_OLD+TEASER if TEASER[:4] != 'http' else TEASER
			debug_MS(f"(resolver.ZdfGetVideo[1]) API_ZDF_OLD ##### TEASER : {NEW_URL} || SECRET : {SECRET} #####")
			DATA_ONE = getContent(NEW_URL, WAY='Api-Auth', AUTH=f"Bearer {SECRET}")
		elif not ZDF_PLAYER:
			TEMPLATE = re.compile(r'''["']__typename["']:["']VodMedia["'],["']ptmdTemplate["']:["']([^"']+)["'],["']vodMediaType["']:["']DEFAULT["'],''', re.S).findall(content_one)
			ANONICAL = re.compile(r'''["']__typename["']:["']Video["'],["']id["'].*?,["']canonical["']:["']([^"']+)["'],["'](?:episodeInfo|structuralMetadata)["']''', re.S).findall(content_one)
			SOPHORA = re.compile(r'''["']page_sophora_id["']:["']([^"']+)["'],["']page_type["']''', re.S).findall(content_one)
			CODING = re.compile(r'''["']tokens["']:\{["']videoToken["']:\{["']apiToken["']:["']([^"']+)["'],''', re.S).findall(content_one)
			if TEMPLATE and '/ptmd/' in TEMPLATE[0] and CODING:
				START_URL = 'https://api.3sat.de' if video_origin.startswith('https://www.3sat.de') else API_ZDF_OLD
				videoFOUND = START_URL+TEMPLATE[0].replace('{playerId}', 'ngplayer_2_5').replace('\/', '/')
				debug_MS(f"(resolver.ZdfGetVideo[1]) EXTRACTED ##### videoFOUND : {videoFOUND} || SECRET : {CODING[0]} #####")
				return ZdfExtractQuality(videoFOUND, 'Api-Auth', f"Bearer {CODING[0]}")
			elif (ANONICAL or SOPHORA) and CODING:
				videoFOUND = f"{API_ZDF_NEW}/document/{ANONICAL[0]}" if ANONICAL else f"{API_ZDF_NEW}/document/{SOPHORA[0]}"
				debug_MS(f"(resolver.ZdfGetVideo[1]) EXTRACTED ##### videoFOUND : {videoFOUND} || SECRET : {CODING[0]} #####")
				return ZdfExtractQuality(videoFOUND, 'Api-Auth', f"Bearer {CODING[0]}")
	if DATA_ONE and DATA_ONE.get('contentType', '') in ['clip', 'episode'] and not DATA_ONE.get('profile') == 'http://zdf.de/rels/not-found':
		START_URL = 'https://api.3sat.de' if TEASER and TEASER.startswith('https://api.3sat.de') else API_ZDF_OLD if TEASER and TEASER.startswith(API_ZDF_OLD) else ""
		BASIS = DATA_ONE['mainVideoContent']['http://zdf.de/rels/target']
		TOPICS = DATA_ONE['mainVideoContent']['http://zdf.de/rels/target']['streams']['default'] if BASIS.get('streams', '') and BASIS['streams'].get('default', '') else BASIS
		videoFOUND = START_URL+TOPICS['http://zdf.de/rels/streams/ptmd-template'].replace('{playerId}', 'ngplayer_2_5').replace('\/', '/')
		debug_MS(f"(resolver.ZdfGetVideo[2]) EXTRACTED ##### videoFOUND : {videoFOUND} #####")
		return ZdfExtractQuality(videoFOUND, 'Api-Auth', f"Bearer {SECRET}") if START_URL != "" else ZdfExtractQuality(videoFOUND, None, None)
	if videoFOUND is False:
		failing("(resolver.ZdfGetVideo[3]) AbspielLink-00 (ZDF+3) : *ZDF-Intern* Der angeforderte -VideoLink- existiert NICHT !!!")
		log("(resolver.ZdfGetVideo[3]) --- ENDE WIEDERGABE ANFORDERUNG ---")
		dialog.notification(translation(30521).format('ZDF - Intern'), translation(30528), icon, 8000)

def ZdfExtractQuality(content_three, PREFIX, TOKEN):
	debug_MS("(resolver.ZdfExtractQuality) ------------------------------------------------ START = ZdfExtractQuality -----------------------------------------------")
	DATA_TWO = getContent(content_three) if TOKEN is None else getContent(content_three, WAY=PREFIX, AUTH=TOKEN)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(resolver.ZdfExtractQuality[1]) XXXXX CONTENT-01 : {DATA_TWO} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	(MASTERS, MEDIAS), (STREAM, FINAL_URL) = ([] for _ in range(2)), (False for _ in range(2))
	M3U8_QUALITIES = ['auto', 'veryhigh', 'high', 'med']
	MPP4_QUALITIES = ['uhd', 'fhd', 'hd', 'veryhigh', 'high', 'low']
	if DATA_TWO is not None and DATA_TWO.get('priorityList', []) and len(DATA_TWO['priorityList']) > 0:
		for each in DATA_TWO.get('priorityList', []):
			formitaeten = each.get('formitaeten')
			if not isinstance(formitaeten, list):
				continue
			for item in formitaeten:
				if item.get('type') == 'h264_aac_ts_http_m3u8_http' and item.get('mimeType').lower() in ['application/x-mpegurl', 'application/vnd.apple.mpegurl']:
					for found in M3U8_QUALITIES:
						for quality in item.get('qualities', []):
							if found not in MASTERS and found == quality['quality']:
								MASTERS.append({'url': quality['audio']['tracks'][0]['uri'], 'quality': quality['quality'], 'mimeType': item.get('mimeType').lower(), 'language': quality['audio']['tracks'][0]['language']})
				if item.get('type') == 'h264_aac_mp4_http_na_na' and 'progressive' in item.get('facets', []) and item.get('mimeType').lower() == 'video/mp4':
					for found in MPP4_QUALITIES:
						for quality in item.get('qualities', []):
							if found not in MEDIAS and found == quality['quality']:
								MEDIAS.append({'url': quality['audio']['tracks'][0]['uri'], 'quality': quality['quality'], 'mimeType': item.get('mimeType').lower(), 'language': quality['audio']['tracks'][0]['language']})
		debug_MS(f"(resolver.ZdfExtractQuality[2/1]) SORTED_LIST | M3U8 ### MASTER : {MASTERS} ###")
		debug_MS(f"(resolver.ZdfExtractQuality[2/1]) SORTED_LIST | MPP4 ### MEDIAS : {MEDIAS} ###")
	elif DATA_TWO is not None and DATA_TWO.get('document', {}) and DATA_TWO['document'].get('formitaeten', []) and len(DATA_TWO['document']['formitaeten']) > 0:
		for item in DATA_TWO['document'].get('formitaeten', []):
			if item.get('type') == 'h264_aac_ts_http_m3u8_http' and item.get('class') == 'main' and item.get('mimeType').lower() in ['application/x-mpegurl', 'application/vnd.apple.mpegurl']:
				for found in M3U8_QUALITIES:
					if found not in MASTERS and found == item['quality']:
						MASTERS.append({'url': item['url'], 'quality': item['quality'], 'mimeType': item.get('mimeType').lower(), 'language': item['language']})
			if item.get('type') == 'h264_aac_mp4_http_na_na' and item.get('class') == 'main' and item.get('mimeType').lower() == 'video/mp4':
				for found in MPP4_QUALITIES:
					if found not in MEDIAS and found == item['quality']:
						MEDIAS.append({'url': item['url'], 'quality': item['quality'], 'mimeType': item.get('mimeType').lower(), 'language': item['language']})
		debug_MS(f"(resolver.ZdfExtractQuality[2/2]) SORTED_LIST | M3U8 ### MASTER : {MASTERS} ###")
		debug_MS(f"(resolver.ZdfExtractQuality[2/2]) SORTED_LIST | MPP4 ### MEDIAS : {MEDIAS} ###")
	if (enableINPUTSTREAM or prefSTREAM == 0) and MASTERS:
		STREAM, FINAL_URL = 'HLS' if enableINPUTSTREAM else 'M3U8', MASTERS[0]['url']
		debug_MS(f"(resolver.ZdfExtractQuality[3]) ***** TAKE - {'Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'} - FILE (Zdf.de+3) *****")
	if not FINAL_URL and MEDIAS:
		STREAM, FINAL_URL = 'MP4', VideoBEST(MEDIAS[0]['url'], improve='DasZweite') # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
		debug_MS(f"(resolver.ZdfExtractQuality[3]) ***** TAKE - (mp4) - FILE (Zdf.de+3) : {MEDIAS[0]['url']} *****")
	return playRESOLVED(FINAL_URL, STREAM, 'ZDF+3', 'ZDF - Intern')

def VideoBEST(highest, improve=False):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen // aktualisiert am 23.11.2024
	standards = [highest, '', '', ''] # Seite zur Überprüfung : https://github.com/mediathekview/MServer/blob/master/src/main/java/mServer/crawler/sender/zdf/ZdfVideoUrlOptimizer.java
	if improve == 'DasErste':
		route_one = (('/960', '/1280'), ('.l.mp4', '.xl.mp4'), ('_C.mp4', '_X.mp4'))
		route_two = (('/1280', '/1920'), ('_X.mp4', '_HD.mp4'), ('x720-50p-3200kbit.mp4', 'x1080-50p-5000kbit.mp4'), ('.hd.mp4', '.1080.mp4'), ('hd1080-avc720.mp4', 'hd1080-avc1080.mp4'))
		route_tree = (('/1920', '/3840'), ('_P.mp4', '_H.mp4'), ('.xl.mp4', '.xxl.mp4'))
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

def playRESOLVED(END_URL, PROTOCOL, MARKING, NOTE, MIME='application/vnd.apple.mpegurl', DRM_GUARD=False):
	if END_URL and PROTOCOL:
		LPM = xbmcgui.ListItem(path=END_URL, offscreen=True)
		if plugin_operate('inputstream.adaptive') and PROTOCOL in ['HLS', 'MPD']:
			IA_NAME, IA_SYSTEM, DRM_SPECIES = 'inputstream.adaptive', 'com.widevine.alpha', None
			IA_VERSION = re.sub(r'(~[a-z]+(?:.[0-9]+)?|\+[a-z]+(?:.[0-9]+)?$|[.^]+)', '', xbmcaddon.Addon(IA_NAME).getAddonInfo('version'))[:4]
			DRM_HEADERS = {'User-Agent': get_userAgent(), 'Content-Type': 'application/octet-stream'} if DRM_GUARD else {}
			LPM.setMimeType(MIME), LPM.setContentLookup(False), LPM.setProperty('inputstream', IA_NAME)
			if KODI_un21:
				LPM.setProperty(f"{IA_NAME}.manifest_type", PROTOCOL.lower()) # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
			if KODI_ov20:
				LPM.setProperty(f"{IA_NAME}.manifest_headers", f"User-Agent={get_userAgent()}") # On KODI v20 and above
			else: LPM.setProperty(f"{IA_NAME}.stream_headers", f"User-Agent={get_userAgent()}") # On KODI v19 and below
			if int(IA_VERSION) >= 2150 and PROTOCOL in ['HLS', 'MPD']:
				DRM_SPECIES = {'DRM_System': 'org.w3.clearkey'} if PROTOCOL == 'HLS' else {'DRM_System': IA_SYSTEM}
				if PROTOCOL == 'MPD' and DRM_GUARD:
					DRM_SPECIES = {'DRM_System': IA_SYSTEM, 'License_Link': DRM_GUARD, 'License_Headers': urlencode(DRM_HEADERS)}
				LPM.setProperty(f"{IA_NAME}.drm_legacy", '|'.join(DRM_SPECIES.values())) # Available from v.21.5.0 / Kodi 21 (Omega) - NEW simple method to configure a single DRM
			elif int(IA_VERSION) < 2150 and PROTOCOL == 'MPD':
				LPM.setProperty(f"{IA_NAME}.license_type", IA_SYSTEM)
				if DRM_GUARD:
					DRM_SPECIES = {'License_Link': DRM_GUARD, 'License_Headers': urlencode(DRM_HEADERS), 'Post_Data': 'R{SSM}|'}
					LPM.setProperty(f"{IA_NAME}.license_key", '|'.join(DRM_SPECIES.values())) # Below v.21.5.0 / Kodi 19+20 - OLD method to configure a single DRM
			if DRM_SPECIES: log(f"(resolver.playRESOLVED) INPUTSTREAM_VERSION: {IA_VERSION} >>>>> LICENSE : {'|'.join(DRM_SPECIES.values())} <<<<<")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
		log(f"(resolver.playRESOLVED) END-AbspielLink ({MARKING}) : {PROTOCOL}_stream : {END_URL}")
	else:
		failing(f"(resolver.playRESOLVED) AbspielLink-00 ({MARKING}) : *{NOTE}* Der angeforderte -VideoLink- existiert NICHT !!!")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
		xbmc.PlayList(1).clear()
		dialog.notification(translation(30521).format(NOTE), translation(30528), icon, 8000)
	log("(resolver.playRESOLVED) --- ENDE WIEDERGABE ANFORDERUNG ---")
