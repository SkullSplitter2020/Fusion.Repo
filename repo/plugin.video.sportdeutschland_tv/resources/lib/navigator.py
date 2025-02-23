# -*- coding: utf-8 -*-

from .common import *
config = traversing.get_config()


def create_account(success=False):
	debug_MS("(navigator.create_account) ############### START ACCOUNT - REGISTRATION ###############")
	email_adress = dialog.input(translation(30541), type=xbmcgui.INPUT_ALPHANUM)
	hidden_sign = dialog.input(translation(30542), type=xbmcgui.INPUT_ALPHANUM)
	if email_adress is not None and len(email_adress) > 0 and hidden_sign is not None and len(hidden_sign) >= 6:
		success, payload = True, {'email': email_adress, 'password': hidden_sign}
		ACC_LOGIN = requests.request('POST', API_LOGINS, headers=head_WEB, allow_redirects=True, verify=False, json=payload, timeout=20)
		debug_MS(f"(navigator.create_account[1]) === ACCOUNT_LOGIN === STATUS : {ACC_LOGIN.status_code} || CONTENT : {ACC_LOGIN.text} ===")
		if ACC_LOGIN.status_code != 401:
			debug_MS("(navigator.create_account[2]) ##### ALLE DATEN GEFUNDEN - DIE REGISTRIERUNG WAR ERFOLGREICH #####")
			addon.setSetting('emailing', email_adress)
			addon.setSetting('password', hidden_sign)
			addon.setSetting('username', f'[B]{email_adress}[/B]')
			xbmc.sleep(1000)
			return dialog.notification(translation(30543).format('Login'), translation(30544).format(email_adress), icon, 10000)
		else:
			return dialog.ok(addon_id, translation(30503))
	if success is False: return dialog.notification(translation(30545), translation(30546), icon , 10000)

def erase_account():
	debug_MS("(navigator.erase_account) XXXXX SPORTDEUTSCHLAND-KONTO ZWANGSWEISE AUS KODI ENTFERNEN - LÖSCHE ACCOUNT-DATEN - ERFOLGREICH XXXXX")
	addon.setSetting('emailing', '')
	addon.setSetting('password', '')
	addon.setSetting('username', '')
	xbmc.sleep(1000)
	return dialog.notification(translation(30543).format('Logout'), translation(30547), icon, 10000)

