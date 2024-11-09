# -*- coding: utf-8 -*-

from .common import *
from .resolver import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

def mainMenu():
	addDir(translation(30601), f"{artpic}favourites.png", {'mode': 'listFavorites'})
	addDir(translation(30602), f"{artpic}beliebteste.png", {'mode': 'listEpisodes', 'url': '/top.json', 'extras': 'shows'})
	addDir(translation(30603), f"{artpic}trends.png", {'mode': 'listEpisodes', 'url': '/trends.json', 'extras': 'shows'})
	addDir(translation(30604), f"{artpic}highlights.png", {'mode': 'listEpisodes', 'url': '/index.json', 'extras': 'highlights'})
	addDir(translation(30605), f"{artpic}stations.png", {'mode': 'listTopics', 'url': '/index.json', 'extras': 'stations'})
	addDir(translation(30606), f"{artpic}categories.png", {'mode': 'listTopics', 'url': '/index.json', 'extras': 'categories'})
	addDir(translation(30607), f"{artpic}justfound.png", {'mode': 'listEpisodes', 'url': '/index.json', 'extras': 'justFound'})
	addDir(translation(30608), f"{artpic}expiring.png", {'mode': 'listEpisodes', 'url': '/index.json', 'extras': 'expiring'})
	addDir(translation(30609), f"{artpic}vonabisz.png", {'mode': 'listAlphabet', 'extras': 'letter_A-Z'})
	addDir(translation(30610), f"{artpic}archive.png", {'mode': 'filtrateSearch', 'url': '/search.json', 'extras': 'searchFILTRATE'})
	addDir(translation(30611), f"{artpic}basesearch.png", {'mode': 'SearchSEVER', 'url': '/search.json?q=%22{}%22', 'extras': 'searchWORD'})
	if enableADJUSTMENT:
		addDir(translation(30612), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30613), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTopics(url, CAT, WANTED):
	debug_MS("(navigator.listTopics) ------------------------------------------------ START = listTopics -----------------------------------------------")
	debug_MS(f"(navigator.listTopics) ### URL = {url} ### CATEGORY = {CAT} ### WANTED = {WANTED} ###")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	DATA = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.listTopics[1]) XXXXX CONTENT-01 : {str(DATA)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if 'index.json' in url and DATA is not None and DATA.get('pageProps', '') and DATA['pageProps'].get(CAT, ''):
		for item in DATA['pageProps'].get(CAT, []):
			if not item.get('name', ''): continue
			slug = quote_plus(item['slug'])
			name = cleaning(item['name'])
			if CAT == 'stations':
				if showARTE is False and name.upper() in ARTEEX: continue
				if showJOYN is False and name.upper() in JOYNEX: continue
				if showRTL is False and name.upper() in RTLEX: continue
			image = f"{BASE_URL[:-1]}{item['logoWhite']}" if item.get('logoWhite', '') else icon
			NEW_URL = f"/{slug}.json"
			if CAT == 'categories':
				image = f"{genpic}{slug.lower()}.png" if xbmcvfs.exists(f"{genpic}{slug.lower()}.png") else icon
				NEW_URL = f"/rubriken/{slug}.json"
			addDir(name, image, {'mode': 'subTopics', 'url': NEW_URL, 'extras': CAT}, background=False)
			debug_MS(f"(navigator.listTopics[2]) ### NAME : {name} || SLUG : {slug} || IMAGE : {image} ###")
	elif 'a-z.json' in url and DATA is not None and DATA.get('pageProps', '') and DATA['pageProps'].get(CAT, ''):
		for item in DATA['pageProps'].get(CAT, []):
			if item.get('letter', '') == WANTED:
				for each in item.get('items', []):
					if not each.get('name', ''): continue
					plot, genre, studio = ("" for _ in range(3))
					seriesID = each.get('id', '00')
					slug = quote_plus(each['slug'])
					name, origSERIE = cleaning(each['name']), cleaning(each['name'])
					if each.get('categories', '') and each.get('categories', {})[0].get('name', ''):
						genre = cleaning(each['categories'][0]['name'])
					if each.get('stations', '') and each.get('stations', {})[0].get('name', ''):
						studio = each['stations'][0]['name']
						plot = translation(30621).format(genre, studio)
						if showCHANFOLD:
							name += f"  ({studio.upper()})"
						if showARTE is False and studio.upper() in ARTEEX: continue
						if showJOYN is False and studio.upper() in JOYNEX: continue
						if showRTL is False and studio.upper() in RTLEX: continue
					NEW_URL = f"/sendungen/{slug}.json"
					addType = 1
					if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
						with open(channelFavsFile, 'r') as fp:
							watch = json.load(fp)
							for item in watch.get('items', []):
								if item.get('ident') == seriesID: addType = 2
					addDir(name, f"{alppic}{WANTED}.jpg", {'mode': 'listEpisodes', 'url': NEW_URL, 'extras': 'shows', 'transmit': origSERIE, 'ident': seriesID}, plot, genre, studio, addType, background=False)
					debug_MS(f"(navigator.listTopics[2]) ### NAME : {name} || IDD : {seriesID} || SLUG : {slug} || STUDIO : {studio} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def subTopics(url, CAT):
	debug_MS("(navigator.subTopics) ------------------------------------------------ START = subTopics -----------------------------------------------")
	debug_MS(f"(navigator.subTopics) ### URL = {url} ### CATEGORY = {CAT} ###")
	RECORDS = traversing.get_records()
	DATA = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.subTopics[1]) XXXXX CONTENT-01 : {str(DATA)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	for item in DATA.get('pageProps', []):
		COMBI = [obj for obj in RECORDS['specifications'] if obj.get('short') == item]
		if COMBI and item[:5] not in CAT and len(DATA.get('pageProps', {}).get(item, '')) > 0:
			name = COMBI[0]['name']
			image = f"{genpic}{item.lower()}.png" if xbmcvfs.exists(f"{genpic}{item.lower()}.png") else icon
			addDir(name, image, {'mode': 'listEpisodes', 'url': url, 'extras': item, 'transmit': name}, background=False)
			debug_MS(f"(navigator.subTopics[2]) ### NAME : {name} || SLUG : {item} || IMAGE : {image} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
		addDir(letter, f"{alppic}{letter}.jpg", {'mode': 'listTopics', 'url': '/a-z.json', 'extras': 'series', 'wanted': letter}, background=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSEVER(url, CAT):
	debug_MS("(navigator.SearchSEVER) ------------------------------------------------ START = SearchSEVER -----------------------------------------------")
	# https://www.sendungverpasst.de/_next/data/cl7AR8ToJErdg4wnRFYGT/search.json?q=%22Rote+Rosen%22
	keyword = None
	if xbmcvfs.exists(SEARCHFILE):
		with open(SEARCHFILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30622), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote_plus(keyword)
			with open(SEARCHFILE, 'w') as record:
				record.write(keyword)
	if keyword: return filtrateSearch(url.format(keyword), CAT, unquote_plus(keyword))
	return None

def filtrateSearch(url, CAT, SERIE):
	debug_MS("(navigator.filtrateSearch) -------------------------------------------------- START = filtrateSearch --------------------------------------------------")
	debug_MS(f"(navigator.filtrateSearch) ### URL = {url} ### CATEGORY = {CAT} ### SERIE : {SERIE} ###")
	if not 'cat=' in url:
		addDir(translation(30623), icon, {'mode': 'selectionSearch', 'url': url, 'extras': 'categories', 'transmit': SERIE})
	if not 'station=' in url:
		addDir(translation(30624), icon, {'mode': 'selectionSearch', 'url': url, 'extras': 'stations', 'transmit': SERIE})
	if not 'date=' in url:
		addDir(translation(30625), icon, {'mode': 'selectionSearch', 'url': url, 'extras': 'dates', 'transmit': SERIE})
	plus_SUFFIX = ('&', '?')[urlparse(url).query == ''] + urlencode({'sort': 'date'})
	addDir(translation(30626), icon, {'mode': 'listEpisodes', 'url': url+plus_SUFFIX, 'extras': 'result', 'transmit': SERIE})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionSearch(url, CAT, SERIE):
	debug_MS("(navigator.selectionSearch) ------------------------------------------------ START = selectionSearch -----------------------------------------------")
	debug_MS(f"(navigator.selectionSearch) ### URL = {url} ### CATEGORY = {CAT} ### SERIE : {SERIE} ###")
	if CAT in ['categories', 'stations']:
		xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
		xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	DATA_ONE = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.selectionSearch[1]) XXXXX CONTENT-01 : {str(DATA_ONE)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_ONE is not None and DATA_ONE.get('pageProps', '') and DATA_ONE['pageProps'].get(CAT, ''):
		for item in DATA_ONE['pageProps'].get(CAT, []):
			if not item.get('name', ''): continue
			slug = str(item['key'])
			name = cleaning(item['name'])
			if CAT == 'stations':
				if showARTE is False and name.upper() in ARTEEX: continue
				if showJOYN is False and name.upper() in JOYNEX: continue
				if showRTL is False and name.upper() in RTLEX: continue
			counter = item.get('doc_count', None)
			if counter: name += f"   [B][COLOR yellow]({str(counter)})[/COLOR][/B]"
			short_QUERY = CAT.replace('categories', 'cat').replace('stations', 'station').replace('dates', 'date')
			plus_SUFFIX = ('&', '?')[urlparse(url).query == ''] + urlencode({short_QUERY: slug})
			addDir(name, icon, {'mode': 'filtrateSearch', 'url': url+plus_SUFFIX, 'extras': CAT, 'transmit': SERIE})
			debug_MS(f"(navigator.selectionSearch[2]) ### NAME : {name} || SLUG : {slug} || CAT : {CAT} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(url, PAGE, LIMIT, POS, TYPE, SERIE):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS(f"(navigator.listEpisodes) ### URL : {url} ### PAGE : {PAGE} ### LIMIT : {LIMIT} ### POSITION : {POS} ### TYPE : {TYPE} ### SERIE : {SERIE} ###")
	PAGE, LIMIT, POS = int(PAGE), int(LIMIT), int(POS)
	counter, SEND, UNIKAT = 0, {}, set()
	COMBI_EPISODE, SEND['videos'] = ([] for _ in range(2))
	DATA_TWO = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(navigator.listEpisodes[1]) XXXXX CONTENT-01 : {str(DATA_TWO)} XXXXX")
	debug_MS("++++++++++++++++++++++++")
	if DATA_TWO is not None and DATA_TWO.get('pageProps', '') and (TYPE in DATA_TWO.get('pageProps', {}) or 'shows' in DATA_TWO.get('pageProps', {})):
		for key, value in DATA_TWO.get('pageProps', []).items():
			#debug_MS(f"(navigator.listEpisodes) ##### KEY : {key} || VALUE : {value} #####")
			if (key in ['current', 'shows', 'show', 'moreShows'] or key == TYPE) and value is not None:
				elements = value if isinstance(value, list) else [value]
				for item in elements:
					studio, tagline, Note_1, Note_2, Note_3, Note_4, Note_5, genre = ("" for _ in range(8))
					seriesname, duration, views, season, episode, startTIMES, begins, aired, endTIMES = (None for _ in range(9))
					MORE_COLLECT, MORE_SEARCH = ('DEFAULT' for _ in range(2))
					seriesENTRY = item
					item = item['_source'] if item.get('_source', '') else item
					debug_MS(f"(navigator.listEpisodes[2]) ##### ELEMENT-02 : {str(item)} #####")
					episID = item.get('id', '00')
					slug = quote_plus(item['slug']) if item.get('slug', '') else None
					#if episID in UNIKAT:
						#continue
					#UNIKAT.add(episID)
					Note_4 = cleaning(item['description']) if item.get('description', '') else ""
					if item.get('stations', '') and item.get('stations', {})[0].get('name', ''):
						studio = item['stations'][0]['name']
						Note_5 = translation(30634).format(studio) if Note_4 != "" else translation(30635).format(studio)
						if showARTE is False and studio.upper() in ARTEEX: continue
						if showJOYN is False and studio.upper() in JOYNEX: continue
						if showRTL is False and studio.upper() in RTLEX: continue
					POS += 1
					counter += 1
					name = cleaning(item['fullTitle']) if item.get('fullTitle', '') else cleaning(item['title']) if item.get('title', '') else cleaning(item['name']) if item.get('name', '') else 'UNBEKANNT'
					if any(x in url for x in ['/trends.', '/top.']) or 'top20' in TYPE:
						name = translation(30627).format(str(counter), name)
					seriesname = cleaning(item['show']) if item.get('show', '') else None # STANDARD=shows - SEARCH=result
					link = (item.get('link', None) or None)
					duration = int(item['duration']) * 60 if str(item.get('duration')).isdigit() else None
					if link and duration:
						MORE_COLLECT = f"/content/{slug}.json" if slug and key not in ['show', 'moreShows', 'result'] else 'DEFAULT' # ERLAUBT: show, moreShows, result
						MORE_SEARCH = f"/search.json?q=%22{quote_plus(seriesname)}%22" if seriesname and key in ['show', 'moreShows'] and DATA_TWO.get('pageProps', {}).get('hasMore', '') is True else 'DEFAULT' # ERLAUBT: show, moreShows
						uvz = build_mass({'mode': 'playCODE', 'IDENTiTY': episID})
						folder = False
					elif link is None and duration is None and slug:
						NEW_URL = f"/sendungen/{slug}.json"
						uvz = build_mass({'mode': 'listEpisodes', 'url': NEW_URL, 'extras': 'shows', 'transmit': name})
						folder = True
					views = (item.get('clicks', None) or None)
					if seriesname and views: Note_1 = translation(30628).format(seriesname, str(views))
					elif seriesname and views is None: Note_1 = translation(30629).format(seriesname)
					matchSE = re.search('(Staffel:? |S)(\d+)', item['title']) if item.get('title', '') else None # "Staffel 13, Folge 05 - Ausgesetzt // Staffel: 6, Folge: 11 - Das große Finale - Teil 2 // S10 E213 // (2 /2)
					if matchSE: season = matchSE.group(2).zfill(2)
					matchEP = re.search('(Episode:? |Folge:? |E|\()(\d+)\)?', item['title']) if item.get('title', '') else None # "Staffel 13, Folge 05 - Ausgesetzt // Staffel: 6, Folge: 11 - Das große Finale - Teil 2 // S10 E213 // (2 /2)
					if matchEP: episode = matchEP.group(2).zfill(2)
					if season and episode: Note_2 = translation(30630).format(str(season), str(episode))
					elif season is None and episode: Note_2 = translation(30631).format(str(episode))
					tagline = cleaning(item.get('subtitle', ''))
					if item.get('datetime', '') and str(item.get('datetime')[:10].replace('.', '').replace('-', '').replace('/', '')).isdigit():
						broadcast = datetime(*(time.strptime(item['datetime'][:16], '%d{0}%m{0}%Y %H{1}%M'.format('.', ':'))[0:6])) # 20.12.2021 20:15
						startTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
						aired = broadcast.strftime('%d{0}%m{0}%Y').format('.') # FirstAired
						begins = broadcast.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
						if KODI_ov20:
							begins = broadcast.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
					if item.get('expiryDate', '') and str(item.get('expiryDate')[:10].replace('.', '').replace('-', '').replace('/', '')).isdigit():
						ending = datetime(*(time.strptime(item['expiryDate'][:16], '%d{0}%m{0}%Y %H{1}%M'.format('.', ':'))[0:6])) # 27.12.2021 00:00
						endTIMES = ending.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
					if startTIMES and endTIMES: Note_3 = translation(30632).format(str(startTIMES), str(endTIMES))
					elif startTIMES and endTIMES is None: Note_3 = translation(30633).format(str(startTIMES))
					elif seriesname and startTIMES is None and endTIMES is None: Note_3 = '[CR]'
					photo = IMG_cover.format(item['image']) if item.get('image', '') else icon
					if str(list(seriesENTRY.values())[0]) == 'series' and photo == icon and slug:
						photo = IMG_cover.format(f"series/{repair_umlaut(item['slug'])}.jpg")
					if item.get('categories', '') and item.get('categories', {})[0].get('name', ''):
						genre = cleaning(item['categories'][0]['name']).replace('/', ' / ')
					plot = Note_1+Note_2+Note_3+Note_4+Note_5
					COMBI_EPISODE.append([POS, uvz, folder, episID, link, MORE_SEARCH, MORE_COLLECT, name, photo, plot, tagline, duration, seriesname, season, episode, genre, studio, begins, aired])
	if COMBI_EPISODE:
		parts = COMBI_EPISODE[:]
		matching = [top for top in parts if top[14] == parts[0][14]]
		plus_STUDIO = True if len(matching) != len(COMBI_EPISODE) else False
		for POS, uvz, folder, episID, link, MORE_SEARCH, MORE_COLLECT, name, photo, plot, tagline, duration, seriesname, season, episode, genre, studio, begins, aired in COMBI_EPISODE:
			if not folder:
				for method in get_Sorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			cineType = 'episode' if str(episode).isdigit() else 'movie'
			if showCHANLINK and plus_STUDIO:
				name += f"  ({studio.upper()})"
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listEpisodes[3]) ##### NAME : {name} || IDD : {episID} || GENRE : {genre} #####")
			debug_MS(f"(navigator.listEpisodes[3]) ##### SERIE : {str(seriesname)} || SEASON : {str(season)} || EPISODE : {str(episode)} #####")
			debug_MS(f"(navigator.listEpisodes[3]) ##### IMAGE : {photo} || STUDIO : {studio} || TYPE : {cineType} #####")
			LSM = xbmcgui.ListItem(name)
			if plot in ['', 'None', None]: plot = "..."
			if KODI_ov20:
				vinfo = LSM.getVideoInfoTag()
				if str(season).isdigit(): vinfo.setSeason(int(season))
				if str(episode).isdigit(): vinfo.setEpisode(int(episode))
				if seriesname: vinfo.setTvShowTitle(seriesname)
				vinfo.setTitle(name)
				vinfo.setTagLine(tagline)
				vinfo.setPlot(plot)
				if str(duration).isdigit(): vinfo.setDuration(int(duration))
				if begins: LSM.setDateTime(begins)
				if aired: vinfo.setFirstAired(aired)
				if genre and len(genre) > 3: vinfo.setGenres([genre])
				vinfo.setStudios([studio])
				if not folder: vinfo.setMediaType(cineType)
			else:
				vinfo = {}
				if str(season).isdigit(): vinfo['Season'] = season
				if str(episode).isdigit(): vinfo['Episode'] = episode
				if seriesname: vinfo['Tvshowtitle'] = seriesname
				vinfo['Title'] = name
				vinfo['Tagline'] = tagline
				vinfo['Plot'] = plot
				if str(duration).isdigit(): vinfo['Duration'] = duration
				if begins: vinfo['Date'] = begins
				if aired: vinfo['Aired'] = aired
				if genre and len(genre) > 3: vinfo['Genre'] = genre
				vinfo['Studio'] = studio
				if not folder: vinfo['Mediatype'] = cineType
				LSM.setInfo('Video', vinfo)
			LSM.setArt({'icon': icon, 'thumb': photo, 'poster': photo, 'fanart': defaultFanart})
			if photo and useThumbAsFanart and photo != icon and not artpic in photo:
				LSM.setArt({'fanart': photo})
			if not folder:
				LSM.setProperty('IsPlayable', 'true')
				LSM.setContentLookup(False)
				entries = []
				entries.append([translation(30654), 'Action(Queue)'])
				if seriesname and MORE_COLLECT != 'DEFAULT': # cyan, magenta, springgreen
					entries.append([translation(30655).format(str(seriesname)), 'Container.Update({})'.format(build_mass({'mode': 'listEpisodes', 'url': API_COMP+MORE_COLLECT,
						'extras': 'show', 'transmit': seriesname}))])
				if seriesname and MORE_SEARCH != 'DEFAULT': # cyan, magenta, springgreen
					entries.append([translation(30656), 'Container.Update({})'.format(build_mass({'mode': 'listEpisodes', 'url': API_COMP+MORE_SEARCH, 'extras': 'result', 'transmit': seriesname}))])
				LSM.addContextMenuItems(entries)
				SEND['videos'].append({'filter': episID, 'url': link, 'name': name, 'tvshow': seriesname, 'station': studio})
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LSM, isFolder=folder)
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		if DATA_TWO is not None and DATA_TWO.get('pageProps', '') and DATA_TWO.get('pageProps', {}).get('total', '') and isinstance(DATA_TWO['pageProps']['total'], int) and int(DATA_TWO['pageProps']['total']) > int(PAGE)*int(LIMIT):
			debug_MS(f"(navigator.listEpisodes[4]) NUMBERING ### totalRESULTS : {str(DATA_TWO['pageProps']['total'])} ###")
			debug_MS(f"(navigator.listEpisodes[4]) NEXTPAGES ### Now show NextPage ... No.{str(int(PAGE)+1)} ... ###")
			origSERIE = seriesname if seriesname else SERIE
			if int(PAGE) == 1:
				plus_SUFFIX = ('&', '?')[urlparse(url).query == ''] + urlencode({'page': str(int(PAGE)+1)})
			else:
				url, plus_SUFFIX = url.split('page=')[0], f"page={str(int(PAGE)+1)}"
			addDir(translation(30636).format(int(PAGE)+1), f"{artpic}nextpage.png", {'mode': 'listEpisodes', 'url': url+plus_SUFFIX, 'page': int(PAGE)+1, 'limit': int(LIMIT), 'position': int(POS), 'extras': TYPE, 'transmit': origSERIE})
	else:
		debug_MS("(navigator.listEpisodes[2]) ##### Keine COMBI_EPISODE-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30525), translation(30526).format(SERIE), icon, 8000)
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### SENDUNGVERPASST_ID : {IDD} ###")
	FINAL_URL, LINK= (False for _ in range(2))
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] != '00' and elem['filter'] == IDD:
				LINK = elem['url']
				CLEAR_TITLE = re.sub('\[.*?\]', '', elem['name']) if elem.get('name', '') else None
				TVSHOW = elem['tvshow']
				STATION = elem['station']
				debug_MS(f"(navigator.playCODE[1]) ### WORKFILE-Line : {str(elem)} ###")
	LINK = LINK.replace('http://', 'https://') if LINK and LINK[:7] == 'http://' else LINK
	log("(navigator.playCODE) --- START WIEDERGABE ANFORDERUNG ---")
	log("(navigator.playCODE[1]) frei")
	log(f"(navigator.playCODE[1]) ~~~ AbspielLink (Original) : {str(LINK)} ~~~")
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
		return playRESOLVED(FINAL_URL, 'TRANSMIT', 'TvNow', 'TvNow - Plugin')
	elif LINK and LINK.startswith(('https://www.3sat.de', 'https://www.phoenix.de', 'https://zdf.de', 'https://www.zdf.de')):
		LINK = LINK.replace('https://zdf.de', 'https://www.zdf.de')
		return ZdfGetVideo(LINK)
	else:
		failing(f"(navigator.playCODE[2]) AbspielLink-00 : Der Provider *{urlparse(LINK).netloc}* konnte nicht aufgelöst werden !!!")
		dialog.notification(translation(30521).format('LINK', ''), translation(30527).format(urlparse(LINK).netloc), icon, 8000)
		log("(navigator.playCODE[2]) --- ENDE WIEDERGABE ANFORDERUNG ---")

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				debug_MS(f"(navigator.listFavorites[1]) ### NAME : {name} || URL : {item.get('url')} || IMAGE : {logo} ###")
				addDir(name, logo, {'mode': 'listEpisodes', 'url': item.get('url'), 'extras': 'shows', 'transmit': name, 'ident': item.get('ident')}, cleaning(item.get('plot')), cleaning(item.get('genre')), item.get('studio'), FAVclear=True, background=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'genre': genre, 'studio': studio, 'ident': ident})
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

def addDir(name, image, params={}, plot=None, genre=None, studio=None, addType=0, FAVclear=False, folder=True, background=True):
	u = build_mass(params)
	liz = xbmcgui.ListItem(name)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setGenres([genre]), vinfo.setStudios([studio])
	else:
		liz.setInfo('Video', {'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': studio})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image and background is True:
		liz.setArt({'fanart': image})
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'ADD', 'name': params.get('transmit', ''), 'pict': 'None' if image == icon else image,
			'url': params.get('url'), 'plot': plot.replace('\n', '[CR]'), 'genre': genre, 'studio': studio, 'ident': params.get('ident')}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image,
			'url': params.get('url'), 'plot': plot, 'genre': genre, 'studio': studio, 'ident': params.get('ident', '')}))])
	liz.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)
