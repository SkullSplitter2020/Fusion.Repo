# -*- coding: utf-8 -*-

from .common import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

COMPS_WAY, TEAMS_WAY, EVENTS_WAY = (None for _ in range(3))

def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	(number, SCORE_LIVE, SCORE_NEXT, NEXT_PAY), SEND, config = (0 for _ in range(4)), {}, traversing.get_config()
	COMBI_PAGES, COMBI_EVENTS, SEND['videos']= ([] for _ in range(3))
	if nowlive or upcoming:
		LINKS = [config['HOME_LIVENEXT'].format('live', 'region'), config['HOME_LIVENEXT'].format('upcoming', 'region')]
		for ELEMENT in LINKS:
			for ii in range(1, 6, 1):
				number += 1
				MURL = f"{ELEMENT}&page={str(ii)}&per_page={limit}"
				debug_MS(f"(navigator.mainMenu[1]) LIVE+NEXT-PAGES XXX POS = {number} || URL = {MURL} XXX")
				COMBI_PAGES.append([int(number), MURL])
		if COMBI_PAGES:
			COMBI_EVENTS = getMultiData(COMBI_PAGES)
			if COMBI_EVENTS:
				DATA_ONE = json.loads(COMBI_EVENTS)
				for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
					if 1 <= int(results['Position']) <= 5 and results is not None and results.get('data', '') and len(results['data']) > 0: # Pages between Number 1 and 5
						for livegame in results.get('data', []):
							if str(livegame.get('endTime'))[:4].isdigit() and get_CentralTime(livegame['endTime']) + timedelta(minutes=15) > datetime.now() and livegame.get('status', 500) == 200 and livegame.get('free', True) is True:
								debug_MS(f"(navigator.mainMenu[2]) LIVESTREAM ### NAME : {cleaning(livegame.get('name', 'UNKNOWN'))} || COMPETITION : {str(livegame.get('competition', {}).get('name', 'UNKNOWN'))} || IDD : {livegame.get('uuid', '00')} ###")
								SCORE_LIVE += 1
					elif 6 <= int(results['Position']) <= 10 and results is not None and results.get('data', '') and len(results['data']) > 0: # Pages between Number 6 and 10
						NEXT_ALL = results.get('totalCount', 0)
						for nextgame in results.get('data', []):
							if str(nextgame.get('startTime'))[:4].isdigit() and datetime.now() < get_CentralTime(nextgame['startTime']) - timedelta(minutes=15) and nextgame.get('status', 500) == 300 and nextgame.get('free', True) is False:
								debug_MS(f"(navigator.mainMenu[3]) NEXTSTREAM ### NAME : {cleaning(nextgame.get('name', 'UNKNOWN'))} || COMPETITION : {str(nextgame.get('competition', {}).get('name', 'UNKNOWN'))} || IDD : {nextgame.get('uuid', '00')} ###")
								NEXT_PAY += 1
						SCORE_NEXT = (NEXT_ALL - NEXT_PAY)
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	DATA_TWO = getUrl('/de.json')
	if advices and DATA_TWO is not None and DATA_TWO.get('pageProps', '') and DATA_TWO['pageProps'].get('promoList', '') and DATA_TWO['pageProps']['promoList'].get('data', '') and DATA_TWO['pageProps']['promoList'].get('data', {})[0].get('promoItems', ''):
		for item in DATA_TWO['pageProps']['promoList']['data'][0].get('promoItems', []):
			debug_MS(f"(navigator.mainMenu[4]) xxxxx ITEM-04 : {str(item)} xxxxx")
			plot, photo = (None for _ in range(2))
			title = cleaning(item['title'])
			table = 'media_assets' if item.get('promotableType', '') == 'MediaAsset' else 'event_playouts' # Event // MediaAsset
			plot = (cleaning(item.get('description', '')) or "")
			slug = item['promotable']['uuid'] if item.get('promotable', '') and item['promotable'].get('uuid', '') else '00'
			if item.get('promotable', '') and item['promotable'].get('images', '') and len(item['promotable']['images']) > 0:
				num, resources = slug, item['promotable'].get('images', [])
				photo = (get_Picture(num, resources, 'cover') or get_Picture(num, resources, 'thumb'))
			if photo is None: photo = icon
			if slug != '00':
				addLink(title, photo, {'mode': 'playCODE', 'IDENTiTY': slug}, plot)
				debug_MS(f"(navigator.mainMenu[4]) ### NAME : {title} || URL : {config['VIDEO_LINK'].format(table, slug)} || PHOTO : {photo} ###")
				SEND['videos'].append({'filter': slug, 'name': title, 'photo': photo, 'plot': plot, 'coding': config['VIDEO_LINK'].format(table, slug), 'muxing': 'VOD'})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		debug_MS("---------------------------------------------")
	if nowlive and SCORE_LIVE > 0:
		LIVE_URL = config['HOME_LIVENEXT'].format('live', 'region')+f"&page={page}&per_page={limit}"
		addDir(translation(30701).format(str(SCORE_LIVE)), f"{artpic}livestream.png", {'mode': 'listVideos', 'url': LIVE_URL, 'category': 'LIVE - Alle Sportarten'}, translation(30702).format(str(SCORE_LIVE)))
	if upcoming and SCORE_NEXT > 0:
		NEXT_URL = config['HOME_LIVENEXT'].format('upcoming', 'region')+f"&page={page}&per_page={limit}"
		addDir(translation(30703).format(str(SCORE_NEXT)), f"{artpic}upcoming.png", {'mode': 'listVideos', 'url': NEXT_URL, 'category': 'NEXT - Alle Sportarten'}, translation(30704).format(str(SCORE_NEXT)))
	addDir(translation(30606), f"{artpic}favourites.png", {'mode': 'listFavorites'})
	if DATA_TWO is not None and DATA_TWO.get('pageProps', '') and DATA_TWO['pageProps'].get('region', '') and DATA_TWO['pageProps']['region'].get('sports', ''):
		for each in DATA_TWO['pageProps']['region'].get('sports', []):
			debug_MS(f"(navigator.mainMenu[5]) xxxxx EACH-05 : {str(each)} xxxxx")
			name = each['name'].title()
			picture = f"{artpic}{name.lower()}.png" if xbmcvfs.exists(f"{artpic}{name.lower()}.png") else icon
			uuid = each.get('uuid', '00')
			published = each.get('published', False)
			name = next((lang.get('new') for lang in GENLANG if lang.get('old') == name.lower()), name)
			if uuid != '00' and published is True:
				addDir(name, picture, {'mode': 'listCategories', 'url': uuid, 'category': name, 'section': name})
				debug_MS(f"(navigator.mainMenu[5]) ### NAME : {name} || UUID : {uuid} || GENRE : {name} ###")
	if basedates: addDir(translation(30607), f"{artpic}preview.png", {'mode': 'listDates'})
	if basesearch: addDir(translation(30608), f"{artpic}basesearch.png", {'mode': 'SearchSPORT'})
	if enableADJUSTMENT:
		addDir(translation(30609), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30610), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listCategories(url, CAT, SECTOR, PAGE, LIMIT):
	debug_MS("(navigator.listCategories) -------------------------------------------------- START = listCategories --------------------------------------------------")
	debug_MS(f"(navigator.listCategories) ##### URL = {url} ##### CATEGORY = {CAT} ##### GENRE = {SECTOR} ##### PAGE = {PAGE} ##### LIMIT = {LIMIT} #####")
	COMBI_PAGES, COMBI_FIRST, COMBI_SECOND = ([] for _ in range(3))
	(FOUND, PAYING), UNIKAT, config = (0 for _ in range(2)), set(), traversing.get_config()
	if '@@' in url:
		CODE, TARGET = url.split('@@')[1], url.split('@@')[0]
		LINKS = [config['LIVE_EVENT'].format(CODE, TARGET, PAGE, LIMIT), config['COMING_EVENT'].format(CODE, TARGET, PAGE, LIMIT), \
						config['LATEST_EVENT'].format(CODE, TARGET, PAGE, LIMIT), config['HIGH_EVENT'].format(CODE, TARGET, PAGE, LIMIT)]
	else:
		CODE, TARGET = url, 'sport'
		LINKS = [config['LIVE_EVENT'].format(CODE, TARGET, PAGE, LIMIT), config['COMING_EVENT'].format(CODE, TARGET, PAGE, LIMIT), config['LATEST_EVENT'].format(CODE, TARGET, PAGE, LIMIT), \
						config['HIGH_EVENT'].format(CODE, TARGET, PAGE, LIMIT), config['SPORT_CONTESTS'].format(CODE, PAGE, LIMIT), config['SPORT_TEAMS'].format(CODE, PAGE, LIMIT)]
	for ii, ELEMENT in enumerate(LINKS, 1):
		debug_MS(f"(navigator.listCategories[1]) CATEGORIES-PAGES XXX POS = {str(ii)} || URL = {ELEMENT} XXX")
		COMBI_PAGES.append([int(ii), ELEMENT])
	if COMBI_PAGES:
		COMBI_FIRST = getMultiData(COMBI_PAGES)
		if COMBI_FIRST:
			debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
			DATA_ONE = json.loads(COMBI_FIRST)
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and results.get('data', '') and len(results['data']) > 0 and results.get('totalCount', ''):
					debug_MS(f"(navigator.listCategories[2]) xxxxx RESULTS-02 : {str(results)} xxxxx")
					POS, DEM = results['Position'], results['Demand']
					TITLE = next((pt.get('title') for pt in config['picks'] if pt.get('member') in DEM), 'UNKNOWN')
					TOTAL = results.get('totalCount', 0)
					PAYING = get_Number(results, DEM)
					TRIMMED = TOTAL - PAYING
					if TITLE in UNIKAT or TRIMMED <= 0:
						continue
					UNIKAT.add(TITLE)
					FOUND += 1
					NAME_ONE, NAME_TWO = (translation(30711).format(TITLE+CAT, str(TRIMMED)) for _ in range(2))
					IMG = next((f"{artpic}{ps.get('member')}.png" for ps in config['picks'] if ps.get('member') in DEM and xbmcvfs.exists(f"{artpic}{ps.get('member')}.png")), icon)
					PLOT = translation(30712).format(TITLE, CAT, str(TRIMMED))
					if 'live' in DEM:
						NAME_ONE = translation(30713).format(NAME_ONE)
						PLOT = translation(30714).format(str(TRIMMED))
					elif 'upcoming' in DEM:
						NAME_ONE = translation(30715).format(NAME_ONE)
						PLOT = translation(30716).format(CAT, str(TRIMMED))
					debug_MS(f"(navigator.listCategories[3]) NUMBERING ### CATEGORY : {TITLE+CAT} ### TOTAL : {TOTAL} ### FORFREE : {TRIMMED} ###")
					debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
					COMBI_SECOND.append([POS, DEM, SECTOR, CAT, NAME_ONE, NAME_TWO, TITLE, IMG, PLOT])
	if COMBI_SECOND and FOUND == 1:
		debug_MS("(navigator.listCategories[4]) ----- Only one Entry FOUND - goto = listVideos -----")
		for POS, DEM, SECTOR, CAT, NAME_ONE, NAME_TWO, TITLE, IMG, PLOT in COMBI_SECOND:
			addDir(translation(30717).format(NAME_TWO), IMG, {'mode': 'blankFUNC', 'url': '00'}, genre=SECTOR, folder=False)
			return listVideos(DEM, TITLE+CAT, SECTOR, page, limit, position, excluded)
	elif COMBI_SECOND and FOUND >= 2:
		for POS, DEM, SECTOR, CAT, NAME_ONE, NAME_TWO, TITLE, IMG, PLOT in sorted(COMBI_SECOND, key=lambda cr: int(cr[0])):
			addDir(NAME_ONE, IMG, {'mode': 'listVideos', 'url': DEM, 'category': TITLE+CAT, 'section': SECTOR}, PLOT, SECTOR)
			debug_MS(f"(navigator.listCategories[4]) ### NAME : {NAME_ONE} || URL : {DEM} || GENRE : {SECTOR} || PHOTO : {IMG} ###")
	else:
		return dialog.notification(translation(30526).format('Einträge'), translation(30527).format(CAT), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listDates():
	debug_MS("(navigator.listDates) ------------------------------------------------ START = listDates -----------------------------------------------")
	config = traversing.get_config()
	DATA_ONE = getUrl(config['EVENT_DATES'])
	#log(f"(navigator.listDates[1]) ### DATES-01 : {str(DATA_ONE)} ###")
	for ii in range(-90, 91, 1):
		utc_start = (datetime.utcnow() - timedelta(days=ii + 1)).strftime('%Y-%m-%d') # 2023-07-19
		epoch_start = TGM(time.strptime(utc_start+'T22:00:00', '%Y-%m-%dT%H:%M:%S')) * 1000 # UTC-EPOCH-STARTZEIT einen Tag zurück um 22:00:00 Uhr (Milliseconds=168980400000)
		utc_end = (datetime.utcnow() - timedelta(days=ii)).strftime('%Y-%m-%d') # 2023-07-20
		epoch_end = TGM(time.strptime(utc_end+'T21:59:59', '%Y-%m-%dT%H:%M:%S')) * 1000 # UTC-EPOCH-ENDZEIT aktuell ausgewählter Tag um 21:59:59 Uhr (Milliseconds=1689890399000)
		if not utc_end in DATA_ONE: continue
		debug_MS(f"(navigator.listDates[1]) ### START_UTC : {utc_start} || START_EPOCH : {str(epoch_start)} ###")
		#log(f"(navigator.listDates[2]) ### UTC_END : {utc_ende} || EPOCH_END : {str(epoch_ende)} ###")
		WD = (datetime.utcnow() - timedelta(days=ii)).strftime('%d.%m.%y | %a') # Datum mit engl. Wochentagskürzel = 16.07.23 | Sun
		for av in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
			WD = WD.replace(*av)
		TIMING = config['EVENT_STARTS'].format('region', epoch_start, epoch_end, page, limit)
		if ii == 0: addDir(translation(30731).format(WD), f"{artpic}calendar.png", {'mode': 'listVideos', 'url': TIMING, 'category': utc_end})
		else: addDir(WD, f"{artpic}calendar.png", {'mode': 'listVideos', 'url': TIMING, 'category': utc_end})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSPORT():
	debug_MS("(navigator.SearchSPORT) ------------------------------------------------ START = SearchSPORT -----------------------------------------------")
	config = traversing.get_config()
	keyword = None
	if xbmcvfs.exists(SEARCHFILE):
		with open(SEARCHFILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30741), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote_plus(keyword)
			with open(SEARCHFILE, 'w') as record:
				record.write(keyword)
	if keyword:
		return listVideos(config['SEARCH_ALL'].format(keyword, page, 50), translation(30742).format(unquote_plus(keyword)), section, page, 50, position, excluded)
	return None

def load_pagination(CONTENT, FEED):
	global COMPS_WAY, TEAMS_WAY, EVENTS_WAY
	if FEED.startswith(('SEARCH:', 'SUCHE:')): # Alles: 'competitions, teams, events' nur in Suchfunktion vorhanden
		if CONTENT.get('data', '') and not isinstance(CONTENT['data'], list) and CONTENT['data'].get('competitions', ''):
			addDir(translation(30751).format(cleaning(FEED)), f"{artpic}competitions.png", {'mode': 'blankFUNC', 'url': '00'}, folder=False)
			COMPS_WAY = 'COMPS'
			for item in sorted(CONTENT['data'].get('competitions', []), key=lambda nc: repair_umlaut(nc.get('name', 'unk').lower())): yield item
			debug_MS("---------------------------------------------")
		if CONTENT.get('data', '') and not isinstance(CONTENT['data'], list) and CONTENT['data'].get('teams', ''):
			addDir(translation(30752).format(cleaning(FEED)), f"{artpic}teams.png", {'mode': 'blankFUNC', 'url': '00'}, folder=False)
			TEAMS_WAY = 'TEAMS'
			for item in sorted(CONTENT['data'].get('teams', []), key=lambda nt: repair_umlaut(nt.get('name', 'unk').lower())): yield item
			debug_MS("---------------------------------------------")
		if CONTENT.get('data', '') and not isinstance(CONTENT['data'], list) and CONTENT['data'].get('events', ''):
			addDir(translation(30753).format(cleaning(FEED)), f"{artpic}latest.png", {'mode': 'blankFUNC', 'url': '00'}, folder=False)
			EVENTS_WAY = 'EVENTS'
			for item in sorted(CONTENT['data'].get('events', []), key=lambda se: se.get('startTime', '2024-01-01T00:00:01.000'), reverse=True): yield item
	elif not FEED.startswith(('SEARCH:', 'SUCHE:')) and CONTENT.get('data', '') and isinstance(CONTENT['data'], list):
		for item in CONTENT.get('data', []): yield item

def listVideos(TARGET, CAT, SECTOR, PAGE, LIMIT, POS, FILTER):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug_MS(f"(navigator.listVideos) ### URL = {TARGET} ### CATEGORY = {CAT} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### POSITION = {POS} ### EXCLUDED = {FILTER} ###")
	# Stream-Status-Codes = 200 : Livestream // 300 : Kommender Stream // 600 : Aufgezeichneter Stream
	DIRECTORY = ['competition', 'team']
	PLAYOUTS = ['live', 'latest', 'upcoming', 'all_events']
	(counterONE, excludedONE), counterTWO, excludedTWO = (0 for _ in range(2)), int(POS), int(FILTER)
	SEND, UNIKAT, config = {}, set(), traversing.get_config()
	SEND['videos'] = []
	UPCOMING = True if 'upcoming' in TARGET else False
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == '0' and HIGHER is True:
		addDir(translation(30771), f"{artpic}backmain.png", {'mode': 'callingMain'})
	DATA_ONE = getUrl(f"{TARGET.split('page=')[0]}page={PAGE}&per_page={LIMIT}") if int(PAGE) > 1 else getUrl(TARGET)
	for each in load_pagination(DATA_ONE, CAT):
		debug_MS(f"(navigator.listVideos[1]) xxxxx EACH-01 : {str(each)} xxxxx")
		startCOMPLETE, startDATE, startTIME, aired, begins, endDATE, plot, photo = (None for _ in range(8))
		(NEXTCOME, RUNNING), branch, source, gender, MARK, fotoBIG = (False for _ in range(2)), 'sport', each, "", 'team', True
		counterONE, counterTWO = counterONE.__add__(1), counterTWO.__add__(1)
		uuid = each.get('uuid', None)
		if uuid is None or uuid in UNIKAT:
			excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
			continue
		UNIKAT.add(uuid)
		title = cleaning(each['name'])
		desc = cleaning(each['description']) if each.get('description', '') else ""
		each = each['event'] if each.get('event', '') and 'highlights' in TARGET else each
		TYPE = each.get('eventType', 'unknown')
		if EVENTS_WAY == 'EVENTS' and TYPE in ['live', 'upcoming']:
			excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
			continue # In der Suchfunktion die live+kommenden Spiele herausfiltern
		FREE = each.get('free', True)
		STAT = each.get('status', 500)
		SEXO = each.get('gender', '')
		if SEXO == 'women': gender = translation(30772).format(SEXO.replace('women', 'F'))
		elif SEXO == 'men': gender = translation(30773).format(SEXO.replace('men', 'M'))
		if str(each.get('startTime'))[:4].isdigit(): # 2024-05-10T19:15:18.000Z
			LOCALstart = get_CentralTime(each['startTime'])
			startCOMPLETE = LOCALstart.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format( '.', '•', ':')
			for tt in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
				startCOMPLETE = startCOMPLETE.replace(*tt)
			startDATE = LOCALstart.strftime('%d.%m.%Y')
			startTIME = LOCALstart.strftime('%H:%M')
			if datetime.now() < LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = True, False # 19:44 < 20:00-15m = 19:45
			if datetime.now() > LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = False, True # 19:46 > 20:00-15m = 19:45
			aired = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
			begins = LOCALstart.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
			if KODI_ov20:
				begins = LOCALstart.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
		if str(each.get('endTime'))[:4].isdigit(): # 2024-05-10T22:00:18.000Z
			LOCALend = get_CentralTime(each['endTime'])
			endDATE = LOCALend.strftime('%d{0}%m{0}%YT%H{1}%M').format('.', ':')
			if datetime.now() > LOCALend + timedelta(minutes=15): # 22:30 > 22:00+15m = 22:15
				NEXTCOME, RUNNING = False, False
			if str(STAT).isdigit() and int(STAT) == 200 and startTIME and datetime.now() > LOCALend + timedelta(hours=4): STAT = 600 # 22:30 > 18:15+4h = 22:15
		else:
			if str(STAT).isdigit() and int(STAT) in [300, 600] and RUNNING is True:
				RUNNING = False
		if each.get('competition', '') and each['competition'].get('name', ''):
			if (RUNNING is True or NEXTCOME is True) and startCOMPLETE:
				plot = translation(30774).format(title, cleaning(each['competition']['name']), startCOMPLETE)
				if len(desc) > 90: plot += desc
			if plot is None and startDATE:
				plot = translation(30775).format(title, cleaning(each['competition']['name']), startDATE)
				if len(desc) > 90: plot += desc
		elif 'competitions' in TARGET:
			if each.get('sportAssociation', '') and each['sportAssociation'].get('name', ''):
				plot = translation(30776).format(title, cleaning(each['sportAssociation']['name']))
				if each['sportAssociation'].get('sport', '') and each['sportAssociation']['sport'].get('name', ''):
					branch = cleaning(each['sportAssociation']['sport']['name'])
		elif 'teams' in TARGET:
			if each.get('competitions', '') and each.get('competitions', {})[0].get('name', ''):
				plot = translation(30777).format(title, cleaning(each['competitions'][0]['name']))
				if each.get('sport', '') and each['sport'].get('name', ''):
					branch = cleaning(each['sport']['name'])
		elif EVENTS_WAY == 'EVENTS' and TYPE == 'latest' and startDATE:
			plot = translation(30778).format(title, startDATE)
			if len(desc) > 90: plot += desc
		if plot is None: plot = f"[B]{desc}[/B]" if 'searches' in TARGET else desc
		if 'searches' in TARGET and each.get('sport', ''):
			branch = cleaning(each['sport'])
		branch = SECTOR if branch == 'sport' and branch.lower() != SECTOR.lower() else branch
		genre = next((lang.get('new') for lang in GENLANG if lang.get('old') == branch.lower()), branch.title())
		if startDATE and FREE is False:
			excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
		if each.get('imageUrl', ''): # Nur in Suchfunktion vorhanden
			photo, fotoBIG = each['imageUrl'], False
		if photo is None and each.get('images', '') and isinstance(each['images'], list):
			num, resources = uuid, each.get('images', [])
			photo = (get_Picture(num, resources, 'cover') or get_Picture(num, resources, 'thumb'))
			if photo is None:
				photo, fotoBIG = get_Picture(num, resources, 'logo'), False
		if photo is None and source.get('images', '') and isinstance(source['images'], list):
			num, resources = uuid, source.get('images', []) # Bei Highlights sind die Bilder manchmal in der StartSource enthalten
			photo = (get_Picture(num, resources, 'cover') or get_Picture(num, resources, 'thumb'))
			if photo is None:
				photo, fotoBIG = get_Picture(num, resources, 'logo'), False
		if photo is None and each.get('teams', ''):
			if each.get('teams', {})[0].get('images', ''):
				num, resources = uuid, each['teams'][0].get('images', [])
				photo = (get_Picture(num, resources, 'cover') or get_Picture(num, resources, 'thumb'))
				if photo is None:
					photo, fotoBIG = get_Picture(num, resources, 'logo'), False
			if photo is None and each.get('teams', {})[0].get('logoUrl', ''):
				photo, fotoBIG = each['teams'][0]['logoUrl'], False
		if photo is None:
			photo, fotoBIG = icon, False
		if startDATE is None:
			if COMPS_WAY == 'COMPS': MARK = 'competition'
			if TEAMS_WAY == 'TEAMS': MARK = 'team'
			MARK = next((drs for drs in DIRECTORY if drs in TARGET), MARK)
			addType = 1
			if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
				with open(channelFavsFile, 'r') as chp:
					watch = json.load(chp)
					for item in watch.get('items', []):
						if item.get('url') == f"{MARK}@@{uuid}": addType = 2
			addDir(title+gender, photo, {'mode': 'listCategories', 'url': f"{MARK}@@{uuid}", 'category': title, 'section': genre}, plot, genre, fotoBIG, HIGHER, addType)
			debug_MS(f"(navigator.listVideos[2]) ### NAME : {title+gender} || URL : {MARK}@@{uuid} || PHOTO : {photo} ###")
			debug_MS("---------------------------------------------")
		elif startDATE and FREE is True:
			name = f"{startDATE} - {title+gender}" if startDATE else title+gender
			if str(STAT).isdigit() and int(STAT) == 200 and RUNNING is True and startTIME:
				name = translation(30779).format(startTIME, title+gender)
			media = 'LIVE' if str(STAT).isdigit() and int(STAT) == 200 else 'VOD'
			table = 'event_playouts' if any(ps in TARGET for ps in PLAYOUTS) or TYPE in ['live', 'latest', 'upcoming'] else 'media_assets' # Event // MediaAsset
			addLink(name, photo, {'mode': 'playCODE', 'IDENTiTY': uuid}, plot, begins, aired, genre, fotoBIG, HIGHER, UPCOMING)
			SEND['videos'].append({'filter': uuid, 'name': name, 'photo': photo, 'plot': plot, 'coding': config['VIDEO_LINK'].format(table, uuid), 'muxing': media})
			debug_MS(f"(navigator.listVideos[3]) ### NAME : {name} || URL : {config['VIDEO_LINK'].format(table, uuid)} || PHOTO : {photo} || EVENT_TYPE : {TYPE.lower()} || GENRE : {genre} ###")
			debug_MS("---------------------------------------------")
	if counterONE >= 1:
		if SEND['videos']:
			with open(WORKFILE, 'w') as ground:
				json.dump(SEND, ground, indent=4, sort_keys=True)
			debug_MS(f"(navigator.listVideos[4]) NUMBERING ### current_RESULT : {counterONE} // all_RESULT : {counterTWO} ### current_EXCLUDED : {excludedONE} // all_EXCLUDED : {excludedTWO} ###")
		if not 'searches' in TARGET and str(DATA_ONE.get('totalCount')).isdigit():
			debug_MS(f"(navigator.listVideos[4]) NUMBERING ### totalRESULTS : {DATA_ONE['totalCount']} // thisPAGE ends at : {str(int(PAGE)*int(LIMIT))} ###")
			if int(DATA_ONE['totalCount']) > int(counterTWO):
				debug_MS(f"(navigator.listVideos[4]) PAGES ### Now show NextPage ... No.{str(int(PAGE)+1)} ... ###")
				addDir(translation(30780).format(int(PAGE)+1), f"{artpic}nextpage.png", {'mode': 'listVideos', 'url': TARGET, 'category': CAT, 'section': SECTOR, 'page': int(PAGE)+1, 'limit': LIMIT, 'position': counterTWO, 'excluded': excludedTWO})
	else:
		MESSAGE = CAT if not 'searches' in TARGET else re.sub('(SEARCH: |SUCHE: )', '', CAT)
		return dialog.notification(translation(30526).format('Einträge'), translation(30527).format(MESSAGE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### SOURCE = {IDD} ###")
	EXTRA, Status, MEDIAS, RECORDED, config = 'LIVE', 'OFFLINE', [], True, traversing.get_config()
	PLAY_URL, PLAY_TYPE, FOUND, PayFree, FINAL_WORKS, STREAM_WORKS, TEST_WORKS = (False for _ in range(7))
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] != '00' and elem['filter'] == IDD:
				CLEAR_TITLE, PHOTO, PLOT, PLAY_URL, PLAY_TYPE = re.sub('(\[B\]|\[/B\])', '', elem['name']), elem['photo'], elem['plot'], elem['coding'], elem['muxing']
				debug_MS(f"(navigator.playCODE) ### WORKFILE-Line : {str(elem)} ###")
	if PLAY_URL and PLAY_TYPE:
		FIRST = getUrl(PLAY_URL)
		debug_MS(f"(navigator.playCODE[1]) XXXXX CONTENT-01 : {str(FIRST)} XXXXX")
		debug_MS("---------------------------------------------")
		if FIRST is not None and not FIRST.get('errors', ''):
			if (FIRST.get('event', '') and len(FIRST['event']) > 0) or (FIRST and len(FIRST) > 0):
				DATA_UNO = FIRST['event'] if FIRST.get('event', '') and len(FIRST['event']) > 0 else FIRST
				if str(DATA_UNO.get('endTime'))[:4].isdigit(): # 2024-05-10T22:00:18.000Z
					LOCALend = get_CentralTime(DATA_UNO['endTime'])
					EXTRA = 'VOD' if datetime.now() > LOCALend else 'LIVE'
					debug_MS(f"(navigator.playCODE[2]) ### NEW_TYPE : {str(EXTRA)} || DAYTIME (local NOW) : {str(datetime.now())[:19]} || official ENDTIME (local GAME) : {str(LOCALend)} ###")
				FOUND = True
				PayFree = True if DATA_UNO.get('free', '') is True else False
				Status = 'ONLINE' if str(DATA_UNO.get('status')).isdigit() and int(DATA_UNO['status']) != 300 else 'OFFLINE'
			if PayFree is True and Status == 'ONLINE' and (FIRST.get('mediaAssets', '') and len(FIRST['mediaAssets']) > 0) or (FIRST.get('mediaAssetLocators', '') and len(FIRST['mediaAssetLocators']) > 0):
				DATA_DUE = FIRST['mediaAssets'] if FIRST.get('mediaAssets', '') and isinstance(FIRST['mediaAssets'], list) else [FIRST]
				for STEPS in DATA_DUE:
					ASSET = STEPS.get('assetType', 'DEFAULT')
					for item in STEPS.get('mediaAssetLocators', []):
						if 'pano' in ASSET: continue
						MEDIAS.append({'video': item['url'], 'asset': ASSET, 'norm': item['mediaFormat']})
				debug_MS(f"(navigator.playCODE[3]) === STATUS : {Status} === HLS/MP4 === SORTED_LIST : {str(MEDIAS)} ===")
	if FOUND is True and PayFree is False:
		failing(f"(navigator.playCODE) ##### Abspielen des Streams NICHT möglich ##### URL : {PLAY_URL} #####\n ########## Dieser Stream ist nur mit einem Bezahl-ABO-System von *https://sporttotal.tv/* abrufbar !!! ##########")
		return dialog.notification(translation(30528), translation(30529), icon, 10000)
	if MEDIAS:
		attempts_one, attempts_two = (1 for _ in range(2))
		heading = {'Cache-Control': 'no-cache', 'Accept': '*/*', 'documentLifecycle': 'active', 'User-Agent': defaultAgent, 'DNT': '1', 'Accept-Encoding': 'gzip', 'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'}
		heading.update(config['header'])
		for item in MEDIAS:
			if ((EXTRA.lower() in item['asset']) or (not item['asset'].lower().startswith('broadcast'))) and item['norm'] == 'hls' and 'm3u8' in item['video']:
				STREAM_ONE, FINAL_ONE = ('HLS' if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') else 'M3U8'), item['video']
				log("(navigator.playCODE[4]) ***** FIRST_TESTING : {} {} - FILE *****".format('Inputstream (hls)' if STREAM_ONE == 'HLS' else 'Standard (m3u8)', EXTRA))
				while not TEST_WORKS and attempts_one < 3: # 2 x Pingversuche für den STREAM-Request ::: zur Überprüfung der Verfügbarkeit des Streams
					attempts_one += 1
					try:
						queries = Request(FINAL_ONE, None, heading)
						scan_one = urlopen(queries, timeout=8)
						debug_MS(f"(navigator.playCODE[4]) === CALL_{STREAM_ONE}_STREAM === RETRIES_no : {str(attempts_one-1)} === STATUS : {str(scan_one.getcode())} || URL : {FINAL_ONE} ===")
					except (URLError, HTTPError) as e:
						debug_MS(f"(navigator.playCODE[4]) ERROR - {STREAM_ONE}_STREAM - ERROR ##### RETRIES_no : {str(attempts_one-1)} === URL : {FINAL_ONE} === FAILURE : {str(e)} #####")
						time.sleep(2)
					else:
						FINAL_WORKS, STREAM_WORKS, TEST_WORKS = FINAL_ONE, STREAM_ONE, True
						break
		if TEST_WORKS is False:
			for item in MEDIAS:
				if item['norm'] == 'mp4' and ('.mp4' in item['video'] or '.ts' in item['video']):
					STREAM_TWO, FINAL_TWO = 'MP4', item['video']
					log("(navigator.playCODE[5]) !!!!! SECOND_TESTING : KEINEN funktionierenden Stream gefunden === nehme jetzt den Reserve-Stream-MP4 !!!!!")
					while not TEST_WORKS and attempts_two < 3: # 2 x Pingversuche für den STREAM-Request ::: zur Überprüfung der Verfügbarkeit des Streams
						attempts_two += 1
						try:
							queries = Request(FINAL_TWO, None, heading)
							scan_two = urlopen(queries, timeout=8)
							debug_MS(f"(navigator.playCODE[5]) === CALL_{STREAM_TWO}_STREAM === RETRIES_no : {str(attempts_two-1)} === STATUS : {str(scan_two.getcode())} || URL : {FINAL_TWO} ===")
						except (URLError, HTTPError) as e:
							debug_MS(f"(navigator.playCODE[5]) ERROR - {STREAM_TWO}_STREAM - ERROR ##### RETRIES_no : {str(attempts_two-1)} === URL : {FINAL_TWO} === FAILURE : {str(e)} #####")
							time.sleep(2)
						else:
							FINAL_WORKS, STREAM_WORKS, TEST_WORKS = FINAL_TWO, STREAM_TWO, True
							break
		if TEST_WORKS is False:
			failing(f"(navigator.playCODE[6]) ##### Abspielen des Streams NICHT möglich ##### URL : {PLAY_URL} #####\n ########## Die vorhandenen Stream-Einträge auf der Webseite von *https://sporttotal.tv/* sind OFFLINE/DEFEKT !!! ##########")
			return dialog.notification(translation(30521).format('URL-2'), translation(30530), icon, 10000)
	else:
		failing(f"(navigator.playCODE[2]) ##### Abspielen des Streams NICHT möglich ##### URL : {PLAY_URL} #####\n ########## KEINEN Stream-Eintrag auf der Webseite von *https://sporttotal.tv/* gefunden !!! ##########")
		return dialog.notification(translation(30521).format('URL-1'), translation(30531), icon, 10000)
	if FINAL_WORKS and TEST_WORKS:
		LPM = xbmcgui.ListItem(CLEAR_TITLE, path=FINAL_WORKS)
		if PLOT in ['', 'None', None]: PLOT = "..."
		if KODI_ov20:
			vinfo = LPM.getVideoInfoTag()
			vinfo.setTitle(CLEAR_TITLE), vinfo.setPlot(PLOT), vinfo.setStudios(['Sporttotal.tv'])
		else:
			LPM.setInfo('Video', {'Title': CLEAR_TITLE, 'Plot': PLOT, 'Studio': 'Sporttotal.tv'})
		LPM.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO})
		MIME_WORKS = 'video/mp4' if STREAM_WORKS == 'MP4' else 'application/x-mpegurl'
		LPM.setMimeType(MIME_WORKS)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and STREAM_WORKS in ['HLS', 'M3U8']:
			LPM.setProperty('inputstream', 'inputstream.adaptive')
			if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
				LPM.setProperty('inputstream.adaptive.manifest_type', 'hls')
				LPM.setProperty('inputstream.adaptive.manifest_update_parameter', 'full') # THE "full" BEHAVIOUR PARAM HAS BEEN REMOVED ON Kodi v21 because now enabled by default.
			if KODI_ov20:
				LPM.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={defaultAgent}")
			else: # DEPRECATED ON Kodi v20, please use 'inputstream.adaptive.manifest_headers' instead.
				LPM.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={defaultAgent}")
			LPM.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true') # If possible allow to start playing a LIVE stream from the beginning of the buffer instead of its end.
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
		log(f"(navigator.playCODE) {STREAM_WORKS}_stream : {FINAL_WORKS}")
		xbmc.sleep(5000)
		if not xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)') and not xbmc.Player().isPlayingVideo():
			return dialog.notification(translation(30521).format('URL-PLAY'), translation(30532), icon, 10000)

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
		with open(channelFavsFile, 'r') as fp: # Favoriten für Profile/Vereine
			snippets = json.load(fp)
			for item in snippets.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				debug_MS(f"(navigator.listFavorites) ### NAME : {name} || URL : {item.get('url')} || IMAGE : {logo} || GENRE : {item.get('section')} ###")
				addDir(name, logo, {'mode': 'listCategories', 'url': item.get('url'), 'category': item.get('category'), 'section': item.get('section')}, cleaning(item.get('plot')), item.get('section'), FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'category': category, 'plot': plot, 'section': section})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30533), translation(30534).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30533), translation(30535).format(name), icon, 8000)