def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	LIVE_ALL, COUNT_ONE, SCORE_LIVE, SCORE_NEXT = (0 for _ in range(4))
	COMBI_PAGES, COMBI_EVENTS, COMBI_LIVES = ([] for _ in range(3))
	if nowlive or upcoming:
		for ii in range(1, 9, 1):
			MURL = f"{config['HOME_LIVENEXT']}page={str(ii)}&per_page=50"
			debug_MS(f"(navigator.mainMenu[1]) LIVE+NEXT-PAGES XXX POS = {str(ii)} || LINK = {MURL} XXX")
			COMBI_PAGES.append([int(ii), MURL])
		if COMBI_PAGES:
			COMBI_EVENTS = getMultiData(COMBI_PAGES)
			if COMBI_EVENTS:
				debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
				DATA_ONE = json.loads(COMBI_EVENTS)
				for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
					if results is not None and results.get('data', '') and len(results['data']) > 0:
						POS, DEM = results['Position'], results['Demand']
						POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT = getNumeros(results, 'livestreams', POS, DEM)
						COMBI_LIVES.append([POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT])
				if COMBI_LIVES:
					LIVE_ALL, ONE_COUNT, LIVE_DEAD, LIVE_FREE, LIVE_PAY, NEXT_FREE, NEXT_PAY = COMBI_LIVES[0][2], charge(3, COMBI_LIVES), \
						charge(4, COMBI_LIVES), charge(5, COMBI_LIVES), charge(6, COMBI_LIVES), charge(7, COMBI_LIVES), charge(8, COMBI_LIVES)
					SCORE_LIVE = (ONE_COUNT - sum([LIVE_DEAD, LIVE_PAY, NEXT_FREE, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else (LIVE_FREE - LIVE_DEAD)
					SCORE_NEXT = (ONE_COUNT - sum([LIVE_FREE, LIVE_PAY, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else NEXT_FREE
					debug_MS(f"(navigator.mainMenu[2]) COUNTERS *** NUM_EVENTS = {ONE_COUNT} || TOTAL_EVENTS = {LIVE_ALL} || SCORE_LIVE = {SCORE_LIVE} || FREE_LIVE = {LIVE_FREE} || PAY_LIVE = {LIVE_PAY} || SCORE_NEXT = {SCORE_NEXT} || FREE_NEXT = {NEXT_FREE} || PAY_NEXT = {NEXT_PAY} ***")
	if nowlive and SCORE_LIVE > 0:
		FETCH_UNO = create_entries({'Title': translation(30701).format(SCORE_LIVE), 'Plot': translation(30702).format(SCORE_LIVE), 'Image': f"{artpic}livestream.png"})
		addDir({'mode': 'listVideos', 'Link': config['HOME_LIVENEXT'], 'Limit': 50, 'Wanted': 4, 'Extras': 'playlive'}, FETCH_UNO)
	if upcoming and SCORE_NEXT > 0:
		UPC_TITLE = f"> {SCORE_NEXT}" if LIVE_ALL > ONE_COUNT else SCORE_NEXT
		FETCH_DUE = create_entries({'Title': translation(30703).format(UPC_TITLE), 'Plot': translation(30704).format(UPC_TITLE), 'Image': f"{artpic}upcoming.png"})
		addDir({'mode': 'listVideos', 'Link': config['HOME_LIVENEXT'], 'Limit': 50, 'Wanted': 3, 'Extras': 'playnext'}, FETCH_DUE)
	addDir({'mode': 'listFavorites'}, create_entries({'Title': translation(30602), 'Image': f"{artpic}favourites.png"}))
	if newest: addDir({'mode': 'listVideos', 'Link': config['HOME_TOPS'], 'Limit': 40, 'Wanted': 2, 'Extras': 'playnext'}, create_entries({'Title': translation(30603)}))
	if xbmcvfs.exists(MENUES_FILE) and os.stat(MENUES_FILE).st_size > 0:
		for elem in preserve(MENUES_FILE):
			paras_MEN = {'mode': 'listCategories', 'Slug': elem.get('Slug'), 'Code': elem.get('Code'), 'Section': cleaning(elem.get('Title')), 'Limit': 20, 'Wanted': 3, 'Extras': 'tags', 'Title': cleaning(elem.get('Title'))}
			ACTION = FETCH_TRE = paras_MEN
			addDir(ACTION, create_entries(FETCH_TRE))
	if sporting: addDir({'mode': 'listSports', 'Link': config['SPORT_TYPES'], 'Limit': 20, 'Wanted': 10, 'Extras': 'sports', 'Name': 'Sportarten'}, create_entries({'Title': translation(30604)}))
	if channeling: addDir({'mode': 'listSports', 'Link': config['SPORT_PROFILE'], 'Limit': 40, 'Wanted': 25, 'Extras': 'channels', 'Name': 'Sportkanäle'}, create_entries({'Title': translation(30605)}))
	if teamsearch: addDir({'mode': 'SearchSDTV', 'Extras': 'PROFILEN'}, create_entries({'Title': translation(30606), 'Image': f"{artpic}basesearch.png"}))
	if videosearch: addDir({'mode': 'SearchSDTV', 'Extras': 'VIDEOS'}, create_entries({'Title': translation(30607), 'Image': f"{artpic}basesearch.png"}))
	addDir({'mode': 'SELECTION', 'Link': config['SPORT_TYPES'], 'Limit': 20, 'Wanted': 10}, create_entries({'Title': translation(30608), 'Image': f"{artpic}editmenu.png"}), False)
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30609), 'Image': f"{artpic}settings.png"}), False)
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive'):
			addDir({'mode': 'iConfigs'}, create_entries({'Title': translation(30610), 'Image': f"{artpic}settings.png"}), False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def SELECTION(TARGET, PAGE, LIMIT, WANTED):
	debug_MS("(navigator.SELECTION) -------------------------------------------------- START = SELECTION --------------------------------------------------")
	PAGE, MAXIMUM = int(PAGE), int(PAGE)+int(WANTED)
	counter, (COMBI_SITES, COMBI_SPORTS, STORED, NAMES, ENTRIES, FOLDERS) = 0, ([] for _ in range(6))
	for ii in range(PAGE, MAXIMUM, 1):
		SURL = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.SELECTION[1]) SELECTION-PAGES XXX POS = {str(ii)} || LINK = {SURL} XXX")
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
							ENTRIES.append({'Number': counter, 'Title': content['name'], 'Code': content['id'], 'Slug': content['slug']})
			debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
			debug_MS(f"(navigator.SELECTION[2]) XXXXX SPORT-MENÜ-EINTRÄGE AUF ANBIETER-LISTE : {ENTRIES} XXXXX")
			debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	if NAMES and ENTRIES:
		if xbmcvfs.exists(MENUES_FILE) and os.stat(MENUES_FILE).st_size > 0:
			positions = preserve(MENUES_FILE)
			STORED = [(int(nr.get('Number', 0)) - 1) for nr in positions]
			debug_MS(f"(navigator.SELECTION[3]) ##### LESE GESPEICHERTE BENUTZER-MENÜ-EINTRÄGE : {[int(nb.get('Number', 0)) for nb in positions]} #####")
		indicator = dialog.multiselect(translation(30712), NAMES, preselect=STORED)
		if indicator is None:
			debug_MS("(navigator.SELECTION[4]) <<<<< BENUTZER-MENÜ-EINTRÄGE NICHT VERÄNDERT - AKTION DURCH BENUTZER ABGEBROCHEN <<<<<")
			return
		FOLDERS = [ENTRIES[dm] for dm in indicator] if indicator else []
		if len(FOLDERS) == 0:
			debug_MS("(navigator.SELECTION[4]) !!!!! BENUTZER-MENÜ-EINTRÄGE SIND LEER - LÖSCHE MENUES_FILE !!!!!")
			xbmcvfs.delete(MENUES_FILE)
		elif len(FOLDERS) >= 1:
			debug_MS(f"(navigator.SELECTION[4]) ***** NEUE BENUTZER-MENÜ-EINTRÄGE ERFOLGREICH ERSTELLT : {FOLDERS} *****")
			preserve(MENUES_FILE, FOLDERS)
		xbmc.sleep(1000)
		xbmc.executebuiltin('Container.Refresh')
	else:
		failing(f"(navigator.SELECTION) ##### Keine COMBI_SPORTS-List - Kein Eintrag unter: {TARGET} gefunden #####")
		return dialog.notification(translation(30521).format('PROVIDER'), translation(30522), icon, 12000)

def listSports(TARGET, CODE, SECTOR, PAGE, LIMIT, WANTED, SCENE, SERIE):
	debug_MS("(navigator.listSports) -------------------------------------------------- START = listSports --------------------------------------------------")
	debug_MS(f"(navigator.listSports) ### LINK = {TARGET} ### CODE = {CODE} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### maxPAGES = {WANTED} ### EXTRA = {SCENE} ### SERIE = {SERIE} ###")
	PAGE, MAXIMUM = int(PAGE), int(PAGE)+int(WANTED)
	UNIKAT, (present, COMBI_PAGES, COMBI_FIRST, COMBI_SECOND) = set(), ([] for _ in range(4))
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == 0 and HIGHER is True:
		addDir({'mode': 'callingMain'}, create_entries({'Title': translation(30721), 'Image': f"{artpic}backmain.png"}))
	for ii in range(PAGE, MAXIMUM, 1): # 1. Alle Sportarten / 2. Vereine und Events / 3. Suche Vereine und Events
		PAGE += 1
		SLINK = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.listSports[1]) SPORT-PAGES XXX POS = {str(ii)} || LINK = {SLINK} XXX")
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
						debug_MS(f"(navigator.listSports[2]) xxxxx CATS-02 : {cats} xxxxx")
						SPID = cats.get('id', None)
						if SPID is None or SPID in UNIKAT:
							continue
						UNIKAT.add(SPID)
						CAT = cleaning(cats['name'])
						SORTTITLE = cleanUmlaut(CAT).lower()
						SLUG = cats['slug']
						branch = cleaning(cats['sport_type']['name']) if cats.get('sport_type', '') and cats['sport_type'].get('name', '') else 'sport'
						GENRE = SECTOR if branch == 'sport' and branch.lower() != SECTOR.lower() else branch.title()
						if SCENE == 'sports': GENRE = CAT
						imgID = (cats.get('image_url', None) or cats.get('image_id', None))
						PHOTO = IMG_categories.format(imgID) if imgID else icon
						DESC = (cleaning(cats.get('description', ''), True) or "")
						newDEM, newLIMIT, newWANTED, newSCENE = SLUG, 20, 3, 'tags'
						if SCENE in ['channels', 'teams']: # Direkt weiter zum Verein
							newDEM, newLIMIT, newWANTED, newSCENE = SLUG, 20, 3, 'profiles'
							DESC = translation(30722).format(CAT, DESC)
						NAME_ONE, NAME_TWO = (CAT for _ in range(2))
						COMBI_SECOND.append([POS, DEM, SPID, CAT, SORTTITLE, SLUG, newDEM, newLIMIT, newWANTED, newSCENE, NAME_ONE, NAME_TWO, PHOTO, DESC, GENRE])
	if COMBI_SECOND:
		for POS, DEM, SPID, CAT, SORTTITLE, SLUG, newDEM, newLIMIT, newWANTED, newSCENE, NAME_ONE, NAME_TWO, PHOTO, DESC, GENRE in sorted(COMBI_SECOND, key=lambda st: st[4]):
			handling = 'skipping' # Alle Sportarten oder Vereine und Events
			if SCENE in ['channels', 'teams']: # Nur Vereine und Events
				handling = 'adding'
				if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
					for article in preserve(FAVORIT_FILE):
						if article.get('Code') == SPID: handling = 'skipping'
			paras_SPO = {'mode': 'listCategories', 'Slug': newDEM, 'Code': SPID, 'Section': GENRE, 'Limit': newLIMIT, 'Wanted': newWANTED, \
				'Extras': newSCENE, 'Title': NAME_ONE, 'Plot': DESC, 'Genre': GENRE, 'Image': PHOTO}
			ACTION = FETCH_UNO = context = paras_SPO
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listSports[3]) ### ACTION : {ACTION} || FAVORITES_HANDLE : {handling} ###")
			addDir(ACTION, create_entries(FETCH_UNO), True, context, handling, HIGHER)
		if results is not None and SCENE == 'teams' and results.get('meta', '') and str(results['meta'].get('total')).isdecimal() and int(results['meta']['total']) > int(PAGE)*int(LIMIT): # 4 x 20 (PAGES=4 / LIMIT=20)
			debug_MS(f"(navigator.listSports[4]) NUMBERING ### totalRESULTS : {results['meta']['total']} || thisPAGE endet bei Eintrag : {str(int(PAGE-1)*int(LIMIT))} ###")
			debug_MS(f"(navigator.listSports[4]) NEXTPAGES ### Zeige nächste Seiten von ... No.{PAGE} bis No.{int(PAGE)+4} ... ###")
			FETCH_DUE = create_entries({'Title': translation(30723), 'Image': f"{artpic}nextpage.png"})
			addDir({'mode': 'listSports', 'Link': TARGET, 'Code': SPID, 'Section': GENRE, 'Page': PAGE, 'Limit': 20, 'Wanted': 3, 'Extras': SCENE, 'Name': SERIE}, FETCH_DUE)
	else:
		failing(f"(navigator.listSports) ##### Keine COMBI_SPORTS-List - Kein Eintrag unter: {TARGET} gefunden #####")
		return dialog.notification(translation(30525).format('Einträge'), translation(30527).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listCategories(TARGET, CODE, SECTOR, PAGE, LIMIT, WANTED, SCENE, SERIE):
	debug_MS("(navigator.listCategories) -------------------------------------------------- START = listCategories --------------------------------------------------")
	debug_MS(f"(navigator.listCategories) ### URL/SLUG = {TARGET} ### CODE = {CODE} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### maxPAGES = {WANTED} ### EXTRA = {SCENE} ### SERIE = {SERIE} ###")
	PAGE, LIMIT, MAXIMUM = int(PAGE), int(LIMIT), int(PAGE)+int(WANTED)
	MEMBERS, COMBI_PAGES, COMBI_EVENTS, COMBI_LIVES, COMBI_ASSET, COMBI_TOPTYP, COMBI_LAST = ([] for _ in range(7))
	UNIKAT, (number, FOUND) = set(), (0 for _ in range(2))
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
			debug_MS(f"(navigator.listCategories[1]) CATEGORY-PAGES XXX POS = {number} || newLIMIT = {BOOST} || LINK = {CLINK} XXX")
			COMBI_PAGES.append([int(number), CLINK])
	if COMBI_PAGES:
		COMBI_EVENTS = getMultiData(COMBI_PAGES)
		if COMBI_EVENTS:
			DATA_ONE = json.loads(COMBI_EVENTS)
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and results.get('data', '') and len(results['data']) > 0:
					POS, DEM = results['Position'], results['Demand']
					if 'livestreams' in DEM:
						POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT = getNumeros(results, 'livestreams', POS, DEM)
						COMBI_LIVES.append([POS_ONE, ORIG_ONE, ALL_LIVE, COUNT_ONE, DEAD_LIVE, FREE_LIVE, PAY_LIVE, FREE_NEXT, PAY_NEXT, LPID, LCAT])
					if '/assets' in DEM:
						POS_TWO, ORIG_TWO, ALL_ASS, COUNT_TWO, DUM_1, FREE_ASS, PAY_ASS, DUM_2, DUM_3, APID, ACAT = getNumeros(results, '/assets', POS, DEM)
						COMBI_ASSET.append([POS_TWO, ORIG_TWO, ALL_ASS, COUNT_TWO, DUM_1, FREE_ASS, PAY_ASS, DUM_2, DUM_3, APID, ACAT])
					if '/top-assets' in DEM or 'sport-types' in DEM:
						TYPING = '/top-assets' if '/top-assets' in DEM else 'sport-types'
						POS_THREE, ORIG_THREE, ALL_TOP, COUNT_THREE, DUM_4, FREE_TOP, PAY_TOP, DUM_5, DUM_6, TPID, TCAT = getNumeros(results, TYPING, POS, DEM)
						COMBI_TOPTYP.append([POS_THREE, ORIG_THREE, ALL_TOP, COUNT_THREE, DUM_4, FREE_TOP, PAY_TOP, DUM_5, DUM_6, TPID, TCAT])
	if COMBI_LIVES or COMBI_ASSET or COMBI_TOPTYP:
		SCORE_LIVE, SCORE_NEXT, SCORE_ASSE, SCORE_TOPS = (0 for _ in range(4))
		if COMBI_LIVES:
			LIVE_ALL, ONE_COUNT, LIVE_DEAD, LIVE_FREE, LIVE_PAY, NEXT_FREE, NEXT_PAY = COMBI_LIVES[0][2], charge(3, COMBI_LIVES), \
				charge(4, COMBI_LIVES), charge(5, COMBI_LIVES), charge(6, COMBI_LIVES), charge(7, COMBI_LIVES), charge(8, COMBI_LIVES)
			SCORE_LIVE  = (ONE_COUNT - sum([LIVE_DEAD, LIVE_PAY, NEXT_FREE, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else (LIVE_FREE - LIVE_DEAD)
			SCORE_NEXT = (ONE_COUNT - sum([LIVE_FREE, LIVE_PAY, NEXT_PAY])) if LIVE_ALL > ONE_COUNT else NEXT_FREE
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
					NAME_ONE, NAME_TWO = (translation(30731).format(TITLE+CAT, PREFIX, SUFFIX) for _ in range(2))
					IMG = next((f"{artpic}{pm.get('member')}.png" for pm in config['picks'] if pm.get('member') == RECORD and xbmcvfs.exists(f"{artpic}{pm.get('member')}.png")), icon)
					if RECORD == 'livestream' and SCORE_LIVE >= 1:
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_uno[1].split('?')[0]}?", 50, 2, 'playlive', im_uno[8], im_uno[9]
						NAME_ONE = translation(30732).format(NAME_ONE)
						PLOT = translation(30733).format(SUFFIX)
					elif RECORD == 'upcoming' and SCORE_NEXT >= 1:
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_uno[1].split('?')[0]}?", 50, 2, 'playnext', im_uno[8], im_uno[9]
						NAME_ONE = translation(30734).format(NAME_ONE)
						PLOT = translation(30735).format(CAT, PREFIX, SUFFIX)
					elif RECORD in ['latest', 'highlights'] and (SCORE_ASSE >= 1 or SCORE_TOPS >= 1):
						FOUND += 1
						(NEW_URL, newPID, newCAT) = (im_due[1], im_due[8], im_due[9]) if RECORD == 'latest' else (im_tre[1], im_tre[8], im_tre[9])
						newDEM, newLIMIT, newWANTED, newSCENE = f"{NEW_URL.split('?')[0]}?", 40, 2, 'tags'
						PLOT = translation(30736).format(TITLE, CAT, PREFIX, SUFFIX)
					elif RECORD == 'sporttypes':
						FOUND += 1
						newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT = f"{im_tre[1].split('?')[0]}?", 20, 3, 'teams', im_tre[8], im_tre[9]
						PLOT = translation(30737).format(CAT, PREFIX, SUFFIX)
					debug_MS(f"(navigator.listCategories[2]) NUMBERING ### CATEGORY : {TITLE+CAT} ### TOTAL : {TOTAL} ### FORFREE : {SUFFIX} ###")
					COMBI_LAST.append([SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT])
	if COMBI_LAST and FOUND == 1:
		debug_MS("---------------------------------------------")
		for SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT in COMBI_LAST:
			addDir({'mode': 'blankFUNC'}, create_entries({'Title': translation(30738).format(NAME_TWO), 'Genre': SECTOR, 'Image': IMG}), False)
			if 'livestreams' in newDEM or 'assets' in newDEM:
				debug_MS("(navigator.listCategories[3]) ----- NUR EIN EINTRAG GEFUNDEN - gehe direkt zu = listVideos -----")
				return listVideos(newDEM, SECTOR, 1, newLIMIT, 0, 0, newWANTED, newSCENE)
			else:
				debug_MS("(navigator.listCategories[3]) ----- NUR EIN EINTRAG GEFUNDEN - gehe direkt zu = listSports -----")
				return listSports(newDEM, newPID, SECTOR, 1, newLIMIT, newWANTED, newSCENE, newCAT)
	elif COMBI_LAST and FOUND >= 2:
		for SECTOR, newDEM, newLIMIT, newWANTED, newSCENE, newPID, newCAT, NAME_ONE, NAME_TWO, IMG, PLOT in COMBI_LAST:
			debug_MS("---------------------------------------------")
			FETCH_UNO = create_entries({'Title': NAME_ONE, 'Plot': PLOT, 'Genre': SECTOR, 'Image': IMG})
			if 'livestreams' in newDEM: # Alle Ordner mit LiveNext-Videos
				addDir({'mode': 'listVideos', 'Link': newDEM, 'Section': SECTOR, 'Limit': newLIMIT, 'Wanted': newWANTED, 'extras': newSCENE}, FETCH_UNO)
			if 'assets' in newDEM: # Alle Ordner mit VOD-Videos
				addDir({'mode': 'listVideos', 'Link': newDEM, 'Section': SECTOR, 'Limit': newLIMIT, 'Wanted': newWANTED, 'extras': newSCENE}, FETCH_UNO)
			if 'sport-types' in newDEM: # Alle Sportarten oder Vereine und Events
				addDir({'mode': 'listSports', 'Link': newDEM, 'Code': newPID, 'Section': SECTOR, 'Limit': newLIMIT, 'Wanted': newWANTED, 'Extras': newSCENE, 'Name': newCAT}, FETCH_UNO)
			debug_MS(f"(navigator.listCategories[3]) ### NAME : {NAME_ONE} || LINK : {newDEM} || TYPE : {newSCENE} || PHOTO : {IMG} ###")
	else:
		failing(f"(navigator.listCategories) ##### Keine COMBI_CATEGORIES-List - Kein Eintrag für: {SERIE} gefunden #####")
		return dialog.notification(translation(30525).format('Einträge'), translation(30527).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSDTV(CAT, keyword=None):
	debug_MS("(navigator.SearchSDTV) ------------------------------------------------ START = SearchSDTV -----------------------------------------------")
	if xbmcvfs.exists(SEARCH_FILE):
		with open(SEARCH_FILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30751).format(CAT), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote(keyword)
			with open(SEARCH_FILE, 'w') as record:
				record.write(keyword)
	if keyword:
		if CAT == 'PROFILEN': return listSports(config['SEARCH_PROFILE'].format(keyword), '', 'Sport', 1, 40, 10, 'teams', 'Profilsuche')
		elif CAT == 'VIDEOS': return listVideos(config['SEARCH_VIDEO'].format(keyword), 'Sport', 1, 40, 0, 0, 5, 'playnext')
	return None

def listVideos(TARGET, SECTOR, PAGE, LIMIT, POS, KICKED, WANTED, SCENE):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug_MS(f"(navigator.listVideos) ### URL = {TARGET} ### GENRE = {SECTOR} ### PAGE = {PAGE} ### LIMIT = {LIMIT} ### POSITION = {POS} ### EXCLUDED = {KICKED} ### maxPAGES = {WANTED} ### showLIVE = {SCENE} ###")
	counterTWO, excludedTWO, PAGE, MAXIMUM = int(POS), int(KICKED), int(PAGE), int(PAGE)+int(WANTED)
	counterONE, excludedONE, number = (0 for _ in range(3))
	UNIKAT, (COMBI_PAGES, COMBI_FIRST, COMBI_SECOND, COMBI_LINKS, COMBI_THIRD, COMBI_FOURTH, SENDING) = set(), ([] for _ in range(7))
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == 0 and HIGHER is True:
		addDir({'mode': 'callingMain'}, create_entries({'Title': translation(30761), 'Image': f"{artpic}backmain.png"}))
	for ii in range(PAGE, MAXIMUM, 1):
		PAGE += 1
		VLINK = f"{TARGET}page={str(ii)}&per_page={LIMIT}"
		debug_MS(f"(navigator.listVideos[1]) VIDEO-PAGES XXX POS = {str(ii)} || LINK = {VLINK} XXX")
		COMBI_PAGES.append([int(ii), VLINK])
	if COMBI_PAGES:
		COMBI_FIRST = getMultiData(COMBI_PAGES)
		if COMBI_FIRST:
			#log("+++++++++++++++++++++++++++++++++++++++++++++")
			DATA_ONE = json.loads(COMBI_FIRST)
			for results in sorted(DATA_ONE, key=lambda pn: int(pn.get('Position', 0))):
				if results is not None and ((results.get('data', '') and len(results['data']) > 0) or (results.get('assets', '') and len(results['assets']) > 0)):
					POS, PATH_ONE = results['Position'], results['Demand']
					items = results['data'] if results.get('data', '') and len(results['data']) > 0 else results['assets']
					for item in items:
						startCOMPLETE, startDATE, startTIME, SORTDAY, AIRED, BEGINS, endDATE, tags, SLUG_ONE, TEA_ONE, NOTIZ = (None for _ in range(11))
						(GENRE, PREFIX, DESC_ONE), (NEXTCOME, RUNNING, LIVING), branch, shorties = ("" for _ in range(3)), (False for _ in range(3)), 'sport', []
						#log(f"(navigator.listVideos[2]) xxxxx ITEM-02 : {item} xxxxx")
						counterONE, counterTWO = counterONE.__add__(1), counterTWO.__add__(1)
						UID_ONE = item.get('id', None)
						if UID_ONE is None or UID_ONE in UNIKAT:
							excludedONE, excludedTWO = excludedONE.__add__(1), excludedTWO.__add__(1)
							continue
						UNIKAT.add(UID_ONE)
						TITLE = cleaning(item['name'])
						if str(item.get('content_start_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdecimal():
							LOCALstart = get_CentralTime(item['content_start_date']) # 2024-05-10T17:15:18.000000Z
							startCOMPLETE = LOCALstart.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
							for tt in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))):
								startCOMPLETE = startCOMPLETE.replace(*tt)
							startDATE = LOCALstart.strftime('%d.%m.%Y')
							startTIME = LOCALstart.strftime('%H:%M')
							if datetime.now() < LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = True, False # 19:44 < 20:00-15m = 19:45
							if datetime.now() > LOCALstart - timedelta(minutes=15): NEXTCOME, RUNNING = False, True # 19:46 > 20:00-15m = 19:45
							if datetime.now() > LOCALstart + timedelta(hours=12): NEXTCOME, RUNNING = False, False # 22:00 > 09:45+12h = 21:45
							SORTDAY = LOCALstart.strftime('%Y.%m.%dT%H:%M')
							BEGINS = LOCALstart.strftime('%Y-%m-%dT%H:%M') if KODI_ov20 else LOCALstart.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
							AIRED = LOCALstart.strftime('%d.%m.%Y') # FirstAired
						if str(item.get('content_end_date'))[:10].replace('.', '').replace('-', '').replace('/', '').isdecimal():
							LOCALend = get_CentralTime(item['content_end_date']) # 2024-05-10T20:00:18.000000Z
							endDATE = LOCALend.strftime('%d.%m.%YT%H:%M')
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
						if str(item.get('price_in_cents')).isdecimal() or len([euro for euro in item.get('monetizations', '')]) > 0:
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
			#log("+++++++++++++++++++++++++++++++++++++++++++++")
			for elem in DATA_TWO:
				if elem is not None and ((elem.get('videos', '') and len(elem['videos']) > 0) or (elem.get('livestream', '') and elem['livestream'].get('src', ''))):
					METER, PATH_TWO = elem['Position'], elem['Demand']
					(VID_TWO, TYP_TWO), DUR_TWO, DESC_TWO = (None for _ in range(2)), 0, ""
					#log(f"(navigator.listVideos[3]) xxxxx ELEM-03 : {str(elem)} xxxxx")
					UID_TWO = (elem.get('uuid', '') or elem.get('id', ''))
					if elem.get('videos', '') and len(elem['videos']) > 0:
						VID_TWO = next((src.get('src') for src in elem.get('videos', {})), None)
						TYP_TWO = next((pem.get('type') for pem in elem.get('videos', {})), None)
						DUR_TWO = next((ura.get('duration') for ura in elem.get('videos', {}) if str(ura.get('duration')).isdecimal()), None)
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
		COMPLETE = [ac + bg for ac in COMBI_SECOND for bg in COMBI_FOURTH if ac[1] == bg[1]] # Zusammenführung von Liste1 und Liste2 - wenn die ID überein stimmt !!!
		if SCENE == 'playnext': # Nur 'upcoming' Folder ohne Videos anzeigen !!!
			COMPLETE += [cm for cm in COMBI_SECOND if all(ds[1] != cm[1] for ds in COMBI_FOURTH)] # Der übriggebliebene Rest von Liste1 - wenn die ID nicht in der Liste2 vorkommt !!!
		#log("+++++++++++++++++++++++++++++++++++++++++++++")
		#log(f"(navigator.listVideos[2/4]) no.04 XXXXX COMPLETE-04 : {str(COMPLETE)} XXXXX")
		debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
		COMPLETE = sorted(COMPLETE, key=lambda vu: vu[5], reverse=True) if 'search/assets' in TARGET else sorted(COMPLETE, key=lambda cr: int(cr[0]))
		for vid in COMPLETE: # 0-11 = Liste1 || 12-18 = Liste2
			debug_MS(f"(navigator.listVideos[2/4]) ### Anzahl = {str(len(vid))} || Eintrag : {vid} ###")
			'''
				Full-Liste-1 = Number1, Mark1, title, name, thumb, sorting, begins, aired, genre, prefix, Desc1, LIVESTREAM = vid[0], vid[1], vid[2], vid[3], vid[4], vid[5], vid[6], vid[7], vid[8], vid[9], vid[10], vid[11]
				Full-Liste-2 = Number2, Mark2, TESTING, CODING, MUXING, duration, Desc2 = vid[12], vid[13], vid[14], vid[15], vid[16], vid[17], vid[18]
			'''
			if len(vid) >= 19: ### Liste1+Liste2 ist gleich Nummer:19 ###
				Number1, Mark1, title, name, thumb, sorting, begins, aired, genre, prefix, Desc1, LIVESTREAM = vid[0], vid[1], vid[2], vid[3], vid[4], vid[5], vid[6], vid[7], vid[8], vid[9], vid[10], vid[11]
				Number2, Mark2, TESTING, CODING, MUXING, duration, Desc2 = vid[12], vid[13], vid[14], vid[15], vid[16], vid[17], vid[18]
				FULL_DESC = Desc2 if len(Desc2) > 70 else Desc1
			else:
				Number1, Mark1, title, name, thumb, sorting, begins, aired, genre, prefix, FULL_DESC, LIVESTREAM = vid[0], vid[1], vid[2], vid[3], vid[4], vid[5], vid[6], vid[7], vid[8], vid[9], vid[10], vid[11]
				(TESTING, CODING, MUXING), duration, Desc2 = (None for _ in range(3)), 0, ""
			plot = prefix+FULL_DESC
			debug_MS(f"(navigator.listVideos[2/4]) ##### POS : {vid[0]} || NAME : {name} || MEDIA_IDD : {Mark1} || TYPE : {MUXING} || GENRE : {genre} #####")
			debug_MS(f"(navigator.listVideos[2/4]) ##### STREAM_CODE : {CODING} || DURATION : {duration} || THUMB : {thumb} #####")
			debug_MS("---------------------------------------------")
			FETCH_UNO = create_entries({'Title': name,'Plot': plot, 'Duration': duration, 'Date': begins, 'Aired': aired, 'Genre': genre, 'Mediatype': 'movie', 'Image': thumb, 'Fanback': thumb, 'Reference': 'Single'})
			addDir({'mode': 'playCODE', 'IDENTiTY': Mark1}, FETCH_UNO, False, higher=HIGHER)
			SENDING.append({'Filter': Mark1, 'Name': name, 'Photo': thumb, 'Plot': plot, 'Genre': genre, 'Testing': TESTING, 'Coding': CODING, 'Muxing': MUXING, 'Live': LIVESTREAM})
		preserve(WORKS_FILE, SENDING)
		debug_MS(f"(navigator.listVideos[3/5]) NUMBERING ### current_RESULT : {counterONE} || all_RESULT : {counterTWO} ### current_EXCLUDED : {excludedONE} || all_EXCLUDED : {excludedTWO} ###")
		if results is not None and not (SCENE == 'playlive' and 'livestreams' in TARGET) and results.get('meta', '') and str(results['meta'].get('total')).isdecimal():
			debug_MS(f"(navigator.listVideos[4/6]) NUMBERING ### totalRESULTS : {results['meta']['total']} || thisPAGE endet bei Eintrag : {int(PAGE-1)*int(LIMIT)} ###")
			if int(results['meta']['total']) > int(counterTWO):
				debug_MS(f"(navigator.listVideos[4/6]) NEXTPAGES ### Zeige nächste Seite ... No.{PAGE} ... ###")
				FETCH_DUE = create_entries({'Title': translation(30767), 'Image': f"{artpic}nextpage.png"})
				addDir({'mode': 'listVideos', 'Link': TARGET, 'Section': genre, 'Page': PAGE, 'Limit': LIMIT, 'Meter': counterTWO, 'Excluded': excludedTWO, 'Wanted': WANTED, 'Extras': SCENE}, FETCH_DUE)
	else:
		failing(f"(navigator.listVideos) ##### Keine COMBI_VIDEO-List - Kein Eintrag unter: {TARGET} gefunden #####")
		return dialog.notification(translation(30525).format('Einträge'), translation(30526), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playCODE(PLID):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### SOURCE = {PLID} ###")
	Status, attempts, (INSPECT, VIDEO, TYPE, RELAY_ONE, SUCCESS, RELAY_TWO, FINAL_ONE, FINAL_WORKS, STREAM_WORKS, TEST_WORKS) = 'OFFLINE', 0, (False for _ in range(10))
	for elem in preserve(WORKS_FILE):
		if elem['Filter'] != '00' and elem['Filter'] == PLID:
			CLEAR_TITLE, PHOTO, PLOT, GENRE, INSPECT, VIDEO, TYPE, NOW_LIVE = re.sub('(\[/?B\])', '', elem['Name']), elem['Photo'], elem['Plot'], elem['Genre'], elem['Testing'], elem['Coding'], elem['Muxing'], elem['Live']
			debug_MS(f"(navigator.playCODE[1]) ### WORKS_FILE-Line : {elem} ###")
	if INSPECT and VIDEO and TYPE:
		debug_MS("---------------------------------------------")
		FIRST = getContent(INSPECT, queries='JSON', timeout=20)
		if FIRST is not None and FIRST.get('livestream', '') and FIRST['livestream'].get('src', '') and FIRST.get('currently_live', False) is True:
			Status = 'LIVE_ONLINE'
		elif FIRST is not None and FIRST.get('videos', '') and len(FIRST['videos']) > 0 and FIRST.get('currently_live', True) is False:
			Status = 'VODS_ONLINE'
		if Status in ['LIVE_ONLINE', 'VODS_ONLINE']:
			TOKEN_LINK = config['PLAY_MUX'].format(PLID, TYPE, VIDEO) if TYPE.startswith('mux') else config['PLAY_LEGACY'].format(PLID)
			RELAY_ONE = getContent(TOKEN_LINK, queries='TRACK', timeout=20)
			if RELAY_ONE.status_code == 401 and 'error":"LOGIN_REQUIRED' in RELAY_ONE.text and addon.getSetting('emailing') != "" and addon.getSetting('password') != "":
				payload = {'email': addon.getSetting('emailing'), 'password': addon.getSetting('password')}
				with requests.Session() as xrs:
					LOGIN_QUERY = xrs.request('POST', API_LOGINS, headers=head_WEB, allow_redirects=True, verify=False, json=payload, timeout=20)
					debug_MS(f"(navigator.playCODE[2]) === ACCOUNT_LOGIN-1 === STATUS : {LOGIN_QUERY.status_code} || CONTENT : {LOGIN_QUERY.text} ===")
					debug_MS("---------------------------------------------")
					if LOGIN_QUERY.status_code == 409 and 'error":"auth.too_many_devices' in LOGIN_QUERY.text:
						section_one = next(filter(lambda sx: sx.get('device_icon', '') == 'fa fa-question-circle' and sx.get('device_name', '') == 'Browser', LOGIN_QUERY.json()['active_devices']), None)
						section_two = LOGIN_QUERY.json()['active_devices'][0].get('delete_url', None)
						choosen = section_one['delete_url'] if section_one else section_two
						REMOVE_URL = xrs.request('DELETE', choosen, headers=head_WEB, allow_redirects=True, verify=False, timeout=20)
						if REMOVE_URL.status_code in [200, 201, 202] and 'message":"Delete successful' in REMOVE_URL.text:
							debug_MS(f"(navigator.playCODE[3]) ##### REMOVE_URL : IHR ÄLTESTES EINGETRAGENES GERÄT WURDE ERFOLGREICH GELÖSCHT #####")
							debug_MS("---------------------------------------------")
							LOGIN_QUERY = xrs.request('POST', API_LOGINS, headers=head_WEB, allow_redirects=True, verify=False, json=payload, timeout=20)
							debug_MS(f"(navigator.playCODE[4]) === ACCOUNT_LOGIN-2 === STATUS : {LOGIN_QUERY.status_code} || CONTENT : {LOGIN_QUERY.text} ===")
							debug_MS("---------------------------------------------")
							if LOGIN_QUERY.status_code in [200, 201, 202] and not 'error' in LOGIN_QUERY.text:
								SUCCESS = True
						else:
							failing(f"(navigator.playCODE[3]) ERROR - REMOVE_URL - ERROR ##### STATUS : {REMOVE_URL.status_code} === DETAILS : {REMOVE_URL.text} #####")
							xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
							xbmc.PlayList(1).clear()
					elif LOGIN_QUERY.status_code in [200, 201, 202] and not 'error' in LOGIN_QUERY.text:
						SUCCESS = True
					if SUCCESS is True:
						RELAY_TWO = xrs.request('GET', TOKEN_LINK, headers=head_WEB, allow_redirects=True, verify=False, timeout=20)
						debug_MS(f"(navigator.playCODE[3/5]) === RELAY_TWO === STATUS : {RELAY_TWO.status_code} || CONTENT : {RELAY_TWO.text} ===")
						debug_MS("---------------------------------------------")
			elif RELAY_ONE.status_code == 401 and 'error":"LOGIN_REQUIRED' in RELAY_ONE.text and (addon.getSetting('emailing') == "" or addon.getSetting('password') == ""):
				failing(f"(navigator.playCODE[2]) ERROR - LOGIN_REQUIRED - ERROR ##### STATUS : {RELAY_ONE.status_code} ===\n === UM DIESES VIDEO ZU SEHEN MÜSSEN EINEN ►FREE-ACCOUNT◄ UNTER ►https://sportdeutschland.tv/◄ ERSTELLEN ===\n === DANACH BITTE DIE ACCOUNT-DATEN IN DEN EINSTELLUNGEN DES ADDONS SPEICHERN #####")
				xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
				xbmc.PlayList(1).clear()
				return dialog.ok(addon_id, translation(30504))
			transaction = RELAY_ONE if RELAY_ONE and RELAY_ONE.status_code in [200, 201, 202] else RELAY_TWO if RELAY_TWO and RELAY_TWO.status_code in [200, 201, 202] else None
			### 1. extract = "profile.slug": "tv-05-07-huettenberg", "slug": "2hbl-tv-05-07-huettenberg-vs-hsc-2000-coburg"
			### 2. getUrl = https://api.sportdeutschland.tv/api/stateless/frontend/assets/tv-05-07-huettenberg/2hbl-tv-05-07-huettenberg-vs-hsc-2000-coburg
			### 3.1. extract = videos[0]src: "https://chess.dosbnewmedia.de//mediafiles/e4dd01b062fc49018225e251a577726d.smil", videos[0]type: "smil"
			### 3.2. extract = videos[0]src: "EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA", videos[0]type: "mux_vod"
			###     or extract = "livestream.src": null
			### 4.1. getUrl = https://api.sportdeutschland.tv/api/frontend/asset-token/958f1bc4-0bbc-4a32-b5fa-ca5f380d7d81?type=legacy
			### 4.2. getUrl = https://api.sportdeutschland.tv/api/frontend/asset-token/95fd4975-646b-48d6-b422-ebe5ce9ebc11?type=mux_vod&playback_id=EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA
			### 5. extract = token if token else ""
			### 6.1. Video = https://chess.dosbnewmedia.de//mediafiles/e4dd01b062fc49018225e251a577726d.smil?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFRUVnQ3BhdnluTVlxTFN3V0ZQR0hTaERuRXU2OFRmcTZUeW1Wem1SaU9BIiwiYXVkIjoidiIsImV4cCI6MTY1MDYzMjg1NCwia2lkIjoiOXMxUG5YcGpwYlNQdldHMDJWWmoxakhNUHY5SHFqVEdJeGxlRGNiZzAwNDAyOCJ9.NAeFSuurX8aHN14Ej4jjPS0bXOu5tiV1PNR7R3Neamuaj8Gb5w8-C5K5DxOoh2om2A4UwNybAMBmXyilzdd_MY3gL1F-BBrZ15o4UiYNlQljlnjiSgzaW9VXHfmE97caNoc9PyQUiPGOVWmBEvv39fJERQaW4tIoqSzMlZX6YKJLspBkw4f9oDNZVyka8W9UeOTnHqv0vfTfNy7Y9jVemglkT4rZhm9QscOcF_dGDNpLRRsAHXci1T0g1e1uJ7wE8WduFdX1EUS7BC210GN94lojyzYjQh3QscO98GvYbm5pekZVWcJWE11kmolA3Ug-Wj9ZPz0H8Lny-2EPuV5DXQ
			### 6.2. Video = https://stream.mux.com/EEEgCpavynMYqLSwWFPGHShDnEu68Tfq6TymVzmRiOA.m3u8?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFRUVnQ3BhdnluTVlxTFN3V0ZQR0hTaERuRXU2OFRmcTZUeW1Wem1SaU9BIiwiYXVkIjoidiIsImV4cCI6MTY1MDYzMjg1NCwia2lkIjoiOXMxUG5YcGpwYlNQdldHMDJWWmoxakhNUHY5SHFqVEdJeGxlRGNiZzAwNDAyOCJ9.NAeFSuurX8aHN14Ej4jjPS0bXOu5tiV1PNR7R3Neamuaj8Gb5w8-C5K5DxOoh2om2A4UwNybAMBmXyilzdd_MY3gL1F-BBrZ15o4UiYNlQljlnjiSgzaW9VXHfmE97caNoc9PyQUiPGOVWmBEvv39fJERQaW4tIoqSzMlZX6YKJLspBkw4f9oDNZVyka8W9UeOTnHqv0vfTfNy7Y9jVemglkT4rZhm9QscOcF_dGDNpLRRsAHXci1T0g1e1uJ7wE8WduFdX1EUS7BC210GN94lojyzYjQh3QscO98GvYbm5pekZVWcJWE11kmolA3Ug-Wj9ZPz0H8Lny-2EPuV5DXQ
			if transaction:
				static_token = re.compile(r'''\{["']token["']:["'](eyJ[^"']+)["']\}''', re.S).findall(transaction.text)
				start_link = VIDEO.replace('.mp4', '.smil', 1) if VIDEO.endswith('.mp4') else config['PLAY_M3U8'].format(VIDEO) if VIDEO[:4] != 'http' else VIDEO
				ends_link = f"?token={static_token[0]}" if static_token else ""
				debug_MS(f"(navigator.playCODE[2/4/6]) === STATUS : {Status} === START_LINK+END_LINK : {start_link+ends_link} ===")
				if start_link.startswith('https://stream.mux.com/'):
					STREAM_ONE, FINAL_ONE = 'HLS', start_link+ends_link
				else:
					last_link = getUrl(start_link+ends_link, queries='TEXT')
					debug_MS(f"(navigator.playCODE[3/5/7]) === STATUS : {Status} === CONTENT-03 : {last_link} ===")
					source = re.compile(r'''<video src=["']([^"']+)["'] type=''', re.S).findall(last_link)
					models = re.compile(r'''["'] type=["']([^"']+)["']''', re.S).findall(last_link)
					STREAM_ONE = 'MP4' if models and models[0] == 'video/mp4' else 'HLS' if models and models[0].startswith('application') else 'M3U8'
					FINAL_ONE = source[0] if source else False
	if FINAL_ONE:
		while not TEST_WORKS and attempts < 2: # 2 x Pingtests for the STREAM-Request ::: to check the availability of the stream
			attempts += 1
			try:
				queries = Request(FINAL_ONE, None, {**head_DET, **{'Cache-Control': 'no-cache', 'Accept': '*/*'}})
				scanning = urlopen(queries, timeout=10)
				debug_MS("---------------------------------------------")
				debug_MS(f"(navigator.playCODE[3/5/7]) === CALL_{STREAM_ONE}_STREAM === RETRIES_no : {attempts} === STATUS : {scanning.getcode()} || URL : {FINAL_ONE} ===")
			except (URLError, HTTPError) as exc:
				failing("---------------------------------------------")
				failing(f"(navigator.playCODE[3/5/7]) ERROR - {STREAM_ONE}_STREAM - ERROR ##### RETRIES_no : {attempts} === URL : {FINAL_ONE} === FAILURE : {exc} #####")
				time.sleep(2)
			else:
				FINAL_WORKS, STREAM_WORKS, TEST_WORKS = FINAL_ONE, STREAM_ONE, True
				break
		if TEST_WORKS is False:
			failing("---------------------------------------------")
			failing(f"(navigator.playCODE[4/6/8]) ##### ABSPIELEN DES STREAMS NICHT MÖGLICH #####\n ##### QUERY : {API_PLAYER}{PLID} || STREAM_CODE : {VIDEO} #####\n ##### DIE VORHANDENEN STREAM-EINTRÄGE AUF DER WEBSEITE VON *Sportdeutschland.tv* SIND OFFLINE/DEFEKT !!! #####")
			xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
			xbmc.PlayList(1).clear()
			return dialog.notification(translation(30521).format('URL-2'), translation(30528), icon, 8000)
	else:
		failing("---------------------------------------------")
		failing(f"(navigator.playCODE[3/5/7]) ##### ABSPIELEN DES STREAMS NICHT MÖGLICH #####\n ##### QUERY : {API_PLAYER}{PLID} || STREAM_CODE : {VIDEO} #####\n ##### KEINEN STREAM-EINTRAG AUF DER WEBSEITE VON *Sportdeutschland.tv* GEFUNDEN !!! #####")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(offscreen=True))
		xbmc.PlayList(1).clear()
		return dialog.notification(translation(30521).format('URL-1'), translation(30529), icon, 8000)
	if FINAL_WORKS and TEST_WORKS:
		LPM = xbmcgui.ListItem(CLEAR_TITLE, path=FINAL_WORKS, offscreen=True)
		if PLOT in ['', 'None', None]: PLOT = ' '
		if KODI_ov20:
			LPM.getVideoInfoTag().setTitle(CLEAR_TITLE), LPM.getVideoInfoTag().setPlot(PLOT), LPM.getVideoInfoTag().setGenres([GENRE])
		else: LPM.setInfo('Video', {'Title': CLEAR_TITLE, 'Plot': PLOT, 'Genre': GENRE})
		LPM.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO})
		MIME_WORKS = 'video/mp4' if STREAM_WORKS == 'MP4' else 'application/x-mpegurl'
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive') and STREAM_WORKS in ['HLS', 'M3U8']:
			IA_NAME = 'inputstream.adaptive'
			IA_VERSION = re.sub(r'(~[a-z]+(?:.[0-9]+)?|\+[a-z]+(?:.[0-9]+)?$|[.^]+)', '', xbmcaddon.Addon(IA_NAME).getAddonInfo('version'))[:4]
			LPM.setMimeType(MIME_WORKS), LPM.setContentLookup(False), LPM.setProperty('inputstream', IA_NAME)
			if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
				LPM.setProperty(f"{IA_NAME}.manifest_type", 'hls')
			if KODI_ov20:
				LPM.setProperty(f"{IA_NAME}.manifest_headers", f"User-Agent={agent_WEB}") # On KODI v20 and above
			else: LPM.setProperty(f"{IA_NAME}.stream_headers", f"User-Agent={agent_WEB}") # On KODI v19 and below
			if int(IA_VERSION) >= 2150 and STREAM_WORKS == 'HLS':
				LPM.setProperty(f"{IA_NAME}.drm_legacy", 'org.w3.clearkey')
			LPM.setProperty(f"{IA_NAME}.play_timeshift_buffer", 'true')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
		debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
		log(f"(navigator.playCODE) {STREAM_WORKS}_stream : {FINAL_WORKS}")

