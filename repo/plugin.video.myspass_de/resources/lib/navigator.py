# -*- coding: utf-8 -*-

from .common import *
config = traversing.get_config()


def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	addDir({'mode': 'listFavorites'}, create_entries({'Title': translation(30601), 'Image': f"{artpic}favourites.png"}))
	NUMBER, DATA_ONE = 0, getContent(config['START_VIEW'].format(API_VANILLA, 'homepage'), AUTH=VANILLA_TOKEN)
	for item in DATA_ONE.get('data', []):
		THEME_CID = item['id']
		TITLE = cleaning(item['attributes']['title']).replace('Hero', translation(30602))
		FORMAT = [check.get('video', '') for check in item['attributes']['items'] if item.get('attributes', {}) and \
			item['attributes'].get('items', {}) and check.get('video') and len(check['video']) > 0]
		INSTANCE = 'listEpisodes' if item.get('attributes', {}) and item['attributes'].get('items', {}) and \
			((FORMAT and len(FORMAT) == len(item['attributes']['items'])) or (item['attributes']['title'] == 'Hero')) else 'listShows'
		NAME, NUMBER = None if INSTANCE == 'listEpisodes' else TITLE, NUMBER.__add__(1)
		if item['attributes'].get('page', '').upper() == 'HOMEPAGE':
			addDir({'mode': INSTANCE, 'target': 'ENTRIES_HOME', 'name': NAME, 'code': THEME_CID, 'number': NUMBER}, create_entries({'Title': f"[B]{TITLE}[/B]"}))
		debug_MS(f"(navigator.mainMenu[2]) ### ACTION : {INSTANCE} || NAME : {TITLE} || THEME_CID : {THEME_CID} || LIST_CID : {NUMBER} ###")
	addDir({'mode': 'listShows', 'target': 'ENTRIES_VIDEO', 'name': 'Alle Sendungen', 'code': 1}, create_entries({'Title': translation(30603)}))
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30609), 'Image': f"{artpic}settings.png"}), False)
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive'):
			addDir({'mode': 'iConfigs'}, create_entries({'Title': translation(30610), 'Image': f"{artpic}settings.png"}), False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listShows(TARGET, NAME, CAT_CID):
	debug_MS("(navigator.listShows) -------------------------------------------------- START = listShows --------------------------------------------------")
	debug_MS(f"(navigator.listShows) ### TARGET = {TARGET} ### NAME = {NAME} ### CAT_CID = {CAT_CID} ###")
	DATA_ONE, COMBINATION, FOUND, UNIKAT = {}, [], 0, set()
	DATA_ONE = getContent(config['START_VIEW'].format(API_VANILLA, 'homepage'), AUTH=VANILLA_TOKEN) if TARGET == 'ENTRIES_HOME' else \
		getContent(config['PAGE_VIEW'].format(API_VANILLA, 'video'), AUTH=VANILLA_TOKEN)
	for item in DATA_ONE.get('data', []):
		if int(item.get('id', 0)) == int(CAT_CID):
			ELEMENTS = item['attributes'].get('items', []) if TARGET == 'ENTRIES_HOME' else item['attributes']['formats'].get('data', [])
			for each in ELEMENTS:
				debug_MS(f"(navigator.listShows[1]) xxxxx EACH-01 : {each} xxxxx")
				SHORT = each['format']['data'] if TARGET == 'ENTRIES_HOME' else each
				SHOW_CID = SHORT['id']
				if SHOW_CID in ['', 0, None] or SHOW_CID in UNIKAT:
					debug_MS("~~~~~~~~~~~~~~~~~~~~~~~~ THIS SHOW IS DOUBLE - REMOVED ~~~~~~~~~~~~~~~~~~~~~~~~")
					continue
				UNIKAT.add(SHOW_CID)
				FOUND += 1
				TITLE = cleaning(SHORT['attributes']['name'])
				PLOT = get_Description(SHORT.get('attributes', {}))
				THUMB = SHORT['attributes']['keyvisual_16_9']['data']['attributes']['url'] if SHORT['attributes'].get('keyvisual_16_9', {}) and \
					SHORT['attributes']['keyvisual_16_9'].get('data', {}) and SHORT['attributes']['keyvisual_16_9']['data'].get('attributes', {}) and \
					SHORT['attributes']['keyvisual_16_9']['data']['attributes'].get('url', '') else None
				POSTER = SHORT['attributes']['keyvisual_5_8']['data']['attributes']['url'] if SHORT['attributes'].get('keyvisual_5_8', {}) and \
					SHORT['attributes']['keyvisual_5_8'].get('data', {}) and SHORT['attributes']['keyvisual_5_8']['data'].get('attributes', {}) and \
					SHORT['attributes']['keyvisual_5_8']['data']['attributes'].get('url', '') else None
				debug_MS(f"(navigator.listShows[2]) ### NAME : {TITLE} || SHOW_CID : {SHOW_CID} || THUMB : {THUMB} ###")
				debug_MS("---------------------------------------------")
				COMBINATION.append([TITLE, PLOT, THUMB, POSTER, SHOW_CID])
	if COMBINATION and FOUND > 0:
		for TITLE, PLOT, THUMB, POSTER, SHOW_CID in sorted(COMBINATION, key=lambda vsx: cleanUmlaut(vsx[0]).lower()):
			operation = 'adding'
			if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
				for article in preserve(FAVORIT_FILE):
					if article.get('Cid') == str(SHOW_CID): operation = 'skipping'
			FETCH_UNO = context = {'Cid': SHOW_CID, 'Title': TITLE, 'Plot': PLOT, 'Image': THUMB, 'Poster': POSTER}
			addDir({'mode': 'listSeasons', 'target': SHOW_CID, 'name': TITLE, 'picture': THUMB}, create_entries(FETCH_UNO), True, context, operation)
	else:
		failing(f'(navigator.listShows) ##### NO SHOWS_LIST - NO ENTRY FOR: "{NAME}" FOUND #####')
		return dialog.notification(translation(30524), translation(30526).format(NAME), icon, 10000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(TARGET, SERIE, IMG):
	debug_MS("(navigator.listSeasons) -------------------------------------------------- START = listSeasons --------------------------------------------------")
	debug_MS(f"(navigator.listSeasons) ### TARGET = {TARGET} ### SERIE = {SERIE} ### THUMB = {IMG} ###")
	ELEMENTS, COMBINATION, FOUND, UNIKAT = None, [], 0, set()
	DATA_ONE = getContent(config['SEAS_VIEW'].format(API_VANILLA, TARGET), AUTH=VANILLA_TOKEN)
	debug_MS(f"(navigator.listSeasons[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('data', {}) and DATA_ONE['data'].get('attributes', {}):
		SHORT = DATA_ONE['data']['attributes']
		if SHORT.get('seasons', {}) and SHORT['seasons'].get('data', ''):
			ELEMENTS = SHORT['seasons'].get('data', [])
		if ELEMENTS is None and str(SHORT.get('number_of_clips')).isdecimal() and int(SHORT['number_of_clips']) > 0:
			return listEpisodes(TARGET, SERIE, 00, 1, 1) # If not Seasons-data -> go directly to listEpisodes (mostly used for Clips)
		for item in ELEMENTS:
			FORM_CID = DATA_ONE['data']['id']
			SEAS_CID = item['id']
			if SEAS_CID in ['', 0, None] or SEAS_CID in UNIKAT:
				continue
			UNIKAT.add(SEAS_CID)
			FOUND += 1
			TITLE = SORTING = cleaning(item['attributes']['name'])
			matchSEA = re.search(r'(Staffel:? |S)([0-9]+)', TITLE)
			if matchSEA: SORTING = f"{int(matchSEA.group(2)):02}" if str(matchSEA.group(2)).isdecimal() and int(matchSEA.group(2)) != 0 else SORTING
			PLOT = get_Description(item.get('attributes', {}))
			debug_MS(f"(navigator.listSeasons[2]) ### NAME : {TITLE} || FORM_CID : {FORM_CID} || SEAS_CID : {SEAS_CID} || THUMB : {IMG} ###")
			COMBINATION.append([SORTING, TITLE, SERIE, PLOT, IMG, FORM_CID, SEAS_CID])
	if COMBINATION and FOUND == 1:
		debug_MS("(navigator.listSeasons[3]) ----- Only one Season FOUND - goto = listEpisodes -----")
		for SORTING, TITLE, SERIE, PLOT, IMG, FORM_CID, SEAS_CID in COMBINATION:
			return listEpisodes(FORM_CID, SERIE, SEAS_CID, 1, 1)
	elif COMBINATION and FOUND > 1:
		for SORTING, TITLE, SERIE, PLOT, IMG, FORM_CID, SEAS_CID in sorted(COMBINATION, key=lambda vsx: cleanUmlaut(vsx[0]).lower()):
			FETCH_UNO = create_entries({'Title': TITLE, 'Plot': PLOT, 'Image': IMG})
			addDir({'mode': 'listEpisodes', 'target': FORM_CID, 'name': SERIE, 'code': SEAS_CID}, FETCH_UNO)
	else:
		failing(f'(navigator.listSeasons) ##### NO SEASON_LIST - NO ENTRY FOR: "{SERIE}" FOUND #####')
		return dialog.notification(translation(30524), translation(30526).format(SERIE), icon, 10000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(TARGET, SERIE, SEAS_CODE, LIST_CODE, PAGE):
	debug_MS("(navigator.listEpisodes) -------------------------------------------------- START = listEpisodes --------------------------------------------------")
	debug_MS(f"(navigator.listEpisodes) ### TARGET = {TARGET} ### SERIE = {SERIE} ### SEAS_CODE = {SEAS_CODE} ### LIST_CODE = {LIST_CODE} ### PAGE = {PAGE} ###")
	DATA_ONE, FOUND, UNIKAT, (TEST_UNO, TEST_DUE) = {}, 0, set(), (False for _ in range(2))
	if TARGET != 'ENTRIES_HOME' and str(TARGET).isdecimal():
		TEST_UNO = getContent(config['EPIS_VIEW'].format(API_VANILLA, TARGET, SEAS_CODE, PAGE), AUTH=VANILLA_TOKEN)
		META_TOTAL = TEST_UNO['meta']['pagination']['total'] if TEST_UNO.get('meta', {}) and TEST_UNO['meta'].get('pagination', {}) and \
			TEST_UNO['meta']['pagination'].get('total', '') and str(TEST_UNO['meta']['pagination']['total']).isdecimal() else 0
		if len(TEST_UNO.get('data', [])) == 0 or int(META_TOTAL) == 0: # If not DATA or not Pagination-entries -> get 'Clips-Url'
			TEST_DUE = getContent(config['CLIPS_VIEW'].format(API_VANILLA, TARGET, PAGE), AUTH=VANILLA_TOKEN)
		DATA_ONE = TEST_DUE if TEST_DUE else TEST_UNO
	elif TARGET == 'ENTRIES_HOME':
		DATA_ONE = getContent(config['START_VIEW'].format(API_VANILLA, 'homepage'), AUTH=VANILLA_TOKEN)
	ELEMENTS = DATA_ONE.get('data', []) if TARGET != 'ENTRIES_HOME' and str(TARGET).isdecimal() else DATA_ONE['data'][int(LIST_CODE)-1]['attributes'].get('items', [])
	for item in ELEMENTS:
		for method in getSorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
		(NOTE_1, NOTE_2), (BC_DATE, BC_TIME, STARTS, BEGINS, AIRED) = ("" for _ in range(2)), (None for _ in range(5))
		if TARGET == 'ENTRIES_HOME' and int(LIST_CODE) == 1 and (item.get('format', '') or (item.get('video', '') and not item['video'].get('data', {}))): continue # Only show Video-entries from Recommendations and skip empty 'video-data' entries
		SHORT = item['video']['data'] if item.get('video', '') else item
		debug_MS(f"(navigator.listEpisodes[1]) xxxxx SHORT-01 : {SHORT} xxxxx")
		EPIS_CID = SHORT['id']
		TITLE = cleaning(SHORT['attributes']['title'])
		origSERIE = SERIE if SERIE not in ['', 'None', None] else SHORT['attributes']['format']['data']['attributes']['name'] if \
			SHORT['attributes'].get('format', {}) and SHORT['attributes']['format'].get('data', {}) and \
			SHORT['attributes']['format']['data'].get('attributes', {}) and SHORT['attributes']['format']['data']['attributes'].get('name', '') else ""
		if origSERIE != "": NOTE_1 = translation(30620).format(origSERIE)
		SEAS = SHORT['attributes']['season']['data']['attributes']['name'].replace('Staffel ', '') if SHORT['attributes'].get('season', {}) and \
			SHORT['attributes']['season'].get('data', {}) and SHORT['attributes']['season']['data'].get('attributes', {}) and \
			SHORT['attributes']['season']['data']['attributes'].get('name', '') else None
		EPIS = SHORT['attributes']['episode']['data']['attributes']['number'] if SHORT['attributes'].get('episode', {}) and \
			SHORT['attributes']['episode'].get('data', {}) and SHORT['attributes']['episode']['data'].get('attributes', {}) and \
			SHORT['attributes']['episode']['data']['attributes'].get('number', '') else None
		DESC = cleaning(SHORT['attributes'].get('teaser_text', ''))
		RUNS = SHORT['attributes'].get('play_length', None)
		BC_DATE = SHORT['attributes'].get('broadcast_date', None)
		BC_TIME = SHORT['attributes'].get('broadcast_time', None)
		if BC_DATE and not str(BC_DATE).startswith(('0000', '1970')) and BC_TIME:
			CIPHER = datetime(*(time.strptime(f"{BC_DATE[:10]}T{BC_TIME[:8]}", '%Y-%m-%dT%H:%M:%S')[0:6])) # 2019-06-13T22:15:00
			STARTS = CIPHER.strftime('%a. %d.%m.%Y')
			for sd in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), \
				('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))): STARTS = STARTS.replace(*sd)
			BEGINS = CIPHER.strftime('%Y-%m-%dT%H:%M') if KODI_ov20 else CIPHER.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
			AIRED = CIPHER.strftime('%d.%m.%Y') # FirstAired
		if str(SEAS).isdecimal() and str(EPIS).isdecimal() and str(EPIS) != '0':
			NAME = translation(30621).format(f"{int(SEAS):02}", f"{int(EPIS):02}", TITLE)
			if STARTS: NOTE_2 = translation(30622).format(f"{int(SEAS):02}", f"{int(EPIS):02}", STARTS)
			else: NOTE_2 = translation(30623).format(f"{int(SEAS):02}", f"{int(EPIS):02}")
		elif str(SEAS).isdecimal() and (not str(EPIS).isdecimal() or str(EPIS) == '0'):
			NAME = translation(30624).format(f"{int(SEAS):02}", TITLE)
			if STARTS: NOTE_2 = translation(30625).format(f"{int(SEAS):02}", STARTS)
			else: NOTE_2 = translation(30626).format(f"{int(SEAS):02}")
		else:
			if STARTS: NAME ,NOTE_2 = TITLE, translation(30627).format(STARTS)
			else: NAME ,NOTE_2 = TITLE, '[CR]'
		VIDEO = SHORT['attributes'].get('video_url', None)
		if EPIS_CID in ['', 0, None] or EPIS_CID in UNIKAT or VIDEO is None:
			continue
		UNIKAT.add(EPIS_CID)
		if not re.search(r'[0-9]+x[0-9]+', SHORT['attributes'].get('thumbnail_url', ''), re.S):
			THUMB = config['IMAGES_URL'].format(re.sub(r'/[0-9]+.jpg', '/1280x720-', SHORT['attributes'].get('thumbnail_url', '')))+SHORT['attributes'].get('thumbnail_url', '').split('/')[-1]
		else:
			THUMB = config['IMAGES_URL'].format(re.sub(r'[0-9]+x[0-9]+-', '1280x720-', SHORT['attributes'].get('thumbnail_url', '')))
		FOUND += 1
		debug_MS(f"(navigator.listEpisodes[2]) ##### NAME : {NAME} || SERIE : {SERIE} || EPIS_CID : {EPIS_CID} || DURATION : {RUNS} #####")
		debug_MS(f"(navigator.listEpisodes[2]) ##### BEGINS : {BEGINS} || SEASON : {SEAS} || EPISODE : {EPIS} || THUMB : {THUMB} #####")
		debug_MS("---------------------------------------------")
		FETCH_UNO = {'Title': NAME, 'TvShowTitle': origSERIE, 'Plot': NOTE_1+NOTE_2+DESC, 'Duration': RUNS, \
			'Season': SEAS,'Episode': EPIS, 'Date': BEGINS, 'Aired': AIRED, 'Mediatype': 'episode', 'Image': THUMB, 'Reference': 'Single'}
		addDir({'mode': 'playVideo', 'url': VIDEO}, create_entries(FETCH_UNO), False)
	NUMBERS = DATA_ONE['meta']['pagination']['total'] if DATA_ONE.get('meta', {}) and DATA_ONE['meta'].get('pagination', {}) and \
		DATA_ONE['meta']['pagination'].get('total', '') and str(DATA_ONE['meta']['pagination']['total']).isdecimal() else None
	if FOUND > 0 and NUMBERS and int(NUMBERS) > int(PAGE)*40:
		debug_MS(f"(navigator.listEpisodes[3]) PAGES ### NOW SHOW NEXTPAGE ENTRY ... No.{int(PAGE)+1} || URL : {config['EPIS_VIEW'].format(API_VANILLA, TARGET, SEAS_CODE, int(PAGE)+1)} ... ###")
		FETCH_DUE = create_entries({'Title': translation(30628).format(int(PAGE)+1), 'Image': f"{artpic}nextpage.png"})
		addDir({'mode': 'listEpisodes', 'target': TARGET, 'name': SERIE, 'code': SEAS_CODE, 'number': LIST_CODE, 'page': int(PAGE)+1}, FETCH_DUE)
	elif FOUND == 0:
		failing(f'(navigator.listEpisodes) ##### NO EPISODE_LIST - NO ENTRY FOR: "{SERIE}" FOUND #####')
		return dialog.notification(translation(30525), translation(30526).format(SERIE), icon, 10000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playVideo(ORIGIN):
	debug_MS("(navigator.playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug_MS(f"(navigator.playVideo) ### SOURCE = {ORIGIN} ###")
	ORIGIN = re.sub(r'/[0-9]+_720-HLS_.m3u8', '/master.m3u8', ORIGIN.replace('/720-HLS', '')) if '/720-HLS' in ORIGIN else ORIGIN
	STREAM, FINAL_URL = 'M3U8' if 'm3u8' in ORIGIN else 'MP4', config['PLAYER_URL'].format(ORIGIN) if ORIGIN else False
	if FINAL_URL:
		LPM = xbmcgui.ListItem(path=FINAL_URL, offscreen=True)
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive') and 'm3u8' in FINAL_URL:
			IA_NAME, STREAM = 'inputstream.adaptive', 'HLS'
			IA_VERSION = re.sub(r'(~[a-z]+(?:.[0-9]+)?|\+[a-z]+(?:.[0-9]+)?$|[.^]+)', '', xbmcaddon.Addon(IA_NAME).getAddonInfo('version'))[:4]
			LPM.setMimeType('application/vnd.apple.mpegurl'), LPM.setContentLookup(False), LPM.setProperty('inputstream', f"{IA_NAME}.")
			if KODI_un21:
				LPM.setProperty(f"{IA_NAME}.manifest_type", STREAM.lower()) # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
			if KODI_ov20:
				LPM.setProperty(f"{IA_NAME}.manifest_headers", f"User-Agent={get_userAgent()}") # On KODI v20 and above
			else: LPM.setProperty(f"{IA_NAME}.stream_headers", f"User-Agent={get_userAgent()}") # On KODI v19 and below
			if int(IA_VERSION) >= 2150 and STREAM == 'HLS':
				LPM.setProperty(f"{IA_NAME}.drm_legacy", 'org.w3.clearkey')
		log(f"(navigator.playVideo) {STREAM}_stream : {FINAL_URL}|User-Agent={get_userAgent()}")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
	else:
		failing(f'(navigator.playVideo) AbspielLink-00 : *MYSPASS* Der angeforderte VideoLink: "{ORIGIN}" wurde NICHT gefunden !!!')
		return dialog.notification(translation(30521).format('VIDEO'), translation(30527), icon, 10000)

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		for each in sorted(preserve(FAVORIT_FILE), key=lambda vsx: cleanUmlaut(vsx.get('Title', 'zorro')).lower()):
			FETCH_UNO = context = {'Cid': each.get('Cid'), 'Title': each.get('Title'), 'Plot': each.get('Plot'), 'Image': each.get('Image'), 'Poster': each.get('Poster')}
			addDir({'mode': 'listSeasons', 'target': each.get('Cid'), 'name': each.get('Title'), 'picture': each.get('Image')}, create_entries(FETCH_UNO), True, context, 'removing')
			debug_MS(f"(navigator.listFavorites[1]) ### NAME : {each.get('Title')} || SHOW_CID : {each.get('Cid')} || THUMB : {each.get('Image')} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favorit_construct(**kwargs):
	TOPS = []
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		TOPS = preserve(FAVORIT_FILE)
	if kwargs['action'] == 'ADD':
		del kwargs['mode']; del kwargs['action']
		TOPS.append({key: value for key, value in kwargs.items() if value not in ['', 'None', None]})
		preserve(FAVORIT_FILE, TOPS)
		xbmc.sleep(500)
		dialog.notification(translation(30528), translation(30529).format(kwargs['Title']), icon, 10000)
	elif kwargs['action'] == 'DEL':
		TOPS = [xs for xs in TOPS if xs.get('Cid') != kwargs.get('Cid')]
		preserve(FAVORIT_FILE, TOPS)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30528), translation(30530).format(kwargs['Title']), icon, 10000)

def addDir(params, listitem, folder=True, context={}, handling='default'):
	uws, entries = build_mass(params), []
	listitem.setPath(uws)
	if handling == 'adding' and context:
		entries.append([translation(30651), f"RunPlugin({build_mass({**context, **{'mode': 'favorit_construct', 'action': 'ADD'}})})"])
	if handling == 'removing' and context:
		entries.append([translation(30652), f"RunPlugin({build_mass({**context, **{'mode': 'favorit_construct', 'action': 'DEL'}})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