def addDir(name, image, params={}, plot=None, genre='Sport', background=False, higher=False, addType=0, FAVclear=False, folder=True):
	uws, entries = build_mass(params), []
	LDM = xbmcgui.ListItem(name, offscreen=True)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = LDM.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setGenres([genre]), vinfo.setStudios(['Sporttotal.tv'])
	else:
		LDM.setInfo('Video', {'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': 'Sporttotal.tv'})
	LDM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and image != icon and not artpic in image and background is True:
		LDM.setArt({'fanart': image})
	LDM.setProperty('IsPlayable', 'false')
	if enableBACK and PLACEMENT == '1' and higher is True:
		entries.append([translation(30650), 'RunPlugin({})'.format(build_mass({'mode': 'callingMain'}))])
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'ADD', 'name': name, 'pict': 'None' if image == icon else image, 'url': params.get('url'), \
			'category': params.get('category'), 'plot': plot.replace('\n', '[CR]'), 'section': params.get('section')}))])
	if addType == 0 and FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), \
			'category': params.get('category'), 'plot': plot, 'genre': genre}))])
	LDM.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uws, listitem=LDM, isFolder=folder)

def addLink(name, image, params={}, plot=None, begins=None, aired=None, genre='Sport', background=False, higher=False, upcoming=False):
	uvz, entries = build_mass(params), []
	LEM = xbmcgui.ListItem(name)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = LEM.getVideoInfoTag()
		vinfo.setTitle(name)
		vinfo.setPlot(plot)
		if begins: LEM.setDateTime(begins)
		if aired: vinfo.setFirstAired(aired)
		if aired and str(aired[6:10]).isdigit(): vinfo.setYear(int(aired[6:10]))
		if genre and len(genre) > 3: vinfo.setGenres([genre])
		vinfo.setStudios(['Sporttotal.tv'])
		vinfo.setMediaType('movie')
	else:
		vinfo = {}
		vinfo['Title'] = name
		vinfo['Plot'] = plot
		if begins: vinfo['Date'] = begins
		if aired: vinfo['Aired'] = aired
		if aired and str(aired[6:10]).isdigit(): vinfo['Year'] = aired[6:10]
		if genre and len(genre) > 3: vinfo['Genre'] = genre
		vinfo['Studio'] = 'Sporttotal.tv'
		vinfo['Mediatype'] = 'movie'
		LEM.setInfo('Video', vinfo)
	LEM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and image != icon and not artpic in image and background is True:
		LEM.setArt({'fanart': image})
	LEM.setProperty('IsPlayable', 'true')
	LEM.setContentLookup(False)
	if enableBACK and PLACEMENT == '1' and higher is True:
		entries.append([translation(30650), 'RunPlugin({})'.format(build_mass({'mode': 'callingMain'}))])
	if upcoming is False:
		entries.append([translation(30654), 'Action(Queue)'])
	LEM.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LEM)
