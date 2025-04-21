# -*- coding: utf-8 -*-

from .common import *
from .resolver import *


def mainMenu():
	for TITLE, IMG, PATH in [(30601, 'favourites', {'mode': 'listFavorites'}), (30602, 'beliebteste', {'mode': 'listBroadcasts', 'url': '/top.json', 'extras': 'shows'}),
		(30603, 'trends', {'mode': 'listBroadcasts', 'url': '/trends.json', 'extras': 'shows'}), (30604, 'highlights', {'mode': 'listBroadcasts', 'url': '/index.json', 'extras': 'highlights'}),
		(30605, 'stations', {'mode': 'listTopics', 'url': '/index.json', 'extras': 'stations'}), (30606, 'categories', {'mode': 'listTopics', 'url': '/index.json', 'extras': 'categories'}),
		(30607, 'justfound', {'mode': 'listBroadcasts', 'url': '/index.json', 'extras': 'justFound'}), (30608, 'expiring', {'mode': 'listBroadcasts', 'url': '/index.json', 'extras': 'expiring'}),
		(30609, 'vonabisz', {'mode': 'listAlphabet', 'extras': 'letter_A-Z'}), (30610, 'archive', {'mode': 'filtrateSearch', 'url': '/search.json', 'extras': 'searchFILTRATE'}),
		(30611, 'basesearch', {'mode': 'SearchSEVER', 'extras': 'searchWORD'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}{IMG}.png"}))
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30612), 'Image': f"{artpic}settings.png"}), folder=False)
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive'):
			addDir({'mode': 'iConfigs'}, create_entries({'Title': translation(30613), 'Image': f"{artpic}settings.png"}), folder=False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTopics(TARGET, CAT, WANTED):
	debug_MS("(navigator.listTopics) ------------------------------------------------ START = listTopics -----------------------------------------------")
	debug_MS(f"(navigator.listTopics) ### TARGET = {TARGET} ### CATEGORY = {CAT} ### WANTED = {WANTED} ###")
	DATA_ONE = getContent(TARGET, REF=BASE_URL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.listTopics[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if 'index.json' in TARGET and DATA_ONE is not None and DATA_ONE.get('pageProps', '') and DATA_ONE['pageProps'].get(CAT, ''):
		for item in sorted(DATA_ONE['pageProps'].get(CAT, []), key=lambda vsx: cleanUmlaut(vsx.get('name', 'zorro')).lower()):
			if not item.get('name', ''): continue
			slug = quote_plus(item['slug'])
			name = cleaning(item['name'])
			if CAT == 'stations' and showARTE is False and name.upper() in ARTEEX: continue
			if CAT == 'stations' and showJOYN is False and name.upper() in JOYNEX: continue
			if CAT == 'stations' and showRTL is False and name.upper() in RTLEX: continue
			image = f"{BASE_URL[:-1]}{item['logoWhite']}" if CAT == 'stations' and item.get('logoWhite', '') else \
				f"{genpic}{slug.lower()}.png" if CAT == 'categories' and xbmcvfs.exists(f"{genpic}{slug.lower()}.png") else icon
			NEW_URL = f"/{slug}.json" if CAT == 'stations' else f"/rubriken/{slug}.json"
			addDir({'mode': 'subTopics', 'url': NEW_URL, 'extras': CAT}, create_entries({'Title': name, 'Image': image}))
			debug_MS(f"(navigator.listTopics[2]) ### NAME : {name} || SLUG : {slug} || IMAGE : {image} ###")
	elif 'a-z.json' in TARGET and DATA_ONE is not None and DATA_ONE.get('pageProps', '') and DATA_ONE['pageProps'].get(CAT, ''):
		for item in DATA_ONE['pageProps'].get(CAT, []):
			if item.get('letter') == WANTED:
				for each in sorted(item.get('items', []), key=lambda vsx: cleanUmlaut(vsx.get('name', 'zorro')).lower()):
					if not each.get('name', ''): continue
					(FETCH_UNO, context), (plot, genre, studio), operation = ({} for _ in range(2)), ("" for _ in range(3)), 'adding'
					seriesID = each.get('id', '00')
					slug = quote_plus(each['slug'])
					name = origSERIE = cleaning(each['name'])
					if each.get('categories', '') and each.get('categories', {})[0].get('name', ''):
						genre = cleaning(each['categories'][0]['name']).replace('/', ' / ').title()
					if each.get('stations', '') and each.get('stations', {})[0].get('name', ''):
						studio = each['stations'][0]['name']
						plot = translation(30621).format(genre, studio)
						name = f"{name}  ({studio.upper()})" if showCHANFOLD else name
						if showARTE is False and studio.upper() in ARTEEX: continue
						if showJOYN is False and studio.upper() in JOYNEX: continue
						if showRTL is False and studio.upper() in RTLEX: continue
					FETCH_UNO = context = {'Cid': seriesID, 'Slug': slug, 'Extra': 'shows', 'Serie': origSERIE, \
						'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': studio, 'Image': f"{alppic}{WANTED}.jpg"}
					if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
						for article in preserve(FAVORIT_FILE):
							if article.get('Cid') == seriesID: operation = 'skipping'
					addDir({'mode': 'listBroadcasts', 'url': f"/sendungen/{slug}.json", 'extras': 'shows', 'transmit': origSERIE}, create_entries(FETCH_UNO), True, context, operation)
					debug_MS(f"(navigator.listTopics[2]) ### NAME : {name} || CID : {seriesID} || SLUG : {slug} || GENRE : {genre} || STUDIO : {studio} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def subTopics(TARGET, CAT):
	debug_MS("(navigator.subTopics) ------------------------------------------------ START = subTopics -----------------------------------------------")
	debug_MS(f"(navigator.subTopics) ### TARGET = {TARGET} ### CATEGORY = {CAT} ###")
	DATA_ONE = getContent(TARGET, REF=BASE_URL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.subTopics[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	for item in DATA_ONE.get('pageProps', []):
		COMBI = [obj for obj in traversing.get_records()['specifications'] if obj.get('short') == item]
		if COMBI and item[:5] not in CAT and len(DATA_ONE.get('pageProps', {}).get(item, '')) > 0:
			name = COMBI[0]['name']
			image = f"{genpic}{item.lower()}.png" if xbmcvfs.exists(f"{genpic}{item.lower()}.png") else icon
			addDir({'mode': 'listBroadcasts', 'url': TARGET, 'extras': item, 'transmit': name}, create_entries({'Title': name, 'Image': image}))
			debug_MS(f"(navigator.subTopics[2]) ### NAME : {name} || SLUG : {item} || IMAGE : {image} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
		addDir({'mode': 'listTopics', 'url': '/a-z.json', 'extras': 'series', 'transmit': letter}, create_entries({'Title': letter, 'Image': f"{alppic}{letter}.jpg"}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSEVER(CAT):
	debug_MS("(navigator.SearchSEVER) ------------------------------------------------ START = SearchSEVER -----------------------------------------------")
	# https://www.sendungverpasst.de/_next/data/cl7AR8ToJErdg4wnRFYGT/search.json?q=%22Rote+Rosen%22
	keyword = preserve(SEARCH_FILE, 'TEXT') if xbmcvfs.exists(SEARCH_FILE) else None
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30622), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword: preserve(SEARCH_FILE, 'TEXT', keyword)
	if keyword: return filtrateSearch(f'/search.json?q={quote_plus(keyword)}', CAT, keyword)
	return None

def filtrateSearch(TARGET, CAT, SERIE):
	debug_MS("(navigator.filtrateSearch) -------------------------------------------------- START = filtrateSearch --------------------------------------------------")
	debug_MS(f"(navigator.filtrateSearch) ### TARGET = {TARGET} ### CATEGORY = {CAT} ### SERIE : {SERIE} ###")
	if not 'cat=' in TARGET:
		addDir({'mode': 'selectionSearch', 'url': TARGET, 'extras': 'categories', 'transmit': SERIE}, create_entries({'Title': translation(30623)}))
	if not 'station=' in TARGET:
		addDir({'mode': 'selectionSearch', 'url': TARGET, 'extras': 'stations', 'transmit': SERIE}, create_entries({'Title': translation(30624)}))
	if not 'date=' in TARGET:
		addDir({'mode': 'selectionSearch', 'url': TARGET, 'extras': 'dates', 'transmit': SERIE}, create_entries({'Title': translation(30625)}))
	plus_SUFFIX = ('&', '?')[urlparse(TARGET).query == ''] + urlencode({'sort': 'date'})
	addDir({'mode': 'listBroadcasts', 'url': TARGET+plus_SUFFIX, 'extras': 'result', 'transmit': SERIE}, create_entries({'Title': translation(30626)}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionSearch(TARGET, CAT, SERIE):
	debug_MS("(navigator.selectionSearch) ------------------------------------------------ START = selectionSearch -----------------------------------------------")
	debug_MS(f"(navigator.selectionSearch) ### TARGET = {TARGET} ### CATEGORY = {CAT} ### SERIE : {SERIE} ###")
	DATA_ONE = getContent(TARGET, REF=BASE_URL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.selectionSearch[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('pageProps', '') and DATA_ONE['pageProps'].get(CAT, ''):
		elements = sorted(DATA_ONE['pageProps'].get(CAT, []), key=lambda vsx: cleanUmlaut(vsx.get('name', 'zorro')).lower()) if \
			CAT in ['categories', 'stations'] else DATA_ONE['pageProps'].get(CAT, [])
		for item in elements:
			if not item.get('name', ''): continue
			slug = str(item['key'])
			name = cleaning(item['name'])
			if CAT == 'stations' and showARTE is False and name.upper() in ARTEEX: continue
			if CAT == 'stations' and showJOYN is False and name.upper() in JOYNEX: continue
			if CAT == 'stations' and showRTL is False and name.upper() in RTLEX: continue
			counter = item.get('doc_count', None)
			if counter: name += f"   [B][COLOR yellow]({counter})[/COLOR][/B]"
			short_QUERY = CAT.replace('categories', 'cat').replace('stations', 'station').replace('dates', 'date')
			plus_SUFFIX = ('&', '?')[urlparse(TARGET).query == ''] + urlencode({short_QUERY: slug})
			addDir({'mode': 'filtrateSearch', 'url': TARGET+plus_SUFFIX, 'extras': CAT, 'transmit': SERIE}, create_entries({'Title': name}))
			debug_MS(f"(navigator.selectionSearch[2]) ### NAME : {name} || SLUG : {slug} || CAT : {CAT} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(TARGET, PAGE, LIMIT, POS, TYPE, SERIE):
	debug_MS("(navigator.listBroadcasts) ------------------------------------------------ START = listBroadcasts -----------------------------------------------")
	debug_MS(f"(navigator.listBroadcasts) ### TARGET = {TARGET} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### POSITION = {POS} ### TYPE = {TYPE} ### SERIE = {SERIE} ###")
	counter, POS, (COMBINATION, SENDING), DATA_ONE = 0, int(POS), ([] for _ in range(2)), getContent(TARGET, REF=BASE_URL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.listBroadcasts[1]) XXXXX CONTENT-01 : {DATA_ONE} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('pageProps', '') and (TYPE in DATA_ONE.get('pageProps', {}) or 'shows' in DATA_ONE.get('pageProps', {})):
		for key, value in DATA_ONE.get('pageProps', []).items():
			#debug_MS(f"(navigator.listBroadcasts) ##### KEY : {key} || VALUE : {value} #####")
			if (key in ['current', 'shows', 'show', 'moreShows'] or key == TYPE) and value is not None:
				elements = value if isinstance(value, list) else [value]
				for item in elements:
					(Note_1, Note_2, Note_3, Note_4, Note_5), (MORE_COLLECT, MORE_SEARCH) = ("" for _ in range(5)), ('DEFAULT' for _ in range(2))
					(folding, excluding), (studio, season, episode, startTIMES, aired, begins, endTIMES, genre) = (True for _ in range(2)), (None for _ in range(8))
					seriesENTRY = item
					item = item['_source'] if item.get('_source', '') else item
					debug_MS(f"(navigator.listBroadcasts[2]) ##### ELEMENT-02 : {item} #####")
					episID = item.get('id', '00')
					slug = quote_plus(item['slug']) if item.get('slug', '') else None
					Note_4 = cleaning(item['description']) if item.get('description', '') else ""
					if item.get('stations', '') and item.get('stations', {})[0].get('name', ''):
						studio = item['stations'][0]['name']
						Note_5 = translation(30634).format(studio) if Note_4 != "" else translation(30635).format(studio)
						if showARTE is False and studio.upper() in ARTEEX: continue
						if showJOYN is False and studio.upper() in JOYNEX: continue
						if showRTL is False and studio.upper() in RTLEX: continue
					POS += 1
					counter += 1
					name = extractor = cleaning(item['fullTitle']) if item.get('fullTitle', '') else cleaning(item['title']) if item.get('title', '') else \
						cleaning(item['name']) if item.get('name', '') else 'UNBEKANNT'
					if any(xu in TARGET for xu in ['/trends.', '/top.']) or 'top20' in TYPE:
						name = translation(30627).format(counter, name)
					seriesname = cleaning(item['show']) if item.get('show', '') else None # STANDARD=shows - SEARCH=result
					origSERIE = seriesname if seriesname else SERIE
					direct = (item.get('link', None) or None)
					duration = int(item['duration']) * 60 if str(item.get('duration')).isdecimal() else None
					if direct and duration:
						MORE_COLLECT = f"/content/{slug}.json" if slug and key not in ['show', 'moreShows', 'result'] else 'DEFAULT' # ERLAUBT: show, moreShows, result
						MORE_SEARCH = f"/search.json?q={quote_plus(seriesname)}&sort=date" if seriesname and key in ['show', 'moreShows'] and \
							DATA_ONE.get('pageProps', {}).get('hasMore', '') is True else 'DEFAULT' # ERLAUBT: show, moreShows
						folding, excluding = False, False
					elif direct is None and duration is None and slug:
						folding, excluding = True, False
					if excluding is True: continue
					views = (item.get('clicks', None) or None)
					if seriesname and views: Note_1 = translation(30628).format(seriesname, str(views))
					elif seriesname and views is None: Note_1 = translation(30629).format(seriesname)
					matchSEA = re.search(r'(Staffel:? |S)([0-9]+)', extractor) # Staffel 13, Folge 05 // Staffel: 6, Folge: 11 // (S01/E03) // (1/3) // Rote Rosen: (1094)
					if matchSEA: season = f"{int(matchSEA.group(2)):02}" if str(matchSEA.group(2)).isdecimal() and int(matchSEA.group(2)) != 0 else None
					if season is None:
						matchSON = re.search(r'\(([0-9]+)/[0-9]+\)', extractor) # Staffel 13, Folge 05 // Staffel: 6, Folge: 11 // (S01/E03) // (1/3) // Rote Rosen: (1094)
						if matchSON: season = f"{int(matchSON.group(1)):02}" if str(matchSON.group(1)).isdecimal() and int(matchSON.group(1)) != 0 else None
					matchEPI = re.search(r'(Episode:? |Folge:? |E)([0-9]+)', extractor) # Staffel 13, Folge 05 // Staffel: 6, Folge: 11 // (S01/E03) // (1/3) // Rote Rosen: (1094)
					if matchEPI: episode = f"{int(matchEPI.group(2)):02}" if str(matchEPI.group(2)).isdecimal() and int(matchEPI.group(2)) != 0 else None
					if episode is None:
						matchODE = re.search(r'\([0-9]+/([0-9]+)\)', extractor) # Staffel 13, Folge 05 // Staffel: 6, Folge: 11 // (S01/E03) // (1/3) // Rote Rosen: (1094)
						if matchODE: episode = f"{int(matchODE.group(1)):02}" if str(matchODE.group(1)).isdecimal() and int(matchODE.group(1)) != 0 else None
					if episode is None:
						matchISO = re.search(r' \(([0-9]+)\)', extractor) # Staffel 13, Folge 05 // Staffel: 6, Folge: 11 // (S01/E03) // (1/3) // Rote Rosen: (1094)
						if matchISO: episode = f"{int(matchISO.group(1)):02}" if str(matchISO.group(1)).isdecimal() and int(matchISO.group(1)) != 0 else None
					if season and episode: Note_2 = translation(30630).format(season, episode)
					elif season is None and episode: Note_2 = translation(30631).format(episode)
					tagline = cleaning(item.get('subtitle', ''))
					if item.get('datetime', '') and str(item.get('datetime')[:10].replace('.', '').replace('-', '').replace('/', '')).isdecimal():
						broadcast = datetime(*(time.strptime(item['datetime'][:16], '%d.%m.%Y %H:%M')[0:6])) # 20.12.2023 20:15
						startTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
						aired = broadcast.strftime('%d.%m.%Y') # FirstAired
						begins = broadcast.strftime('%Y-%m-%dT%H:%M') if KODI_ov20 else broadcast.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
					if item.get('expiryDate', '') and str(item.get('expiryDate')[:10].replace('.', '').replace('-', '').replace('/', '')).isdecimal():
						ending = datetime(*(time.strptime(item['expiryDate'][:16], '%d.%m.%Y %H:%M')[0:6])) # 27.12.2023 00:00
						endTIMES = ending.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
					if startTIMES and endTIMES: Note_3 = translation(30632).format(startTIMES, endTIMES)
					elif startTIMES and endTIMES is None: Note_3 = translation(30633).format(startTIMES)
					elif seriesname and startTIMES is None and endTIMES is None: Note_3 = '[CR]'
					photo = IMG_cover.format(item['image']) if item.get('image', '') else icon
					if str(list(seriesENTRY.values())[0]) == 'series' and photo == icon and slug:
						photo = IMG_cover.format(f"series/{cleanUmlaut(item['slug'])}.jpg")
					if item.get('categories', '') and item.get('categories', {})[0].get('name', ''):
						genre = cleaning(item['categories'][0]['name']).replace('/', ' / ').title()
					plot = Note_1+Note_2+Note_3+Note_4+Note_5
					COMBINATION.append([POS, folding, name, seriesname, origSERIE, episID, slug, tagline, plot, duration, season, episode, \
						begins, aired, genre, studio, photo, direct, MORE_COLLECT, MORE_SEARCH])
	if COMBINATION:
		parts = COMBINATION[:]
		matching = [psx for psx in parts if psx[15] == parts[0][15]]
		plus_STUDIO = True if len(matching) != len(COMBINATION) else False
		for xev in COMBINATION:
			# [POS=0, folding=1, name=2, seriestitle=3, origSERIE=4, episID=5, slug=6, tagline=7, plot=8, duration=9, season=10, episode=11]
			# [begins=12, aired=13, genre=14, studio=15, photo=16, direct=17, MORE_COLLECT=18, MORE_SEARCH=19]
			xev[2] = f"{xev[2]}  ({xev[15].upper()})" if showCHANLINK and plus_STUDIO else xev[2]
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listBroadcasts[3]) ##### TITLE : {xev[2]} || SEASON : {xev[10]} || EPISODE : {xev[11]} || AIRED : {xev[13]} #####")
			debug_MS(f"(navigator.listBroadcasts[3]) ##### SLUG : {xev[6]} || CID : {xev[5]} || GENRE : {xev[14]} || STUDIO : {xev[15]} || THUMB : {xev[16]} #####")
			FETCHING = {'Slug': xev[6], 'Title': xev[2], 'TvShowTitle': xev[3], 'Tagline': xev[7], 'Plot': xev[8], 'Season': xev[10], 'Episode': xev[11], \
				'Date': xev[12], 'Aired': xev[13], 'Genre': xev[14], 'Studio': xev[15], 'Image': xev[16]}
			if xev[1] is True:
				folder, ACTION = True, {'mode': 'listBroadcasts', 'url': f"/sendungen/{xev[6]}.json", 'extras': 'shows', 'transmit': xev[2]}
				FETCH_UNO = create_entries(FETCHING)
			else:
				for method in get_Sorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
				folder, ACTION = False, {'mode': 'playCODE', 'IDENTiTY': xev[5]}
				FETCH_UNO = create_entries({**FETCHING, **{'Duration': xev[9], 'Mediatype': 'episode' if str(xev[11]).isdecimal() else 'movie', 'Reference': 'Single'}})
				if xev[3] and xev[18] != 'DEFAULT': # cyan, magenta, springgreen
					FETCH_UNO.addContextMenuItems([(translation(30655).format(xev[3]), f"Container.Update({build_mass(HOST_AND_PATH, {'mode': 'listBroadcasts', 'url': API_COMP+xev[18], 'extras': 'show', 'transmit': xev[3]})})")])
				if xev[3] and xev[19] != 'DEFAULT': # cyan, magenta, springgreen
					FETCH_UNO.addContextMenuItems([(translation(30656), f"Container.Update({build_mass(HOST_AND_PATH, {'mode': 'listBroadcasts', 'url': API_COMP+xev[19], 'extras': 'result', 'transmit': xev[3]})})")])
				SENDING.append({'filter': xev[5], 'name': xev[2], 'tvshow': xev[3], 'station': xev[15], 'direct': xev[17]})
			addDir(ACTION, FETCH_UNO, folder)
		preserve(WORKS_FILE, 'JSON', SENDING)
		if DATA_ONE is not None and DATA_ONE.get('pageProps', '') and DATA_ONE.get('pageProps', {}).get('total', '') and \
			isinstance(DATA_ONE['pageProps']['total'], int) and int(DATA_ONE['pageProps']['total']) > int(PAGE)*int(LIMIT):
			debug_MS(f"(navigator.listBroadcasts[4]) PAGES ### currentENTRIES : {int(PAGE)*int(LIMIT)} from totalENTRIES : {DATA_ONE['pageProps']['total']} ###")
			plus_SUFFIX = ('&', '?')[urlparse(TARGET).query == ''] + urlencode({'page': int(PAGE)+1}) if int(PAGE) == 1 else f"page={int(PAGE)+1}"
			FETCH_DUE = create_entries({'Title': translation(30636).format(int(PAGE)+1), 'Image': f"{artpic}nextpage.png"})
			addDir({'mode': 'listBroadcasts', 'url': TARGET.split('page=')[0]+plus_SUFFIX, 'page': int(PAGE)+1, 'limit': int(LIMIT), 'position': int(POS), 'extras': TYPE, 'transmit': origSERIE}, FETCH_DUE)
	else:
		failing(f'(navigator.listBroadcasts) ##### NO BROADCAST-LIST - NO ENTRY FOR: "{SERIE}" FOUND #####')
		return dialog.notification(translation(30525), translation(30526).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playCODE(PLID):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### SENDUNGVERPASST_CID : {PLID} ###")
	FINAL_URL, CLEAR_TITLE, TVSHOW, LINK = (False for _ in range(4))
	for elem in preserve(WORKS_FILE):
		if elem['filter'] != '00' and elem['filter'] == PLID:
			CLEAR_TITLE = re.sub('\[.*?\]', '', elem['name']) if elem.get('name', '') else False
			TVSHOW, STATION, LINK = elem['tvshow'], elem['station'], elem['direct']
			debug_MS(f"(navigator.playCODE) ### WORKS_FILE-Line : {elem} ###")
	LINK = LINK.replace('http://', 'https://') if LINK and LINK[:7] == 'http://' else LINK
	log("(navigator.playCODE) --- START WIEDERGABE ANFORDERUNG ---")
	log("(navigator.playCODE[1]) frei")
	log(f"(navigator.playCODE[1]) ~~~ AbspielLink-01 (Original) : {LINK} ~~~")
	log("(navigator.playCODE[1]) frei")
	if LINK and LINK.startswith('https://www.ardmediathek.de'):
		return ArdGetVideo(LINK)
	elif LINK and LINK.startswith('https://www.arte.tv'):
		videoID = re.compile('arte.tv/de/videos/([^/]+?)/', re.S).findall(LINK)[0]
		FINAL_URL = f"plugin://plugin.video.tyl0re.arte/?mode=playVideo&url={videoID}"
		return playRESOLVED(FINAL_URL, 'TRANSMIT', 'ARTE.TV', 'ARTE.TV - Plugin')
	elif LINK and LINK.startswith('https://www.dw.com'):
		return DwGetVideo(LINK)
	elif LINK and LINK.startswith('https://www.joyn.de'):
		return JoynGetVideo(LINK)
	elif LINK and LINK.startswith('https://www.kika.de'):
		return KikaGetVideo(LINK)
	elif LINK and LINK.startswith('https://plus.rtl.de'):
		videoHUB = re.search('(\d+)', LINK.split('-')[-1])
		if videoHUB: # https://plus.rtl.de/video-tv/serien/alles-was-zaehlt-146430/2023-12-984414/episode-4351-niemand-ahnt-welch-waghalsigen-plan-justus-schmiedet-927644
			PREDICATE = 'movie' if 'filme/' in LINK else 'episode' # shows + serien
			FINAL_URL = f"plugin://plugin.video.tvnow.de/?action=playVod&id=rrn:watch:videohub:{PREDICATE}:{videoHUB.group(1)}"
		return playRESOLVED(FINAL_URL, 'TRANSMIT', 'RTL+ - Webversion', 'RTL+ - Plugin')
	elif LINK and LINK.startswith(('https://www.3sat.de', 'https://www.phoenix.de', 'https://zdf.de', 'https://www.zdf.de')):
		LINK = LINK.replace('https://zdf.de', 'https://www.zdf.de')
		return ZdfGetVideo(LINK)
	else:
		failing(f"(navigator.playCODE[2]) AbspielLink-00 : Der Provider *{urlparse(LINK).netloc}* konnte nicht aufgelöst werden !!!")
		dialog.notification(translation(30521).format('LINK'), translation(30527).format(urlparse(LINK).netloc), icon, 8000)
		log("(navigator.playCODE[2]) --- ENDE WIEDERGABE ANFORDERUNG ---")

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		for each in sorted(preserve(FAVORIT_FILE), key=lambda vsx: cleanUmlaut(vsx.get('Serie', 'zorro')).lower()):
			FETCH_UNO, context = ({} for _ in range(2))
			ACTION = {'mode': 'listBroadcasts', 'url': f"/sendungen/{each.get('Slug')}.json", 'extras': each.get('Extra'), 'transmit': each.get('Serie')}
			FETCH_UNO = context = {'Cid': each.get('Cid'), 'Slug': each.get('Slug'), 'Extra': each.get('Extra'), 'Serie': each.get('Serie'), \
				'Title': each.get('Serie'), 'Plot': each.get('Plot'), 'Genre': each.get('Genre'), 'Studio': each.get('Studio'), 'Image': each.get('Image')}
			debug_MS(f"(navigator.listFavorites[1]) ##### NAME : {each.get('Title')} || CID : {each.get('Cid')} || SLUG : {each.get('Slug')} || THUMB : {each.get('Image')} #####")
			addDir(ACTION, create_entries(FETCH_UNO), True, context, 'removing')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favorit_construct(**kwargs):
	TOPS = []
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		TOPS = preserve(FAVORIT_FILE)
	if kwargs['action'] == 'ADD':
		del kwargs['mode']; del kwargs['action']
		TOPS.append({key: value if value != 'None' else None for key, value in kwargs.items()})
		preserve(FAVORIT_FILE, 'JSON', TOPS)
		xbmc.sleep(500)
		dialog.notification(translation(30532), translation(30533).format(kwargs['Serie']), icon, 8000)
	elif kwargs['action'] == 'DEL':
		TOPS = [xs for xs in TOPS if xs.get('Cid') != kwargs.get('Cid')]
		preserve(FAVORIT_FILE, 'JSON', TOPS)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30532), translation(30534).format(kwargs['Serie']), icon, 8000)

def addDir(params, listitem, folder=True, context={}, handling='default'):
	uws, entries = build_mass(HOST_AND_PATH, params), []
	listitem.setPath(uws)
	if handling == 'adding' and context:
		entries.append([translation(30651), f"RunPlugin({build_mass(HOST_AND_PATH, {**context, **{'mode': 'favorit_construct', 'action': 'ADD'}})})"])
	if handling == 'removing' and context:
		entries.append([translation(30652), f"RunPlugin({build_mass(HOST_AND_PATH, {**context, **{'mode': 'favorit_construct', 'action': 'DEL'}})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
