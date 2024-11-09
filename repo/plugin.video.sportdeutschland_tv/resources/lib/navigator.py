# -*- coding: utf-8 -*-

from .common import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	(LIVE_ALL, SCORE_LIVE, SCORE_NEXT), config = (0 for _ in range(3)), traversing.get_config()
	COMBI_PAGES, COMBI_EVENTS, COMBI_LIVES = ([] for _ in range(3))
	if nowlive or upcoming:
		for ii in range(1, 13, 1):
			MURL = f"{config['HOME_LIVENEXT']}page={str(ii)}&per_page=50"
			debug_MS(f"(navigator.mainMenu[1]) LIVE+NEXT-PAGES XXX POS = {str(ii)} || URL = {MURL} XXX")
			COMBI_PAGES.append([int(ii), MURL])
		if COMBI_PAGES:
			COMBI_EVENTS = getMultiData(COMBI_PAGES)
			if COMBI_EVENTS:
				DATA_ONE = json.loads(COMBI_EVENTS)
				for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
					if results is not None and results.get('data', '') and len(results['data']) > 0:
						POS, DEM = results['Position'], results['Demand']
						POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT = get_Number(results, 'livestreams', POS, DEM)
						COMBI_LIVES.append([POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT])
		if COMBI_LIVES:
			LIVE_ALL, ONE_COUNT, LIVE_DEAD, LIVE_FREE, LIVE_PAY, NEXT_FREE, NEXT_PAY = COMBI_LIVES[0][2], charge(3, COMBI_LIVES), \
				charge(4, COMBI_LIVES), charge(5, COMBI_LIVES), charge(6, COMBI_LIVES), charge(7, COMBI_LIVES), charge(8, COMBI_LIVES)
			SCORE_LIVE  = (LIVE_ALL - sum([LIVE_DEAD, LIVE_PAY, NEXT_FREE, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else (LIVE_FREE - LIVE_DEAD)
			SCORE_NEXT = (LIVE_ALL - sum([LIVE_FREE, LIVE_PAY, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else NEXT_FREE
			debug_MS(f"(navigator.mainMenu[2]) COUNTERS *** NUM_EVENTS = {ONE_COUNT} || TOTAL_EVENTS = {LIVE_ALL} || SCORE_LIVE = {SCORE_LIVE} || FREE_LIVE = {LIVE_FREE} || PAY_LIVE = {LIVE_PAY} || SCORE_NEXT = {SCORE_NEXT} || FREE_NEXT = {NEXT_FREE} || PAY_NEXT = {NEXT_PAY} ***")
	if nowlive and SCORE_LIVE > 0:
		addDir(translation(30701).format(str(SCORE_LIVE)), f"{artpic}livestream.png", {'mode': 'listVideos', 'url': config['HOME_LIVENEXT'], 'limit': 50, 'wanted': 4, 'extras': 'playlive'}, translation(30702).format(str(SCORE_LIVE)))
	if upcoming and SCORE_NEXT > 0:
		addDir(translation(30703).format(str(SCORE_NEXT)), f"{artpic}upcoming.png", {'mode': 'listVideos', 'url': config['HOME_LIVENEXT'], 'limit': 50, 'wanted': 3, 'extras': 'playnext'}, translation(30704).format(str(SCORE_NEXT)))
	addDir(translation(30602), f"{artpic}favourites.png", {'mode': 'listFavorites'})
	if newest: addDir(translation(30603), icon, {'mode': 'listVideos', 'url': config['HOME_TOPS'], 'limit': 40, 'wanted': 2, 'extras': 'playnext'})
	if xbmcvfs.exists(menuFavsFile) and os.stat(menuFavsFile).st_size > 0:
		with open(menuFavsFile, 'r') as mp:
			points = json.load(mp)
			for elem in points.get('items', []):
				addDir(cleaning(elem.get('name')), icon, {'mode': 'listCategories', 'url': elem.get('slug'), 'code': elem.get('idd'), 'section': cleaning(elem.get('name')), 'limit': 20, 'wanted': 3, 'extras': 'tags', 'name': cleaning(elem.get('name'))}, genre=cleaning(elem.get('name')))
	if sporting: addDir(translation(30604), icon, {'mode': 'listSports', 'url': config['SPORT_TYPES'], 'limit': 20, 'wanted': 10, 'extras': 'sports', 'name': 'Sportarten'})
	if channeling: addDir(translation(30605), icon, {'mode': 'listSports', 'url': config['SPORT_PROFILE'], 'limit': 40, 'wanted': 25, 'extras': 'channels', 'name': 'Sportkanäle'})
	if teamsearch: addDir(translation(30606), f"{artpic}basesearch.png", {'mode': 'SearchSDTV', 'extras': 'PROFILEN'})
	if videosearch: addDir(translation(30607), f"{artpic}basesearch.png", {'mode': 'SearchSDTV', 'extras': 'VIDEOS'})
	addDir(translation(30608), f"{artpic}editmenu.png", {'mode': 'SELECTION', 'url': config['SPORT_TYPES'], 'limit': 20, 'wanted': 10}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30609), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30610), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def SELECTION(TARGET, PAGE, LIMIT, WANTED):
	debug_MS("(navigator.SELECTION) -------------------------------------------------- START = SELECTION --------------------------------------------------")
	PAGE, MAXIMUM = int(PAGE), int(PAGE)+int(WANTED)
	counter, FOLDERS = 0, {}
	COMBI_SITES, COMBI_SPORTS, STORED, NAMES, ENTRIES, FOLDERS['items'] = ([] for _ in range(6))
	for ii in range(PAGE, MAXIMUM, 1):
		SURL = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.SELECTION[1]) SELECTION-PAGES XXX POS = {str(ii)} || URL = {SURL} XXX")
		COMBI_SITES.append([int(ii), SURL])
	if COMBI_SITES:
		COMBI_SPORTS = getMultiData(COMBI_SITES)
		if COMBI_SPORTS:
			DATA_ONE = json.loads(COMBI_SPORTS)
			for contents in sorted(DATA_ONE, key=lambda sk: int(sk.get('Position', 0))):
				if contents is not None and contents.get('data', '') and len(contents['data']) > 0:
					for content in contents.get('data', []):
						if content.get('name', '') and content.get('id', '') and content.get('slug', ''):
							counter += 1
							NAMES.append(translation(30711).format(counter, str(content['name'])))
							ENTRIES.append({'number': counter, 'name': content['name'], 'idd': content['id'], 'slug': content['slug']})
			debug_MS("++++++++++++++++++++++++")
			debug_MS(f"(navigator.SELECTION[2]) XXXXX SPORTS-MENU-ENTRIES FROM PROVIDER : {ENTRIES} XXXXX")
			debug_MS("++++++++++++++++++++++++")
	if NAMES and ENTRIES:
		if xbmcvfs.exists(menuFavsFile) and os.stat(menuFavsFile).st_size > 0:
			with open(menuFavsFile, 'r') as present:
				positions = json.load(present)
				STORED = [(int(nr.get('number', 0)) - 1) for nr in positions.get('items', [])]
				debug_MS(f"(navigator.SELECTION[3]) ##### READING STORED INDEX OF USER-MENU-ENTRIES : {[int(nb.get('number', 0)) for nb in positions.get('items', [])]} #####")
		indicator = dialog.multiselect(translation(30712), NAMES, preselect=STORED)
		if indicator is None:
			debug_MS("(navigator.SELECTION[4]) <<<<< USER-MENU-ENTRIES NOT CHANGED - ACTION CANCELLED BY USER <<<<<")
			return
		FOLDERS['items'] = [ENTRIES[dm] for dm in indicator] if indicator else []
		if len(FOLDERS['items']) == 0:
			debug_MS("(navigator.SELECTION[5]) !!!!! USER-MENU-ENTRIES ARE EMPTY - DELETE STORED FILE !!!!!")
			xbmcvfs.delete(menuFavsFile)
		elif len(FOLDERS['items']) >= 1:
			debug_MS(f"(navigator.SELECTION[5]) ***** SUCCESSFULLY CREATED NEW USER-MENU-ENTRIES : {FOLDERS['items']} *****")
			with open(menuFavsFile, 'w') as choice:
				json.dump(FOLDERS, choice, indent=4, sort_keys=True)
		xbmc.sleep(1000)
		xbmc.executebuiltin('Container.Refresh')
	else:
		failing("(navigator.SELECTION) ##### Keine COMBI_SPORTS-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30521).format('PROVIDER'), translation(30522), icon, 12000)

def listSports(TARGET, CODE, SECTOR, PAGE, LIMIT, WANTED, SCENE, SERIE):
	debug_MS("(navigator.listSports) -------------------------------------------------- START = listSports --------------------------------------------------")
	debug_MS(f"(navigator.listSports) ### URL/SLUG = {TARGET} ### IDD = {CODE} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### maxPAGES = {WANTED} ### EXTRA = {SCENE} ### SERIE = {SERIE} ###")
	PAGE, MAXIMUM = int(PAGE), int(PAGE)+int(WANTED)
	COMBI_PAGES, COMBI_FIRST, COMBI_SECOND = ([] for _ in range(3))
	UNIKAT, config = set(), traversing.get_config()
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == '0' and HIGHER is True:
		addDir(translation(30721), f"{artpic}backmain.png", {'mode': 'callingMain'})
	for ii in range(PAGE, MAXIMUM, 1): # 1. Alle Sportarten / 2. Vereine und Events / 3. Suche Vereine und Events
		PAGE += 1
		SLINK = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.listSports[1]) SPORTS-PAGES XXX POS = {str(ii)} || URL = {SLINK} XXX")
		COMBI_PAGES.append([int(ii), SLINK])
	if COMBI_PAGES:
		COMBI_FIRST = getMultiData(COMBI_PAGES)
		if COMBI_FIRST:
			debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
			DATA_ONE = json.loads(COMBI_FIRST)
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and results.get('data', '') and len(results['data']) > 0:
					POS, DEM = results['Position'], results['Demand']
					for cats in results.get('data', []):
						debug_MS(f"(navigator.listSports[2]) xxxxx CATS-02 : {str(cats)} xxxxx")
						SPID = cats.get('id', None)
						if SPID is None or SPID in UNIKAT:
							continue
						UNIKAT.add(SPID)
						CAT = cleaning(cats['name'])
						SORTTITLE = repair_umlaut(CAT).lower()
						SLUG = cats['slug']
						branch = cleaning(cats['sport_type']['name']) if cats.get('sport_type', '') and cats['sport_type'].get('name', '') else 'sport'
						GENRE = SECTOR if branch == 'sport' and branch.lower() != SECTOR.lower() else branch.title()
						if SCENE == 'sports': GENRE = CAT
						imgID = (cats.get('image_url', None) or cats.get('image_id', None))
						PHOTO = IMG_categories.format(imgID) if imgID else icon
						DESC = (cleaning(cats.get('description', '')) or "")
						newDEM, newLIMIT, newWANTED, newSCENE = SLUG, 20, 3, 'tags'
						if SCENE in ['channels', 'teams']: # Direkt weiter zum Verein
							newDEM, newLIMIT, newWANTED, newSCENE = SLUG, 20, 3, 'profiles'
							DESC = translation(30722).format(CAT, DESC)
						NAME_ONE, NAME_TWO = (CAT for _ in range(2))
						COMBI_SECOND.append([POS, DEM, SPID, CAT, SORTTITLE, SLUG, newDEM, newLIMIT, newWANTED, newSCENE, NAME_ONE, NAME_TWO, PHOTO, DESC, GENRE])
	if COMBI_SECOND:
		debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
		for POS, DEM, SPID, CAT, SORTTITLE, SLUG, newDEM, newLIMIT, newWANTED, newSCENE, NAME_ONE, NAME_TWO, PHOTO, DESC, GENRE in sorted(COMBI_SECOND, key=lambda st: st[4]):
			addType = 2 # Alle Sportarten oder Vereine und Events
			if SCENE in ['channels', 'teams']: # Nur Vereine und Events
				addType = 1
				if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
					with open(channelFavsFile, 'r') as chp:
						watch = json.load(chp)
						for item in watch.get('items', []):
							if item.get('code') == SPID: addType = 2
			addDir(NAME_ONE, PHOTO, {'mode': 'listCategories', 'url': newDEM, 'code': SPID, 'section': GENRE, 'limit': newLIMIT, 'wanted': newWANTED, 'extras': newSCENE, 'name': CAT}, DESC, GENRE, False, HIGHER, addType)
			debug_MS(f"(navigator.listSports[3]) ### NAME : {NAME_ONE} || URL : {DEM} || TYPE : {newSCENE} || PHOTO : {PHOTO} ###")
		if results is not None and SCENE == 'teams' and results.get('meta', '') and str(results['meta'].get('total')).isdigit() and int(results['meta']['total']) > int(PAGE)*int(LIMIT): # 4 x 20 (PAGES=4 / LIMIT=20)
			debug_MS(f"(navigator.listSports[4]) NUMBERING ### totalRESULTS : {results['meta']['total']} || thisPAGE ends at : {str(int(PAGE-1)*int(LIMIT))} ###")
			debug_MS(f"(navigator.listSports[4]) NEXTPAGES ### Now show NextPage ... No.{PAGE} to No.{str(int(PAGE)+4)} ... ###")
			addDir(translation(30723), f"{artpic}nextpage.png", {'mode': 'listSports', 'url': TARGET, 'code': SPID, 'section': GENRE, 'page': PAGE, 'limit': 20, 'wanted': 3, 'extras': SCENE, 'name': SERIE})
	else:
		return dialog.notification(translation(30525).format('Einträge'), translation(30527).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listCategories(TARGET, CODE, SECTOR, PAGE, LIMIT, WANTED, SCENE, SERIE):
	debug_MS("(navigator.listCategories) -------------------------------------------------- START = listCategories --------------------------------------------------")
	debug_MS(f"(navigator.listCategories) ### URL/SLUG = {TARGET} ### IDD = {CODE} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### maxPAGES = {WANTED} ### EXTRA = {SCENE} ### SERIE = {SERIE} ###")
	PAGE, LIMIT, MAXIMUM = int(PAGE), int(LIMIT), int(PAGE)+int(WANTED)
	MEMBERS, COMBI_PAGES, COMBI_EVENTS, COMBI_LIVES, COMBI_ASSET, COMBI_TOPTYP, COMBI_LAST = ([] for _ in range(7))
	(number, FOUND), UNIKAT, config = (0 for _ in range(2)), set(), traversing.get_config()
	if SCENE == 'profiles': # Nur ein Verein
		LINKS = [config['TEAM_LIVENEXT'].format(TARGET), config['TEAM_ASSETS'].format(TARGET), config['TEAM_TOPS'].format(TARGET)]
	elif SCENE == 'tags': # Nur eine Sportart
		LINKS = [config['TAGS_LIVENEXT'].format(TARGET), config['TAGS_ASSETS'].format(TARGET), config['TAGS_TYPES'].format(CODE)]
	for ELEMENT in LINKS: # live: 4x50, asset: 4x20, tops: 2x20, types: 2x20
		BOOST = 50 if 'livestreams' in ELEMENT else 40 if 'assets' in ELEMENT else LIMIT
		HIGHEST = 3 if not 'livestreams' in ELEMENT else MAXIMUM
		for ii in range(PAGE, HIGHEST, 1):
			number += 1
			CLINK = f"{ELEMENT}page={str(ii)}&per_page={str(BOOST)}"
			debug_MS(f"(navigator.listCategories[1]) CATEGORIES-PAGES XXX POS = {number} || newLIMIT = {BOOST} || URL = {CLINK} XXX")
			COMBI_PAGES.append([int(number), CLINK])
	if COMBI_PAGES:
		COMBI_EVENTS = getMultiData(COMBI_PAGES)
		if COMBI_EVENTS:
			DATA_ONE = json.loads(COMBI_EVENTS)
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and results.get('data', '') and len(results['data']) > 0:
					POS, DEM = results['Position'], results['Demand']
					if 'livestreams' in DEM:
						POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT = get_Number(results, 'livestreams', POS, DEM)
						COMBI_LIVES.append([POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT])
					if '/assets' in DEM:
						POS_TWO, ORIG_TWO, ALL_ASS, COUNT_TWO, DUM_1, FREE_ASS, PAY_ASS, DUM_2, DUM_3, APID, ACAT = get_Number(results, '/assets', POS, DEM)
						COMBI_ASSET.append([POS_TWO, ORIG_TWO, ALL_ASS, COUNT_TWO, DUM_1, FREE_ASS, PAY_ASS, DUM_2, DUM_3, APID, ACAT])
					if '/top-assets' in DEM or 'sport-types' in DEM:
						TYPING = '/top-assets' if '/top-assets' in DEM else 'sport-types'
						POS_THREE, ORIG_THREE, ALL_TOP, COUNT_THREE, DUM_4, FREE_TOP, PAY_TOP, DUM_5, DUM_6, TPID, TCAT = get_Number(results, TYPING, POS, DEM)
						COMBI_TOPTYP.append([POS_THREE, ORIG_THREE, ALL_TOP, COUNT_THREE, DUM_4, FREE_TOP, PAY_TOP, DUM_5, DUM_6, TPID, TCAT])
	if COMBI_LIVES or COMBI_ASSET or COMBI_TOPTYP:
		SCORE_LIVE, SCORE_NEXT, SCORE_ASSE, SCORE_TOPS = (0 for _ in range(4))
		if COMBI_LIVES:
			LIVE_ALL, ONE_COUNT, LIVE_DEAD, LIVE_FREE, LIVE_PAY, NEXT_FREE, NEXT_PAY = COMBI_LIVES[0][2], charge(3, COMBI_LIVES), \
				charge(4, COMBI_LIVES), charge(5, COMBI_LIVES), charge(6, COMBI_LIVES), charge(7, COMBI_LIVES), charge(8, COMBI_LIVES)
			SCORE_LIVE  = (LIVE_ALL - sum([LIVE_DEAD, LIVE_PAY, NEXT_FREE, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else (LIVE_FREE - LIVE_DEAD)
			SCORE_NEXT = (LIVE_ALL - sum([LIVE_FREE, LIVE_PAY, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else NEXT_FREE
			if SCORE_LIVE >= 1: MEMBERS += ['livestream']
			elif SCORE_NEXT >= 1: MEMBERS += ['upcoming']
		if COMBI_ASSET:
			ASS_ALL, ASS_FREE, ASS_PAY = COMBI_ASSET[0][2], charge(5, COMBI_ASSET), charge(6, COMBI_ASSET)
			SCORE_ASSE = (ASS_ALL - ASS_PAY) if ASS_ALL > sum([ASS_FREE, ASS_PAY]) else ASS_FREE
			if SCORE_ASSE >= 1: MEMBERS += ['latest']
		if COMBI_TOPTYP and SCENE == 'profiles':
			TOP_ALL, TOP_FREE, TOP_PAY = COMBI_TOPTYP[0][2], charge(5, COMBI_TOPTYP), charge(6, COMBI_TOPTYP)
			SCORE_TOPS = (TOP_ALL - TOP_PAY) if TOP_ALL > sum([TOP_FREE, TOP_PAY]) else TOP_FREE
			if SCORE_TOPS >= 1: MEMBERS+= ['highlights']
		if COMBI_TOPTYP and SCENE == 'tags' and COMBI_TOPTYP[0][2] >= 1: MEMBERS+= ['sporttypes']
		for (im_uno, im_due, im_tre) in zip_longest(COMBI_LIVES, COMBI_ASSET, COMBI_TOPTYP, fillvalue=['LIST_MISSING']):
			if (len(im_uno) > 3 and 'page=1' in im_uno[1]) or (len(im_due) > 3 and 'page=1' in im_due[1]) or (len(im_tre) > 3 and 'page=1' in im_tre[1]):
				debug_MS("+++++++++++++++++++++++++++++++++++++++++++++") # Liste1 = im_uno[0]:im_uno[9] || Liste2 = im_due[0]:im_due[9] || Liste3 = im_tre[0]:im_tre[9]
				debug_MS(f"(navigator.listCategories[2]) ### Anzahl = {len(im_uno+im_due+im_tre)} || Eintrag : {str(im_uno+im_due+im_tre)} || Members : {MEMBERS} ###")
				'''
				Liste-1.1 = POS_ONE, ORIG_ONE, LIVE_ALL, COUNT_ONE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT = im_uno[0], im_uno[1], im_uno[2], im_uno[3], im_uno[4], im_uno[5], im_uno[6], im_uno[7], im_uno[8], im_uno[9]
				Liste-2.1 = POS_TWO, ORIG_TWO, ASS_ALL, COUNT_TWO, FREE_ASS, PAY_ASS, DUM_1, DUM_2, APID, ACAT = im_due[0], im_due[1], im_due[2], im_due[3], im_due[4], im_due[5], im_due[6], im_due[7], im_due[8], im_due[9]
				Liste-3.1 = POS_THREE, ORIG_THREE, TOP_ALL, COUNT_THREE, FREE_TOP, PAY_TOP, DUM_3, DUM_4, TPID, TCAT = im_tre[0], im_tre[1], im_tre[2], im_tre[3], im_tre[4], im_tre[5], im_tre[6], im_tre[7], im_tre[8], im_tre[9]
				Liste-3.2 = POS_THREE, ORIG_THREE, TYP_ALL, COUNT_THREE, DUM_5, DUM_6, DUM_7, DUM_8, SPID, SCAT = im_tre[0], im_tre[1], im_tre[2], im_tre[3], im_tre[4], im_tre[5], im_tre[6], im_tre[7], im_tre[8], im_tre[9]
				'''
				for RECORD in MEMBERS:
					CAT = SERIE if SERIE != "" else im_uno[9] if RECORD in ['livestream', 'upcoming'] else im_due[9] if RECORD == 'latest' else im_tre[9]
					TOTAL = im_uno[2] if RECORD in ['livestream', 'upcoming'] else im_due[2] if RECORD == 'latest' else im_tre[2]
					TITLE = next((pt.get('title') for pt in config['picks'] if pt.get('member') == RECORD), 'UNKNOWN')
					SUFFIX = SCORE_LIVE if RECORD == 'livestream' else SCORE_NEXT if RECORD == 'upcoming' else \
						SCORE_ASSE if RECORD == 'latest' else SCORE_TOPS if RECORD == 'highlights' else im_tre[2] if RECORD == 'sporttypes' else None
					if SUFFIX is None: continue
					PREFIX = '> ' if (RECORD == 'latest' and im_due[2] > SCORE_ASSE and SCORE_ASSE > 79) or (RECORD == 'highlights' and im_tre[2] > SCORE_TOPS and SCORE_TOPS > 79) else ""
					NAME_ONE, NAME_TWO = (translation(30731).format(TITLE+CAT, PREFIX, str(SUFFIX)) for _ in range(2))
					IMG = next((f"{artpic}{pm.get('member')}.png" for pm in config['picks'] if pm.get('member') == RECORD and xbmcvfs.exists(f"{artpic}{pm.get('member')}.png")), icon)
					if RECORD == 'livestream' and SCORE_LIVE >= 1:
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_uno[1].split('?')[0]}?", 50, 2, 'playlive', im_uno[8], im_uno[9]
						NAME_ONE = translation(30732).format(NAME_ONE)
						PLOT = translation(30733).format(str(SUFFIX))
					elif RECORD == 'upcoming' and SCORE_NEXT >= 1:
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_uno[1].split('?')[0]}?", 50, 2, 'playnext', im_uno[8], im_uno[9]
						NAME_ONE = translation(30734).format(NAME_ONE)
						PLOT = translation(30735).format(CAT, PREFIX, str(SUFFIX))
					elif RECORD in ['latest', 'highlights'] and (SCORE_ASSE >= 1 or SCORE_TOPS >= 1):
						FOUND += 1
						(NEW_URL, newPID, newCAT) = (im_due[1], im_due[8], im_due[9]) if RECORD == 'latest' else (im_tre[1], im_tre[8], im_tre[9])
						newDEM, newLIMIT, newWANTED, newSCENE = f"{NEW_URL.split('?')[0]}?", 40, 2, 'tags'
						PLOT = translation(30736).format(TITLE, CAT, PREFIX, str(SUFFIX))
					elif RECORD == 'sporttypes':
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_tre[1].split('?')[0]}?", 20, 3, 'teams', im_tre[8], im_tre[9]
						PLOT = translation(30737).format(CAT, PREFIX, str(SUFFIX))
					debug_MS(f"(navigator.listCategories[3]) NUMBERING ### CATEGORY : {TITLE+CAT} ### TOTAL : {TOTAL} ### FORFREE : {SUFFIX} ###")
					COMBI_LAST.append([SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT])
	if COMBI_LAST and FOUND == 1:
		debug_MS("(navigator.listCategories[4]) ----- Only one Entry FOUND - goto = listVideos -----")
		for SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT in COMBI_LAST:
			addDir(translation(30738).format(NAME_TWO), IMG, {'mode': 'blankFUNC', 'url': '00'}, genre=SECTOR, folder=False)
			if 'livestreams' in newDEM or 'assets' in newDEM:
				return listVideos(newDEM, SECTOR, page, newLIMIT, position, excluded, newWANTED, newSCENE)
			else:
				return listSports(newDEM, newPID, SECTOR, page, newLIMIT, newWANTED, newSCENE, newCAT)
	elif COMBI_LAST and FOUND >= 2:
		debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
		for SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT in COMBI_LAST:
			if 'livestreams' in newDEM: # Alle Ordner mit LiveNext-Videos
				addDir(NAME_ONE, IMG, {'mode': 'listVideos', 'url': newDEM, 'code': newPID, 'section':  SECTOR, 'limit': newLIMIT, 'wanted': newWANTED, 'extras': newSCENE}, PLOT, SECTOR, background=False)
			if 'assets' in newDEM: # Alle Ordner mit VOD-Videos
				addDir(NAME_ONE, IMG, {'mode': 'listVideos', 'url': newDEM, 'code': newPID, 'section':  SECTOR, 'limit': newLIMIT, 'wanted': newWANTED, 'extras': newSCENE}, PLOT, SECTOR, background=False)
			if 'sport-types' in newDEM: # Alle Sportarten oder Vereine und Events
				addDir(NAME_ONE, IMG, {'mode': 'listSports', 'url': newDEM, 'code': newPID, 'section':  SECTOR, 'limit': newLIMIT, 'wanted': newWANTED, 'extras': newSCENE, 'name': newCAT}, PLOT, SECTOR, background=False)
			debug_MS(f"(navigator.listCategories[4]) ### NAME : {NAME_ONE} || URL : {newDEM} || TYPE : {newSCENE} || PHOTO : {IMG} ###")
	else:
		return dialog.notification(translation(30525).format('Einträge'), translation(30527).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSDTV(CAT):
	debug_MS("(navigator.SearchSDTV) ------------------------------------------------ START = SearchSDTV -----------------------------------------------")
	config = traversing.get_config()
	keyword = None
	if xbmcvfs.exists(SEARCHFILE):
		with open(SEARCHFILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30751).format(CAT), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote(keyword)
			with open(SEARCHFILE, 'w') as record:
				record.write(keyword)
	if keyword:
		if CAT == 'PROFILEN': return listSports(config['SEARCH_PROFILE'].format(keyword), code, section, page, 40, 10, 'teams', 'Profilsuche')
		elif CAT == 'VIDEOS': return listVideos(config['SEARCH_VIDEO'].format(keyword), section, page, 40, position, excluded, 5, 'playnext')
	return None

def listVideos(TARGET, SECTOR, PAGE, LIMIT, POS, FILTER, WANTED, SCENE):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug_MS(f"(navigator.listVideos) ### URL = {TARGET} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### POSITION = {POS} ### EXCLUDED = {FILTER} ### maxPAGES = {WANTED} ### showLIVE = {SCENE} ###")
	counterTWO, excludedTWO, PAGE, MAXIMUM = int(POS), int(FILTER), int(PAGE), int(PAGE)+int(WANTED)
	counterONE, excludedONE, number = (0 for _ in range(3))
	SEND, UNIKAT, config = {}, set(), traversing.get_config()
	COMBI_PAGES, COMBI_FIRST, COMBI_SECOND, COMBI_LINKS, COMBI_THIRD, COMBI_FOURTH, SEND['videos'] = ([] for _ in range(7))
	UPCOMING = True if 'livestreams' in TARGET else False
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == '0' and HIGHER is True:
		addDir(translation(30761), f"{artpic}backmain.png", {'mode': 'callingMain'})
	for ii in range(PAGE, MAXIMUM, 1):
		PAGE += 1
		VLINK = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.listVideos[1]) VIDEOS-PAGES XXX POS = {str(ii)} || URL = {VLINK} XXX")
		COMBI_PAGES.append([int(ii), VLINK])
	if COMBI_PAGES:
		COMBI_FIRST = getMultiData(COMBI_PAGES)
		if COMBI_FIRST:
			DATA_ONE = json.loads(COMBI_FIRST)
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listVideos[2]) XXXXX CONTENT-02 : {str(DATA_ONE)} XXXXX")
			#log("++++++++++++++++++++++++")
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and ((results.get('data', '') and len(results['data']) > 0) or (results.get('assets', '') and len(results['assets']) > 0)):
					POS, PATH_ONE = results['Position'], results['Demand']
					items = results['data'] if results.get('data', '') and len(results['data']) > 0 else results['assets']
					for item in items:
						startCOMPLETE, startDATE, startTIME, SORTDAY, AIRED, BEGINS, endDATE, tags, SLUG_ONE, TEA_ONE, NOTIZ = (None for _ in range(11))
						(GENRE, PREFIX, DESC_ONE), (NEXTCOME, RUNNING, LIVING), branch, shorties = ("" for _ in range(3)), (False for _ in range(3)), 'sport', []
						#log(f"(navigator.listVideos[2]) xxxxx ITEM-02 : {str(item)} xxxxx")
						counterONE, counterTWO = counterONE.__add__(1), counterTWO.__add__(1)
						UID_ONE = item.get('id', None)
						if UID_ONE is None or UID_ONE in UNIKAT:
							excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
							continue
						UNIKAT.add(UID_ONE)
						TITLE = cleaning(item['name'])
						if str(item.get('content_start_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdigit():
							LOCALstart = get_CentralTime(item['content_start_date']) # 2024-05-10T17:15:18.000000Z
							startCOMPLETE = LOCALstart.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format( '.', '•', ':')
							for tt in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
								startCOMPLETE = startCOMPLETE.replace(*tt)
							startDATE = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
							startTIME = LOCALstart.strftime('%H{0}%M').format(':')
							if datetime.now() < LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = True, False # 19:44 < 20:00-15m = 19:45
							if datetime.now() > LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = False, True # 19:46 > 20:00-15m = 19:45
							if datetime.now() > LOCALstart + timedelta(hours=12): NEXTCOME, RUNNING = False, False # 22:00 > 09:45+12h = 21:45
							SORTDAY = LOCALstart.strftime('%Y{0}%m{0}%dT%H{1}%M').format('.', ':')
							AIRED = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
							BEGINS = LOCALstart.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
							if KODI_ov20:
								BEGINS = LOCALstart.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
						if str(item.get('content_end_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdigit():
							LOCALend = get_CentralTime(item['content_end_date']) # 2024-05-10T20:00:18.000000Z
							endDATE = LOCALend.strftime('%d{0}%m{0}%YT%H{1}%M').format('.', ':')
							if datetime.now() > LOCALend + timedelta(minutes=15): # 22:30 > 22:00+15m = 22:15
								NEXTCOME, RUNNING = False, False
						else:
							if item.get('currently_live', '') is False and RUNNING is True:
								RUNNING = False
						imgID = (item.get('image_url', None) or item.get('image_id', None))
						PHOTO = IMG_assets.format(imgID) if imgID else icon
						if 'search/assets' in TARGET and (RUNNING is True or NEXTCOME is True):
							excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
							continue # In der Suchfunktion die live+kommenden Spiele herausfiltern
						if str(item.get('price_in_cents')).isdigit() or len([euro for euro in item.get('monetizations', '')]) > 0:
							excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
							continue
						if (item.get('currently_live', '') is True and SCENE in ['playnext', 'tags']) or (item.get('currently_live', '') is False and SCENE == 'playlive'):
							excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
							continue
						NAME = f"{startDATE} - {TITLE}" if startDATE else TITLE
						if item.get('currently_live', '') is True and RUNNING is True and startTIME:
							NAME, LIVING = translation(30762).format(startTIME, TITLE), True
						if item.get('display_tags', '') and len(item['display_tags']) > 0:
							shorties = [og.get('name', '') for og in item.get('display_tags', [])]
							if shorties: tags = '[CR]'.join(sorted(shorties[:3]))
						TEA_ONE = (item.get('description', None) or item.get('teaser', None))
						if TEA_ONE: DESC_ONE = cleaning(TEA_ONE, True).replace('\n', '[CR]')
						if item.get('profile', ''):
							SHORT = item['profile']
							if TEA_ONE is None and SHORT.get('description', ''):
								DESC_ONE = cleaning(SHORT['description'], True).replace('\n', '[CR]')
							SLUG_ONE = SHORT.get('slug', None)
							branch = cleaning(SHORT['sport_type']['name']) if SHORT.get('sport_type', '') and SHORT['sport_type'].get('name', '') else 'sport'
						GENRE = SECTOR if branch == 'sport' and branch.lower() != SECTOR.lower() else branch.title()
						SLUG_TWO = item.get('slug', None)
						if (RUNNING is True or NEXTCOME is True) and startCOMPLETE and tags: # Datum, Uhrzeit und Tags
							NOTIZ = translation(30763).format(TITLE, cleaning(tags), startCOMPLETE)
						if NOTIZ is None and (RUNNING is True or NEXTCOME is True) and startCOMPLETE and tags is None: # Datum, Uhrzeit KEINE Tags
							NOTIZ = translation(30764).format(TITLE, startCOMPLETE)
						if NOTIZ is None and startDATE and tags: # Einfaches Datum und Tags
							NOTIZ = translation(30765).format(TITLE, cleaning(tags), startDATE)
						if NOTIZ is None and startDATE and tags is None: # Einfaches Datum KEINE Tags
							NOTIZ = translation(30766).format(TITLE, startDATE)
						if NOTIZ: PREFIX = NOTIZ
						number += 1
						COMBI_SECOND.append([int(number), UID_ONE, TITLE, NAME, PHOTO, SORTDAY, BEGINS, AIRED, GENRE, PREFIX, DESC_ONE, LIVING])
						if SLUG_ONE and SLUG_TWO:
							COMBI_LINKS.append([int(number), config['VIDEO_LINK'].format(SLUG_ONE, SLUG_TWO)])
	if COMBI_SECOND:
		COMBI_THIRD = getMultiData(COMBI_LINKS)
		if COMBI_THIRD:
			DATA_TWO = json.loads(COMBI_THIRD)
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listVideos[3]) XXXXX CONTENT-03 : {str(DATA_TWO)} XXXXX")
			#log("++++++++++++++++++++++++")
			for elem in DATA_TWO:
				if elem is not None and ((elem.get('videos', '') and len(elem['videos']) > 0) or (elem.get('livestream', '') and elem['livestream'].get('src', ''))):
					METER, PATH_TWO = elem['Position'], elem['Demand']
					(VID_TWO, TYP_TWO), DUR_TWO, DESC_TWO = (None for _ in range(2)), 0, ""
					#log(f"(navigator.listVideos[3]) xxxxx ELEM-03 : {str(elem)} xxxxx")
					UID_TWO = (elem.get('uuid', '') or elem.get('id', ''))
					if elem.get('videos', '') and len(elem['videos']) > 0:
						VID_TWO = elem.get('videos', {})[0].get('src', None)
						TYP_TWO = elem.get('videos', {})[0].get('type', None)
						DUR_TWO = int(elem['videos'][0]['duration']) if str(elem.get('videos', {})[0].get('duration')).isdigit() else 0
					elif elem.get('livestream', '') and elem['livestream'].get('src', ''):
						VID_TWO = elem['livestream'].get('src', None)
						TYP_TWO = elem['livestream'].get('type', None)
					TEA_TWO = (elem.get('description', None) or elem.get('teaser', None))
					if TEA_TWO: DESC_TWO = cleaning(TEA_TWO, True).replace('\n', '[CR]')
					elif TEA_TWO is None and elem.get('home_team', '') and elem['home_team'].get('name', '') and elem.get('guest_team', '') and elem['guest_team'].get('name', ''):
						DESC_TWO = f"{cleaning(elem['home_team']['name'])} vs. {cleaning(elem['guest_team']['name'])}"
					COMBI_FOURTH.append([int(METER), UID_TWO, PATH_TWO, VID_TWO, TYP_TWO, DUR_TWO, DESC_TWO])
				else:
					excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
	if (SCENE == 'playnext' and COMBI_SECOND) or (SCENE != 'playnext' and COMBI_SECOND and COMBI_FOURTH): # Zähler NULL ist immer die Nummerierungder Listen 1+2
		COMPLETE = [a + b for a in COMBI_SECOND for b in COMBI_FOURTH if a[1] == b[1]] # Zusammenführung von Liste1 und Liste2 - wenn die ID überein stimmt !!!
		if SCENE == 'playnext': # Nur 'upcoming' Folder ohne Videos anzeigen !!!
			COMPLETE += [c for c in COMBI_SECOND if all(d[1] != c[1] for d in COMBI_FOURTH)] # Der übriggebliebene Rest von Liste1 - wenn die ID nicht in der Liste2 vorkommt !!!
		#log("++++++++++++++++++++++++")
		#log(f"(navigator.listVideos[4]) no.04 XXXXX COMPLETE-04 : {str(COMPLETE)} XXXXX")
		debug_MS("---------------------------------------------")
		COMPLETE = sorted(COMPLETE, key=lambda sd: sd[5], reverse=True) if 'search/assets' in TARGET else sorted(COMPLETE, key=lambda cr: int(cr[0]))
		for da in COMPLETE: # 0-11 = Liste1 || 12-18 = Liste2
			debug_MS(f"(navigator.listVideos[4]) ### Anzahl = {str(len(da))} || Eintrag : {str(da)} ###")
			'''
				Full-Liste-1 = Number1, Mark1, title, name, image, sorting, begins, aired, genre, prefix, Desc1, LIVESTREAM = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11]
				Full-Liste-2 = Number2, Mark2, CODING, MUXING, duration, Desc2 = da[11], da[12], da[13], da[14], da[15], da[16]
			'''
			if len(da) >= 19: ### Liste1+Liste2 ist gleich Nummer:19 ###
				Number1, Mark1, title, name, image, sorting, begins, aired, genre, prefix, Desc1, LIVESTREAM = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11]
				Number2, Mark2, TESTING, CODING, MUXING, duration, Desc2 = da[12], da[13], da[14], da[15], da[16], da[17], da[18]
				FULL_DESC = Desc2 if len(Desc2) > 70 else Desc1
			else:
				Number1, Mark1, title, name, image, sorting, begins, aired, genre, prefix, FULL_DESC, LIVESTREAM = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11]
				(TESTING, CODING, MUXING), duration, Desc2 = (None for _ in range(3)), 0, ""
			uvz, entries = build_mass({'mode': 'playCODE', 'IDENTiTY': Mark1}), []
			plot = prefix+FULL_DESC
			debug_MS(f"(navigator.listVideos[5]) ##### POS : {str(da[0])} || NAME : {name} || mediaID : {Mark1} || GENRE : {genre} #####")
			debug_MS(f"(navigator.listVideos[5]) ##### THUMB : {image} || VIDEO : {str(CODING)} || TYPE : {str(MUXING)} || DURATION : {str(duration)} #####")
			debug_MS("---------------------------------------------")
			LEM = xbmcgui.ListItem(name)
			if plot in ['', 'None', None]: plot = "..."
			if KODI_ov20:
				vinfo = LEM.getVideoInfoTag()
				vinfo.setTitle(name)
				vinfo.setPlot(plot)
				if str(duration).isdigit(): vinfo.setDuration(int(duration))
				if begins: LEM.setDateTime(begins)
				if aired: vinfo.setFirstAired(aired)
				if aired and str(aired[6:10]).isdigit(): vinfo.setYear(int(aired[6:10]))
				if genre and len(genre) > 3: vinfo.setGenres([genre])
				vinfo.setStudios(['Sportdeutschland.tv'])
				vinfo.setMediaType('movie')
			else:
				vinfo = {}
				vinfo['Title'] = name
				vinfo['Plot'] = plot
				if str(duration).isdigit(): vinfo['Duration'] = duration
				if begins: vinfo['Date'] = begins
				if aired: vinfo['Aired'] = aired
				if aired and str(aired[6:10]).isdigit(): vinfo['Year'] = aired[6:10]
				if genre and len(genre) > 3: vinfo['Genre'] = genre
				vinfo['Studio'] = 'Sportdeutschland.tv'
				vinfo['Mediatype'] = 'movie'
				LEM.setInfo('Video', vinfo)
			LEM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
			if image and image != icon and not artpic in image:
				LEM.setArt({'fanart': image})
			LEM.setProperty('IsPlayable', 'true')
			LEM.setContentLookup(False)
			if enableBACK and PLACEMENT == '1' and HIGHER is True:
				entries.append([translation(30650), 'RunPlugin({})'.format(build_mass({'mode': 'callingMain'}))])
			if UPCOMING is False:
				entries.append([translation(30654), 'Action(Queue)'])
			LEM.addContextMenuItems(entries)
			SEND['videos'].append({'filter': Mark1, 'name': name, 'photo': image, 'plot': plot, 'genre': genre, 'testing': TESTING, 'coding': CODING, 'muxing': MUXING, 'live': LIVESTREAM})
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LEM)
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		debug_MS(f"(navigator.listVideos[6]) NUMBERING ### current_RESULT : {counterONE} // all_RESULT : {counterTWO} ### current_EXCLUDED : {excludedONE} // all_EXCLUDED : {excludedTWO} ###")
		if results is not None and not (SCENE == 'playlive' and 'livestreams' in TARGET) and results.get('meta', '') and str(results['meta'].get('total')).isdigit():
			debug_MS(f"(navigator.listVideos[6]) NUMBERING ### totalRESULTS : {results['meta']['total']} // thisPAGE ends at : {str(int(PAGE-1)*int(LIMIT))} ###")
			if int(results['meta']['total']) > int(counterTWO):
				debug_MS(f"(navigator.listVideos[6]) NEXTPAGES ### Now show NextPage ... No.{PAGE} ... ###")
				addDir(translation(30767), f"{artpic}nextpage.png", {'mode': 'listVideos', 'url': TARGET, 'section': genre, 'page': PAGE, 'limit': LIMIT, 'position': counterTWO, 'excluded': excludedTWO, 'wanted': WANTED, 'extras': SCENE})
	else:
		debug_MS("(navigator.listEpisodes[2]) ##### Keine COMBI_VIDEO-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30525).format('Einträge'), translation(30526), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### SOURCE = {IDD} ###")
	Status, config = 'OFFLINE', traversing.get_config()
	INSPECT, VIDEO, TYPE, FINAL_ONE, FINAL_WORKS, STREAM_WORKS, TEST_WORKS = (False for _ in range(7))
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] != '00' and elem['filter'] == IDD:
				CLEAR_TITLE, PHOTO, PLOT, GENRE, INSPECT, VIDEO, TYPE, NOW_LIVE = re.sub('(\[B\]|\[/B\])', '', elem['name']), elem['photo'], elem['plot'], elem['genre'], elem['testing'], elem['coding'], elem['muxing'], elem['live']
				debug_MS(f"(navigator.playCODE[1]) ### WORKFILE-Line : {str(elem)} ###")
	if INSPECT and VIDEO and TYPE:
		FIRST = getUrl(INSPECT)
		if FIRST is not None and ((FIRST.get('livestream', '') and FIRST['livestream'].get('src', '') and FIRST.get('currently_live', '') is True) or (FIRST.get('videos', '') and len(FIRST['videos']) > 0 and FIRST.get('currently_live', '') is False)):
			Status = 'ONLINE'
		if Status == 'ONLINE' and 'vidibus.net/live' in VIDEO:
			STREAM_ONE, FINAL_ONE = 'M3U8', VIDEO.replace('.smil', '.m3u8', 1)
		elif Status == 'ONLINE' and not 'vidibus.net/live' in VIDEO:
			### 1. extract = "profile.slug": "tv-05-07-huettenberg", "slug": "2hbl-tv-05-07-huettenberg-vs-hsc-2000-coburg"
			### 2. getUrl = https://api.sportdeutschland.tv/api/stateless/frontend/assets/tv-05-07-huettenberg/2hbl-tv-05-07-huettenberg-vs-hsc-2000-coburg
			### 3.1. extract = videos[0]src: "https://chess.dosbnewmedia.de//mediafiles/e4dd01b062fc49018225e251a577726d.smil", videos[0]type: "smil"
			### 3.2. extract = videos[0]src: "EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA", videos[0]type: "mux_vod"
			###     oder extract = "livestream.src": null
			### 4.1. getUrl = https://api.sportdeutschland.tv/api/frontend/asset-token/958f1bc4-0bbc-4a32-b5fa-ca5f380d7d81?type=legacy
			### 4.2. getUrl = https://api.sportdeutschland.tv/api/frontend/asset-token/95fd4975-646b-48d6-b422-ebe5ce9ebc11?type=mux_vod&playback_id=EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA
			### 5. extract = token if token else ""
			### 6.1. Video = https://chess.dosbnewmedia.de//mediafiles/e4dd01b062fc49018225e251a577726d.smil?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFRUVnQ3BhdnluTVlxTFN3V0ZQR0hTaERuRXU2OFRmcTZUeW1Wem1SaU9BIiwiYXVkIjoidiIsImV4cCI6MTY1MDYzMjg1NCwia2lkIjoiOXMxUG5YcGpwYlNQdldHMDJWWmoxakhNUHY5SHFqVEdJeGxlRGNiZzAwNDAyOCJ9.NAeFSuurX8aHN14Ej4jjPS0bXOu5tiV1PNR7R3Neamuaj8Gb5w8-C5K5DxOoh2om2A4UwNybAMBmXyilzdd_MY3gL1F-BBrZ15o4UiYNlQljlnjiSgzaW9VXHfmE97caNoc9PyQUiPGOVWmBEvv39fJERQaW4tIoqSzMlZX6YKJLspBkw4f9oDNZVyka8W9UeOTnHqv0vfTfNy7Y9jVemglkT4rZhm9QscOcF_dGDNpLRRsAHXci1T0g1e1uJ7wE8WduFdX1EUS7BC210GN94lojyzYjQh3QscO98GvYbm5pekZVWcJWE11kmolA3Ug-Wj9ZPz0H8Lny-2EPuV5DXQ
			### 6.2. Video = https://stream.mux.com/EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA.m3u8?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFRUVnQ3BhdnluTVlxTFN3V0ZQR0hTaERuRXU2OFRmcTZUeW1Wem1SaU9BIiwiYXVkIjoidiIsImV4cCI6MTY1MDYzMjg1NCwia2lkIjoiOXMxUG5YcGpwYlNQdldHMDJWWmoxakhNUHY5SHFqVEdJeGxlRGNiZzAwNDAyOCJ9.NAeFSuurX8aHN14Ej4jjPS0bXOu5tiV1PNR7R3Neamuaj8Gb5w8-C5K5DxOoh2om2A4UwNybAMBmXyilzdd_MY3gL1F-BBrZ15o4UiYNlQljlnjiSgzaW9VXHfmE97caNoc9PyQUiPGOVWmBEvv39fJERQaW4tIoqSzMlZX6YKJLspBkw4f9oDNZVyka8W9UeOTnHqv0vfTfNy7Y9jVemglkT4rZhm9QscOcF_dGDNpLRRsAHXci1T0g1e1uJ7wE8WduFdX1EUS7BC210GN94lojyzYjQh3QscO98GvYbm5pekZVWcJWE11kmolA3Ug-Wj9ZPz0H8Lny-2EPuV5DXQ
			TOKEN_URL = config['PLAY_MUX'].format(IDD, TYPE, VIDEO) if TYPE.startswith('mux') else config['PLAY_LEGACY'].format(IDD) if not TYPE.startswith('mux') else None
			if TOKEN_URL:
				SECOND = getUrl(TOKEN_URL, 'LOAD')
				STATIC_TOKEN = re.compile(r'''\{["']token["']:["'](eyJ[^"']+)["']\}''', re.S).findall(SECOND)
				START_LINK = VIDEO.replace('.mp4', '.smil', 1) if VIDEO.endswith('.mp4') else config['PLAY_M3U8'].format(VIDEO) if VIDEO[:4] != 'http' else VIDEO
				END_LINK = f"?token={STATIC_TOKEN[0]}" if STATIC_TOKEN else ""
				debug_MS(f"(navigator.playCODE[2]) === STATUS : {Status} === START_LINK+END_LINK : {str(START_LINK+END_LINK)} ===")
				if START_LINK.startswith('https://stream.mux.com/'):
					STREAM_ONE, FINAL_ONE = 'HLS', START_LINK+END_LINK
				else:
					THIRD = getUrl(START_LINK+END_LINK, 'LOAD')
					debug_MS(f"(navigator.playCODE[3]) === STATUS : {Status} === CONTENT-03 : {str(THIRD)} ===")
					SOURCE = re.compile(r'''<video src=["']([^"']+)["'] type=''', re.S).findall(THIRD)
					MIME = re.compile(r'''["'] type=["']([^"']+)["']''', re.S).findall(THIRD)
					STREAM_ONE = 'MP4' if MIME and MIME[0] == 'video/mp4' else 'HLS' if MIME and MIME[0].startswith('application') else 'M3U8'
					FINAL_ONE = SOURCE[0] if SOURCE else False
	if FINAL_ONE:
		attempts = 1
		while not TEST_WORKS and attempts < 3: # 2 x Pingversuche für den STREAM-Request ::: zur Überprüfung der Verfügbarkeit des Streams
			attempts += 1
			try:
				heading = {'Cache-Control': 'no-cache', 'Accept': '*/*', 'documentLifecycle': 'active', 'User-Agent': defaultAgent, 'DNT': '1', 'Accept-Encoding': 'gzip', 'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'}
				heading.update(config['header'])
				queries = Request(FINAL_ONE, None, heading)
				scanning = urlopen(queries, timeout=8)
				debug_MS(f"(navigator.playCODE[4]) === CALL_{STREAM_ONE}_STREAM === RETRIES_no : {str(attempts-1)} === STATUS : {str(scanning.getcode())} || URL : {FINAL_ONE} ===")
			except (URLError, HTTPError) as e:
				failing(f"(navigator.playCODE[4]) ERROR - {STREAM_ONE}_STREAM - ERROR ##### RETRIES_no : {str(attempts-1)} === URL : {FINAL_ONE} === FAILURE : {str(e)} #####")
				time.sleep(2)
			else:
				FINAL_WORKS, STREAM_WORKS, TEST_WORKS = FINAL_ONE, STREAM_ONE, True
				break
		if TEST_WORKS is False:
			failing(f"(navigator.playCODE[5]) ##### Abspielen des Streams NICHT möglich #####\n ##### QUERY : {API_PLAYER}{IDD} || VIDEO : {str(VIDEO)} #####\n ########## Die vorhandenen Stream-Einträge auf der Webseite von *sportdeutschland.tv* sind OFFLINE/DEFEKT !!! ##########")
			return dialog.notification(translation(30521).format('URL-2'), translation(30528), icon, 8000)
	else:
		failing(f"(navigator.playCODE[4]) ##### Abspielen des Streams NICHT möglich #####\n ##### QUERY : {API_PLAYER}{IDD} || VIDEO : {str(VIDEO)} #####\n ########## KEINEN Stream-Eintrag auf der Webseite von *sportdeutschland.tv* gefunden !!! ##########")
		return dialog.notification(translation(30521).format('URL-1'), translation(30529), icon, 8000)
	if FINAL_WORKS and TEST_WORKS:
		LPM = xbmcgui.ListItem(CLEAR_TITLE, path=FINAL_WORKS)
		if PLOT in ['', 'None', None]: PLOT = "..."
		if KODI_ov20:
			vinfo = LPM.getVideoInfoTag()
			vinfo.setTitle(CLEAR_TITLE), vinfo.setPlot(PLOT), vinfo.setGenres([GENRE]), vinfo.setStudios(['Sportdeutschland.TV'])
		else:
			LPM.setInfo('Video', {'Title': CLEAR_TITLE, 'Plot': PLOT, 'Genre': GENRE, 'Studio': 'Sportdeutschland.TV'})
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
			LPM.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
		log(f"(navigator.playCODE) {STREAM_WORKS}_stream : {FINAL_WORKS}")

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
		with open(channelFavsFile, 'r') as fp: # Favoriten für Profile/Vereine
			snippets = json.load(fp)
			for item in snippets.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				debug_MS(f"(navigator.listFavorites[1]) ### NAME : {name} || URL : {item.get('url')} || IMAGE : {logo} ###")
				addDir(name, logo, {'mode': 'listCategories', 'url': item.get('url'), 'code': item.get('code'), 'section': item.get('section'), 'limit': item.get('limit'), 'wanted': item.get('wanted'), 'extras': item.get('extras'), \
					'name': name}, cleaning(item.get('plot')), cleaning(item.get('section')), background=False, FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile) and os.stat(channelFavsFile).st_size > 0:
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'code': code, 'limit': limit, 'wanted': wanted, 'extras': extras, 'plot': plot, 'section': section})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30530), translation(30531).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('code') != code]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30530), translation(30532).format(name), icon, 8000)