def listFavorites():
	debug_MS("(navigator.listFavorites) ------------------------------------------------ START = listFavorites -----------------------------------------------")
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		snippets = preserve(FAVORIT_FILE) # Favoriten für Profile/Vereine
		for each in sorted(snippets, key=lambda sx: (sx.get('Extras', 'Zorro'), cleanUmlaut(sx.get('Title', 'Zorro').lower()))):
			paras_FAV = {'mode': 'listCategories', 'Slug': each.get('Slug'), 'Code': each.get('Code'), 'Section': each.get('Section', 'Sport'), 'Limit': each.get('Limit'), 'Wanted': each.get('Wanted'), \
				'Extras': each.get('Extras'), 'Title': cleaning(each.get('Title')), 'Plot': cleaning(each.get('Plot')), 'Genre': each.get('Section', 'Sport'), 'Image': each.get('Image')}
			ACTION = FETCH_UNO = context = paras_FAV
			debug_MS(f"(navigator.listFavorites[1]) ### NAME : {cleaning(each.get('Title'))} || SLUG : {each.get('Slug')} || THUMB : {each.get('Image')} ###")
			addDir(ACTION, create_entries(FETCH_UNO), True, context, 'removing')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favorit_construct(**kwargs):
	TOPS = []
	if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
		TOPS = preserve(FAVORIT_FILE)
	if kwargs['action'] == 'ADD':
		del kwargs['mode']; del kwargs['action']; del kwargs['Genre']
		TOPS.append({key: value if value != 'None' else None for key, value in kwargs.items()})
		preserve(FAVORIT_FILE, TOPS)
		xbmc.sleep(500)
		dialog.notification(translation(30530), translation(30531).format(kwargs['Title']), icon, 10000)
	elif kwargs['action'] == 'DEL':
		TOPS = [xs for xs in TOPS if xs.get('Code') != kwargs.get('Code')]
		if len(TOPS) == 0:
			xbmcvfs.delete(FAVORIT_FILE)
		elif len(TOPS) >= 1:
			preserve(FAVORIT_FILE, TOPS)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30530), translation(30532).format(kwargs['Title']), icon, 10000)

def addDir(params, listitem, folder=True, context={}, handling='default', higher=False):
	uws, entries = build_mass(params), []
	listitem.setPath(uws)
	if enableBACK and PLACEMENT == 1 and higher is True:
		entries.append([translation(30650), f"RunPlugin({build_mass({'mode': 'callingMain'})})"])
	if handling == 'adding' and context:
		entries.append([translation(30651), f"RunPlugin({build_mass({**context, **{'mode': 'favorit_construct', 'action': 'ADD'}})})"])
	if handling == 'removing' and context:
		entries.append([translation(30652), f"RunPlugin({build_mass({**context, **{'mode': 'favorit_construct', 'action': 'DEL'}})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