def addDir(name, image, params={}, plot=None, genre='Sport', background=True, higher=False, addType=0, FAVclear=False, folder=True):
	uws, entries = build_mass(params), []
	LDM = xbmcgui.ListItem(name, offscreen=True)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = LDM.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setGenres([genre]), vinfo.setStudios(['Sportdeutschland.tv'])
	else:
		LDM.setInfo('Video', {'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': 'Sportdeutschland.tv'})
	LDM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image != icon and not artpic in image and background is True:
		LDM.setArt({'fanart': image})
	LDM.setProperty('IsPlayable', 'false')
	if enableBACK and PLACEMENT == '1' and higher is True:
		entries.append([translation(30650), 'RunPlugin({})'.format(build_mass({'mode': 'callingMain'}))])
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'ADD', 'name': name, 'pict': 'None' if image == icon else image, 'url': params.get('url'), \
			'code': params.get('code'), 'limit': params.get('limit'), 'wanted': params.get('wanted'), 'extras': params.get('extras'), 'name': params.get('name'), 'plot': plot.replace('\n', '[CR]'), 'section': params.get('section')}))])
	if addType == 0 and FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), \
			'code': params.get('code'), 'limit': params.get('limit'), 'wanted': params.get('wanted'), 'extras': params.get('extras'), 'name': params.get('name'), 'plot': plot, 'genre': genre}))])
	LDM.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uws, listitem=LDM, isFolder=folder)
