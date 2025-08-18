# -*- coding: utf-8 -*-

from .common import *


def mainMenu():
	for TITLE, PATH in [(30601, {'mode': 'blankFUNC', 'url': '00'}), (30602, {'mode': 'listTrailers', 'category': 'MOVIES'}),
		(30603, {'mode': 'listBroadcasts', 'category': 'MOVIES'}), (30604, {'mode': 'blankFUNC', 'url': '00'}), (30605, {'mode': 'listTrailers', 'category': 'SERIES'}),
		(30606, {'mode': 'listBroadcasts', 'category': 'SERIES'}), (30607, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/interviews/", 'category': 'INTERVIEWS'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE)}), folder=False if TITLE in [30601, 30604] else True)
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30608), 'Image': f"{artpic}settings.png"}), False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTrailers(CATEGORY):
	if CATEGORY == 'MOVIES':
		for item in [{'name': 30621, 'turn': 'listVideos', 'slug': '/trailer/beliebteste.html'},{'name': 30622, 'turn': 'listVideos', 'slug': '/trailer/imkino/'},
			{'name': 30623, 'turn': 'listVideos', 'slug': '/trailer/bald/'},{'name': 30624, 'turn': 'listVideos', 'slug': '/trailer/neu/'},{'name': 30625, 'turn': 'filtrating', 'slug': '/trailer/archiv/'}]:
			addDir({'mode': item['turn'], 'url': f"{BASE_URL}{item['slug']}", 'category': 'ARCHIVES' if item['name'] == 30625 else 'TRAILERS'}, create_entries({'Title': translation(item['name'])}))
	else:
		for item in [{'name': 30626, 'slug': '/trailer/serien/kurz/'},{'name': 30627, 'slug': '/trailer/serien/meisterwartete/'},{'name': 30628, 'slug': '/trailer/serien/neueste/'}]:
			addDir({'mode': 'listVideos', 'url': f"{BASE_URL}{item['slug']}", 'category': 'TRAILERS'}, create_entries({'Title': translation(item['name'])}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(CATEGORY):
	if CATEGORY == 'MOVIES':
		for item in [{'name': 30631, 'turn': 'listVideos', 'slug': '/filme-imkino/vorpremiere/'},
			{'name': 30632, 'turn': 'listVideos', 'slug': '/filme-imkino/kinostart/'},{'name': 30633, 'turn': 'listVideos', 'slug': '/filme-imkino/neu/'},
			{'name': 30634, 'turn': 'listVideos', 'slug': '/filme-imkino/besten-filme/user-wertung/'},{'name': 30635, 'turn': 'selectionWeeks', 'slug': '/filme-vorschau/de/'},
			{'name': 30636, 'turn': 'filtrating', 'slug': '/kritiken/filme-alle/user-wertung/'},{'name': 30637, 'turn': 'filtrating', 'slug': '/kritiken/filme-alle/'}]:
			addDir({'mode': item['turn'], 'url': f"{BASE_URL}{item['slug']}", 'category': 'MOVIES' if item['name'] in [30636, 30637] else 'standard'}, create_entries({'Title': translation(item['name'])}))
	else:
		for item in [{'name': 30641, 'turn': 'listVideos', 'slug': '/serien/top/'},{'name': 30642, 'turn': 'filtrating', 'slug': '/serien/beste/'},
			{'name': 30643, 'turn': 'listVideos', 'slug': '/serien/top/populaerste/'},{'name': 30644, 'turn': 'listVideos', 'slug': '/serien/kommende-staffeln/meisterwartete/'},
			{'name': 30645, 'turn': 'listVideos', 'slug': '/serien/kommende-staffeln/'},{'name': 30646, 'turn': 'listVideos', 'slug': '/serien/kommende-staffeln/demnaechst/'},
			{'name': 30647, 'turn': 'listVideos', 'slug': '/serien/neue/'},{'name': 30648, 'turn': 'filtrating', 'slug': '/serien-archiv/'}]:
			addDir({'mode': item['turn'], 'url': f"{BASE_URL}{item['slug']}", 'category': 'SERIES' if item['name'] in [30642, 30648] else 'standard'}, create_entries({'Title': translation(item['name'])}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def filtrating(TARGET, CATEGORY):
	debug_MS("(navigator.filtrating) -------------------------------------------------- START = filtrating --------------------------------------------------")
	debug_MS(f"(navigator.filtrating) ### URL = {TARGET} ### CATEGORY = {CATEGORY} ###")
	if not 'genre-' in TARGET:
		addDir({'mode': 'selectionArticles', 'url': TARGET, 'category': CATEGORY, 'extras': 'Nach Genre'}, create_entries({'Title': translation(30801)}))
	if CATEGORY == 'ARCHIVES':
		if not 'sprache-' in TARGET:
			addDir({'mode': 'selectionArticles', 'url': TARGET, 'category': CATEGORY, 'extras': 'Nach Sprache'}, create_entries({'Title': translation(30802)}))
		if not 'format-' in TARGET:
			addDir({'mode': 'selectionArticles', 'url': TARGET, 'category': CATEGORY, 'extras': 'Nach Typ'}, create_entries({'Title': translation(30803)}))
	else:
		if not 'jahrzehnt' in TARGET:
			addDir({'mode': 'selectionArticles', 'url': TARGET, 'category': CATEGORY, 'extras': 'Nach Produktionsjahr'}, create_entries({'Title': translation(30804)}))
		if not 'produktionsland-' in TARGET:
			addDir({'mode': 'selectionArticles', 'url': TARGET, 'category': CATEGORY, 'extras': 'Nach Land'}, create_entries({'Title': translation(30805)}))
	addDir({'mode': 'listVideos', 'url': TARGET, 'category': CATEGORY}, create_entries({'Title': translation(30806)}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionArticles(TARGET, CATEGORY, TYPE):
	debug_MS("(navigator.selectionArticles) -------------------------------------------------- START = selectionArticles --------------------------------------------------")
	debug_MS(f"(navigator.selectionArticles) ### URL = {TARGET} ### CATEGORY = {CATEGORY} ### TYPE = {TYPE} ###")
	DATA_ONE = getContent(TARGET)
	results = DATA_ONE[DATA_ONE.find(f'data-name="{TYPE}"')+1:]
	results = results[:results.find('</ul>')]
	part = results.split('class="filter-entity-item"')
	for i in range(1, len(part), 1):
		entry = re.sub(r'</?strong>', '', part[i])
		matchH1 = re.compile(r'''class=["']item-content["'] href=["']([^"']+)["'] title=.+?["']>([^<]+)</a>''', re.S).findall(entry)
		matchH2 = re.compile(r'''<span class=["']ACr([^"']+) item-content["'] title=.+?["']>([^<]+)</span>''', re.S).findall(entry)
		LINK = BASE_URL+matchH1[0][0] if matchH1 else BASE_URL+convert64(matchH2[0][0])
		NAME = cleaning(matchH1[0][1]) if matchH1 else cleaning(matchH2[0][1])
		matchNUM = re.compile(r'''<span class=["']light["']>\(([^<]+)\)</span>''', re.S).findall(entry)
		if matchNUM: NAME += translation(30831).format(str(matchNUM[0].strip()))
		addDir({'mode': 'filtrating', 'url': LINK, 'category': CATEGORY}, create_entries({'Title': NAME}))
		debug_MS(f"(navigator.selectionArticles[1]) ##### NAME : {NAME} || LINK : {LINK} #####")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionWeeks(TARGET):
	debug_MS("(navigator.selectionWeeks) -------------------------------------------------- START = selectionWeeks --------------------------------------------------")
	debug_MS(f"(navigator.selectionWeeks) ### URL = {TARGET} ###")
	DATA_ONE = getContent(TARGET)
	results = DATA_ONE[DATA_ONE.find('<div class="pagination pagination-select">')+1:]
	results = results[:results.find('<span class="txt">Nächste</span><i class="icon icon-right icon-arrow-right-a">')]
	matchOPT = re.compile(r'''<option value=["']ACr([^"']+)["']([^<]+)</option>''', re.S).findall(results)
	for linkway, title in matchOPT:
		LINK = BASE_URL+convert64(linkway)
		DATES = re.sub(r'filme-vorschau/de/week-|/', '', linkway)
		NAME = translation(30832).format(cleaning(title.replace('>', '').replace('selected', ''))) if 'selected' in title else cleaning(title.replace('>', ''))
		addDir({'mode': 'listVideos', 'url': LINK, 'category': 'PREVIEWS'}, create_entries({'Title': NAME}))
		debug_MS(f"(navigator.selectionWeeks[1]) ##### NAME : {NAME} || DATE : {DATES} #####")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(TARGET, PAGE, POS, CATEGORY):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	COMBI_FIRST, COMBI_LINKS, COMBI_SECOND, SENDING = ([] for _ in range(4))
	UNIKAT, counter = set(), 0
	NEW_URL = f"{TARGET}?page={PAGE}" if int(PAGE) > 1 else TARGET
	debug_MS(f"(navigator.listVideos) ### URL = {NEW_URL} ### PAGE = {PAGE} ### POSITION = {POS} ### CATEGORY = {CATEGORY} ###")
	DATA_ONE = getContent(NEW_URL)
	HIGHER = True if int(PAGE) > 1 else False
	if enableBACK and PLACEMENT == 0 and HIGHER is True:
		addDir({'mode': 'callingMain'}, create_entries({'Title': translation(30833), 'Image': f"{artpic}backmain.png"}))
	matchPG = re.findall(r'''<nav class=["']pagination(.+?)<div class=["']mdl-rc["']>''', DATA_ONE, re.S)
	if int(POS) == 0 and matchPG:
		PG_ONE = re.compile(r'''<a class=["']button button-md item["'] href=.+?page=[0-9]+["']>([0-9]+)</a></div></nav>''', re.S).findall(matchPG[0])
		PG_TWO = re.compile(r'''<span class=["']ACr.+?button-md item["']>([0-9]+)</span></div></nav>''', re.S).findall(matchPG[0])
		POS = PG_ONE[0] if PG_ONE else PG_TWO[0] if PG_TWO else POS
		debug_MS(f"(navigator.listVideos[1]) NEXTPAGES ### Pages-Maximum : {POS} ###")
	results = DATA_ONE[DATA_ONE.find('<main id="content-layout" class="content-layout cf">')+1:]
	results = results[:results.find('<div class="mdl-rc">')]
	part = results.split('<figure class="thumbnail')
	for i in range(1, len(part), 1):
		entry = re.sub(r'</?strong>', ' ', part[i])
		debug_MS(f"(navigator.listVideos[1]) xxxxx ENTRY-01 : {entry} xxxxx")
		DESC_1, (DATE_1, RATING_1) = "", (None for _ in range(2))
		GENRE_1, DIRECTOR_1, WRITER_1, STAFF_1 = ([] for _ in range(4))
		matchH1 = re.compile(r'''(?:class=["']meta-title-link["']|class=["']layer-link-holder["']><a) href=["']([^"']+)["'](?: class=["']layer-link["']| )?>([^<]+)</a>''', re.S).findall(entry)
		matchH2 = re.compile(r'''class=["']thumbnail-container thumbnail-link["'] href=["']([^"']+)["'] title=["']([^"']+)["']>''', re.S).findall(entry)
		matchH3 = re.compile(r'''class=["']ACr([^ "']+) thumbnail-container thumbnail-link["'] title=["']([^"']+)["']''', re.S).findall(entry)
		ORLINK_1 = BASE_URL+matchH1[0][0] if matchH1 else BASE_URL+matchH2[0][0] if matchH2 else BASE_URL+convert64(matchH3[0][0])
		WFLINK_1 = f"{ORLINK_1.split('/videos')[0]}.html" if '/videos' in ORLINK_1 else f"{ORLINK_1.split('/trailer')[0]}.html" if '/trailer' in ORLINK_1 else f"{ORLINK_1.split('/staffel')[0]}.html" if '/staffel' in ORLINK_1 else ORLINK_1
		if CATEGORY != 'INTERVIEWS' and WFLINK_1 in UNIKAT:
			continue
		UNIKAT.add(WFLINK_1)
		TITLE_1 = cleaning(matchH1[0][1]) if matchH1 else cleaning(matchH2[0][1]) if matchH2 else cleaning(matchH3[0][1])
		IMAGE_1 = re.compile(r'''(?:class=["']thumbnail-img["'] |data-)src=["'](https?://.+?[a-z0-9]+(?:\.png|\.jpg|\.jpeg|\.jfif|\.gif))["'?]''', re.S).findall(entry)
		THUMB_1 = enlargeIMG(IMAGE_1[0]) if IMAGE_1 and len(IMAGE_1[0]) > 0 else None
		agreeDUR = re.compile(r'''class=["']thumbnail-count["']>([^<]+)</span>''', re.S).findall(entry) # Grab - Duration
		DURATION_1 = get_RunTime(agreeDUR[0]) if agreeDUR and len(agreeDUR[0]) > 0 else None # 1:55
		agreeVIS = re.compile(r'''class=["']meta-sub light["']>(.+?)</div>''', re.S).findall(entry)
		VISITORS_1 = cleaning(agreeVIS[0], True) if agreeVIS else None
		counter += 1
		WORKS_1 = True if '<span class="icon icon-play-arrow"></span>' in entry or DURATION_1 is not None else False
		if CATEGORY == 'INTERVIEWS':
			DESC_1, TITLE_1 = TITLE_1, 'FILMSTARTS - Interview'
			DESC_1 += translation(30834).format(VISITORS_1) if VISITORS_1 else ""
		if CATEGORY not in ['ARCHIVES', 'INTERVIEWS', 'TRAILERS']:
			AREA_1 = re.compile(r'''<div class=["']meta-body-item meta-body-info(.+?)</div>''', re.S).findall(entry) # Grab - Genres
			if '<span class="spacer">' in entry:
				AREA_1 = re.compile(r'''<span class=["']spacer["']>(.+?)<div class=["']meta-body-item(?: meta-body-direction)?''', re.S).findall(entry) # Grab - Genres
			agreeGEN = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(AREA_1[0]) if AREA_1 else []
			GENRE_1 = ' / '.join(sorted([cleaning(gens, True) for gens in agreeGEN])) if agreeGEN else [] # Drama, Familie, Komödie
			AREA_2 = re.compile(r'''<span class=["']light["']>Regie(.+?)</div>''', re.S).findall(entry) # Grab - Directors
			agreeDIR = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_2[0]) if AREA_2 else []
			DIRECTOR_1 = ', '.join([cleaning(dirs, True) for dirs in agreeDIR]) if agreeDIR else [] # Steven Seagal
			AREA_3 = re.compile(r'''<span class=["']light["']>(?:Drehbuch|Creator)(.+?)</div>''', re.S).findall(entry) # Grab - Writers
			agreeCREA = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_3[0]) if AREA_3 else []
			WRITER_1 = ', '.join([cleaning(creas, True) for creas in agreeCREA]) if agreeCREA else [] # Ed Horowitz, Robin U. Russin
			AREA_4 = re.compile(r'''<span class=["']light["']>Besetzung(.+?)</div>''', re.S).findall(entry) # Grab - Casts
			agreeACT = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_4[0]) if AREA_4 else []
			STAFF_1 = ','.join([cleaning(star, True) for star in agreeACT]) if agreeACT and len(agreeACT) > 0 else [] # Fran Monegan, Gabriel L. Muktoyuk, Helen Hakkila
			agreePLOT = re.compile(r'''<div class=["']content-txt(?: )?["']>(.+?)</div>''', re.S).findall(entry) # Grab - Plot
			DESC_1 = cleaning(agreePLOT[0], True) if agreePLOT else ""
			agreeDAT = re.compile(r'''<span class=["'](?:ACr.*?)?date(?: )?["']>(.+?)</span>''', re.S).findall(entry) # Grab - Date
			if '/serien' in ORLINK_1 or not agreeDAT:
				agreeDAT = re.compile(r'''<div class=["']meta-body-item meta-body-info["']>(.+?)<span class=["']spacer["']>''', re.S).findall(entry) # Grab - Date
			DATE_1 = cleaning(re.sub(r'\n|\<.*?\>|Im Kino|als VoD', '', agreeDAT[0])) if agreeDAT and len(agreeDAT[0]) > 0 else None # 20. Februar 2024 auf Amazon
			try:
				AREA_5 = (entry[entry.find('User-Wertung')+1:] or entry[entry.find('Pressekritiken')+1:]) # Grab - Rating
				RATING_1 = re.compile(r'''class=["']stareval-note["']>([^<]+)</span>''', re.S).findall(AREA_5)[0].strip().replace(',', '.') # 2,5
			except: pass
			COMBI_FIRST.append([int(counter), ORLINK_1, WFLINK_1, TARGET, TITLE_1, THUMB_1, GENRE_1, DIRECTOR_1, WRITER_1, STAFF_1, DESC_1, DATE_1, RATING_1, DURATION_1, WORKS_1])
			COMBI_LINKS.append([int(counter), CATEGORY, ORLINK_1, WFLINK_1])
		else:
			COMBI_FIRST.append([int(counter), ORLINK_1, WFLINK_1, TARGET, TITLE_1, THUMB_1, GENRE_1, DIRECTOR_1, WRITER_1, STAFF_1, DESC_1, DATE_1, RATING_1, DURATION_1, WORKS_1])
			COMBI_LINKS.append([int(counter), CATEGORY, ORLINK_1, WFLINK_1])
	if COMBI_FIRST and CATEGORY != 'INTERVIEWS': # Für Interviews kein Aufruf der 'COMBI_SECOND'
		COMBI_SECOND = listSubstances(COMBI_LINKS)
	if COMBI_FIRST or COMBI_SECOND: # Zusammenführung von Liste1 + Liste2 - wenn die Nummer an erster Stelle(0) überein stimmt !!!
		RESULT = [ac + bg for ac in COMBI_FIRST for bg in COMBI_SECOND if ac[0] == bg[0]] if CATEGORY != 'INTERVIEWS' else COMBI_FIRST # Für Interviews keine 'COMBI_SECOND'
		for xev in sorted(RESULT, key=lambda pn: int(pn[0])): # 0-14 = Liste1 || 15-34 = Liste2
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listVideos[3]) ### Anzahl : {len(xev)} || Eintrag : {xev} ###")
			Note_1, Note_2, Note_3 = ("" for _ in range(3))
			if len(xev) > 15: ### Liste2 beginnt mit Nummer:15 ###
				Number1, oLink1, wLink1, uLink1, Title1, Thumb1, Genre1, Director1, Writer1, Staff1, Desc1, Date1, Rated1, Dur1, Works1 = xev[0], xev[1], xev[2], xev[3], xev[4], xev[5], xev[6], xev[7], xev[8], xev[9], xev[10], xev[11], xev[12], xev[13], xev[14]
				Number2, oExtra2, oLink2, oLink3, Title2, Thumb2, Genre2, original, Director2, Writer2, Staff2, country, Mpaa2, Desc2, seasons, Date2, Rated2, Dur2, Works2, TEASER = xev[15], xev[16], xev[17], xev[18], xev[19], xev[20], xev[21], xev[22], xev[23], xev[24], xev[25], xev[26], xev[27], xev[28], xev[29], xev[30], xev[31], xev[32], xev[33], xev[34]
			else:
				Number1, oLink1, wLink1, uLink1, Title1, Thumb1, Genre1, Director1, Writer1, Staff1, Desc1, Date1, Rated1, Dur1, Works1 = xev[0], xev[1], xev[2], xev[3], xev[4], xev[5], xev[6], xev[7], xev[8], xev[9], xev[10], xev[11], xev[12], xev[13], xev[14]
				Number2, oExtra2, oLink2, oLink3, Title2, Thumb2, Genre2, original, Director2, Writer2, Staff2, country, Mpaa2, Desc2, seasons, Date2, Rated2, Dur2, Works2, TEASER = 0, 'standard', None, None, None, None, None, None, None, None, [], None, None, "", None, None, None, 0, False, None
			title = Title2 if Title2 and CATEGORY != 'ARCHIVES' else Title1
			duration = Dur2 if Dur2 and CATEGORY != 'ARCHIVES' else Dur1 if Dur1 else None
			image = Thumb2 if Thumb2 and CATEGORY != 'ARCHIVES' else Thumb1 if Thumb1 else None
			genre = Genre2 if Genre2 else Genre1 if Genre1 else None
			director = Director2 if Director2 else Director1 if Director1 else None
			writer = Writer2 if Writer2 else Writer1 if Writer1 else None
			actors = Staff2 if Staff2 else Staff1 if Staff1 else None
			STARTING = Date2 if Date2 else Date1
			rating = Rated2 if Rated2 else Rated1 if Rated1 else None
			agerate = translation(30835) if Mpaa2 and '0' in str(Mpaa2) else Mpaa2
			working = True if Works2 is True or Works1 is True else False
			transfer = TEASER if TEASER else oLink1
			if working is True:
				ACTION, name = {'mode': 'playCODE', 'IDENTiTY': transfer}, title
			else: ACTION, name = {'mode': 'blankFUNC', 'url': 'NO VIDEO'}, translation(30836).format(title)
			Note_1 = translation(30837).format(seasons) if seasons else ""
			if Date2 or Date1:
				BEGINNING = Date2.replace('er Starttermin', '') if Date2 else Date1.replace('er Starttermin', '')
				Note_2 = translation(30838).format(BEGINNING)
			if seasons and Date1 is None and Date2 is None: Note_2 = '[CR]'
			Note_3 = Desc2 if len(Desc2) > len(Desc1) else Desc1
			plot = Note_1+Note_2+Note_3
			debug_MS(f"(navigator.listVideos[4]) ##### NAME : {name} || LINK : {transfer} || DATE : {STARTING} #####")
			debug_MS(f"(navigator.listVideos[4]) ##### GENRE : {genre} || COUNTRY : {country} || DIRECTOR : {director} || WRITER : {writer} #####")
			debug_MS(f"(navigator.listVideos[4]) ##### TRAILER : {working} || DURATION : {duration} || THUMB : {image} #####")
			FETCH_UNO = create_entries({'Title': name, 'Original': original, 'Plot': plot, 'Duration': duration, 'Genre': genre, 'Country': country, 'Director': director, \
				'Writer': writer, 'Cast': actors, 'Rating': rating, 'Mpaa': agerate, 'Mediatype': 'movie', 'Image': image, 'Reference': 'Single' if working is True else 'Standard'})
			addDir(ACTION, FETCH_UNO, False, HIGHER)
			SENDING.append({'filter': transfer, 'name': name, 'photo': image, 'genre': genre})
		preserve(WORKS_FILE, SENDING)
	if counter == 0:
		return dialog.notification(translation(30525), translation(30526), icon, 10000)
	if BEFORE_AND_AFTER and CATEGORY == 'PREVIEWS':
		try:
			LEFT = convert64(re.compile(r'''<span class=["']ACr([^ "']+) button button-md button-primary-full button-left["']>.*?span class=["']txt["']>Vorherige</span>''', re.S).findall(results)[0])
			RIGHT = convert64(re.compile(r'''<span class=["']ACr([^ "']+) button button-md button-primary-full button-right["']>.*?span class=["']txt["']>Nächste</span>''', re.S).findall(results)[0])
			BeforeDAY, AfterDAY = re.sub(r'filme-vorschau/de/week-|/', '', LEFT), re.sub(r'filme-vorschau/de/week-|/', '', RIGHT)
			beforeDATE, afterDATE = datetime(*(time.strptime(BeforeDAY, '%Y-%m-%d')[0:6])), datetime(*(time.strptime(AfterDAY, '%Y-%m-%d')[0:6]))
			BeforeNEW, AfterNEW = beforeDATE.strftime('%d.%m.%Y'), afterDATE.strftime('%d.%m.%Y')
			addDir({'mode': 'listVideos', 'url': BASE_URL+RIGHT, 'category': CATEGORY}, create_entries({'Title': translation(30839).format(AfterNEW)}))
			addDir({'mode': 'listVideos', 'url': BASE_URL+LEFT, 'category': CATEGORY}, create_entries({'Title': translation(30840).format(BeforeNEW)}))
		except: pass
	if int(POS) > int(PAGE) and CATEGORY != 'PREVIEWS':
		debug_MS(f"(navigator.listVideos[4]) NEXTPAGES ### Now show NextPage ... No.{int(PAGE)+1} ... ###")
		FETCH_DUE = create_entries({'Title': translation(30841).format(int(PAGE)+1), 'Image': f"{artpic}nextpage.png"})
		addDir({'mode': 'listVideos', 'url': TARGET, 'page': int(PAGE)+1, 'position': int(POS), 'category': CATEGORY}, FETCH_DUE)
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listSubstances(MURLS):
	debug_MS("(navigator.listSubstances) -------------------------------------------------- START = listSubstances --------------------------------------------------")
	COMBI_DETAILS, COMBI_THIRD = ([] for _ in range(2))
	COMBI_DETAILS = getMultiData(MURLS)
	if COMBI_DETAILS:
		#log("++++++++++++++++++++++++")
		#log(f"(navigator.llistSubstances[2]) XXXXX CONTENT-02 : {COMBI_DETAILS} XXXXX")
		debug_MS("*****************************************")
		for number, CATEGORY_2, ORLINK_2, WFLINK_2, elem in COMBI_DETAILS:
			if elem is not None:
				RATING_2, (TRAILER_2, WORKS_2) = None, (False for _ in range(2))
				GENRE_2, DIRECTOR_2, WRITER_2, STAFF_2, COUNTRY_2 = ([] for _ in range(5))
				details = re.findall(r'''<main id=["']content-layout["'] class=["'](?:row )?content-layout entity (?:movie|series) cf(.*?)<section class=["']js-outbrain section(?: )?["']>''', elem, re.S)
				for item in details:
					item = re.sub(r'</?strong>', ' ', item)
					debug_MS(f"(navigator.listSubstances[2]) xxxxx ITEM-02 : {item} xxxxx")
					SECTOR_1 = re.compile(r'''class=["']card entity-card entity-card-list cf(.+?)</figure>''', re.S).findall(item) # Grab - Title + Link + Photo
					matchL1 = re.compile(r'''class=["']thumbnail-container thumbnail-link["'] href=["']([^"']+)["'] title=["'](.+?)["']>''', re.S).findall(SECTOR_1[0]) if SECTOR_1 else None # Grab - Link
					matchL2 = re.compile(r'''class=["']ACr([^ "']+) thumbnail-container thumbnail-link["'] title=["'](.+?)["']>''', re.S).findall(SECTOR_1[0]) if SECTOR_1 else None # Grab - Link
					ORLINK_3 = BASE_URL+matchL1[0][0] if matchL1 else BASE_URL+convert64(matchL2[0][0]) if matchL2 else None
					NAME_2 = cleaning(matchL1[0][1]) if matchL1 else cleaning(matchL2[0][1]) if matchL2 else None
					IMAGE_2 = re.compile(r'''class=["']thumbnail-img["'] (?:.*?data-)?src=["'](https?://.+?[a-z0-9]+(?:\.png|\.jpg|\.jpeg|\.jfif|\.gif))["'?]''', re.S).findall(SECTOR_1[0]) if SECTOR_1 else None
					THUMB_2 = enlargeIMG(IMAGE_2[0]) if IMAGE_2 and not 'empty/' in IMAGE_2[0] else None
					SECTOR_2 = re.compile(r'''<div class=["']meta-body-item meta-body-info(.+?)</div>''', re.S).findall(item) # Grab - Genres
					if '<span class="spacer">' in item:
						SECTOR_2 = re.compile(r'''<span class=["']spacer["']>(.+?)<div class=["']meta-body-item(?: meta-body-direction)?''', re.S).findall(item) # Grab - Genres
					matchGEN = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(SECTOR_2[0]) if SECTOR_2 else []
					GENRE_2 = ' / '.join(sorted([cleaning(gens, True) for gens in matchGEN])) if matchGEN else [] # Drama, Familie, Komödie
					matchORG = re.compile(r'''<span class=["']light["']>Originaltitel(.+?)</div>''', re.S).findall(item) # Grab - Originaltitle
					ORIGINAL_2 = cleaning(matchORG[0], True) if matchORG else None # World on Fire
					SECTOR_3 = re.compile(r'''<span class=["']light["']>Regie(.+?)</div>''', re.S).findall(item) # Grab - Directors
					matchDIR = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_3[0]) if SECTOR_3 else []
					DIRECTOR_2 = ', '.join([cleaning(dirs, True) for dirs in matchDIR]) if matchDIR else [] # Steven Seagal
					SECTOR_4 = re.compile(r'''<span class=["']light["']>(?:Drehbuch|Creator)(.+?)</div>''', re.S).findall(item) # Grab - Writers
					matchCREA = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_4[0]) if SECTOR_4 else []
					WRITER_2 = ', '.join([cleaning(creas, True) for creas in matchCREA]) if matchCREA else [] # Ed Horowitz, Robin U. Russin
					SECTOR_5 = re.compile(r'''<span class=["']light["']>Besetzung(.+?)</div>''', re.S).findall(item) # Grab - Casts
					matchACT = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_5[0]) if SECTOR_5 else []
					STAFF_2 = ','.join([cleaning(stars, True) for stars in matchACT]) if matchACT and len(matchACT) > 0 else []
					SECTOR_6 = re.compile(r'''<span class=["'](?:what )?light["']>Produktions(?:land|länder)(.+?)</div>''', re.S).findall(elem) # Grab - Countries
					matchCOU = re.compile(r'''<span class=["']ACr.*?nationality["']>(.+?)</span>''', re.S).findall(SECTOR_6[0]) if SECTOR_6 else None
					if ORLINK_3 and ('/serien' in ORLINK_3 or matchCOU is None):
						SECTOR_7 = re.compile(r'''<span class=["'](?:what )?light["']>Produktions(?:land|länder)(.+?)</div>''', re.S).findall(item) # Grab - Countries
						matchCOU = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(SECTOR_7[0]) if SECTOR_7 else None
					COUNTRY_2 = ', '.join(sorted([cleaning(cous, True) for cous in matchCOU])) if matchCOU else [] # Deutschland
					matchAGE = re.compile(r'''<span class=["']certificate-text(?: )?["']>(.+?)</span>''', re.S).findall(item) # Grab - Mpaa
					MPAA_2 = cleaning(matchAGE[0]) if matchAGE else None # FSK ab 18
					matchPLOT = re.compile(r'''<div class=["']content-txt(?: )?["']>(.+?)</div>''', re.S).findall(item) # Grab - Plot
					DESC_2 = cleaning(matchPLOT[0], True) if matchPLOT else ""
					SECTOR_8 = re.compile(r'''class=["']stats-numbers-row stats-numbers-seriespage(.+?)class=["']end-section-link-container''', re.S).findall(item) # Grab - Seasons + Episodes
					matchSEA = re.compile(r'''<div class=["']stats-item(?: )?["']>(.+?)</div>''', re.S).findall(SECTOR_8[0]) if SECTOR_8 else []
					SEASON_2 = ' • '.join([cleaning(seas) for seas in matchSEA]) if matchSEA else [] # 20 Staffeln • 420 Episoden
					matchDAT = re.compile(r'''<span class=["'](?:ACr.*?)?date(?: blue-link| )?["']>(.+?)</span>''', re.S).findall(item) # Grab - Date
					if ORLINK_3 and ('/serien' in ORLINK_3 or not matchDAT):
						matchDAT = re.compile(r'''<div class=["']meta-body-item meta-body-info["']>(.+?)<span class=["']spacer["']>''', re.S).findall(item) # Grab - Date
					DATE_2 = cleaning(re.sub(r'\n|\<.*?\>|Im Kino|als VoD', '', matchDAT[0])) if matchDAT and len(matchDAT[0]) > 0 else None # 20. Februar 2024 auf Amazon
					try:
						SECTOR_9 = (item[item.find('User-Wertung')+1:] or item[item.find('Pressekritiken')+1:]) # Grab - Rating
						RATING_2 = re.compile(r'''class=["']stareval-note["']>([^<]+)</span>''', re.S).findall(SECTOR_9)[0].strip().replace(',', '.') # 2,5
					except: pass
					SECTOR_10 = re.compile(r'''class=["']card video-card video-card-col(.+?)</section>''', re.S).findall(item) # Grab - Videos
					matchTR1 = re.compile(r'''<span class=["']ACr([^ "']+) meta-title-link["']>([^<]+)</span>''', re.S).findall(SECTOR_10[0]) if SECTOR_10 else [] # <span class="ACrL2tACryaXRpa2VuLzMwODMxNi90cmFpbGVyLzE5NTk0NjgxLmh0bWw= meta-title-link">
					matchTR2 = re.compile(r'''class=["']meta-title-link["'] href=["']([^"']+)["']>([^<]+)</a>''', re.S).findall(SECTOR_10[0]) if SECTOR_10 else [] # <a class="meta-title-link" href="/kritiken/308316/trailer/19594681.html">
					if CATEGORY_2 != 'ARCHIVES':
						TRAILER_2 = BASE_URL+convert64(matchTR1[0][0]) if matchTR1 else BASE_URL+matchTR2[0][0] if matchTR2 else False
					NEW_TITLE = cleaning(matchTR1[0][1]) if matchTR1 else cleaning(matchTR2[0][1]) if matchTR2 else NAME_2
					TITLE_2 = f"{NAME_2} - {NEW_TITLE}" if not NAME_2 in NEW_TITLE else NEW_TITLE
					WORKS_2 = True if TRAILER_2 and any(rai in TRAILER_2 for rai in ['teaser', 'trailer', 'videos']) else False
					matchDUR = re.compile(r'''class=["']thumbnail-count["']>([^<]+)</span>''', re.S).findall(SECTOR_10[0]) if SECTOR_10 else [] # Grab - Duration
					DURATION_2 = get_RunTime(matchDUR[0]) if matchDUR and len(matchDUR[0]) > 0 else None # 1:55
					COMBI_THIRD.append([int(number), CATEGORY_2, ORLINK_2, ORLINK_3, TITLE_2, THUMB_2, GENRE_2, ORIGINAL_2, DIRECTOR_2, WRITER_2, STAFF_2, COUNTRY_2, MPAA_2, DESC_2, SEASON_2, DATE_2, RATING_2, DURATION_2, WORKS_2, TRAILER_2])
	return COMBI_THIRD

def playCODE(SOURCE):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### TRAILER_SOURCE : {SOURCE} ###")
	TRAILER_LINK, FINAL_URL = (False for _ in range(2))
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	for elem in preserve(WORKS_FILE):
		if elem['filter'] != '00' and elem['filter'] == SOURCE:
			TRAILER_LINK, CLEAR_TITLE, PHOTO, GENRE = elem['filter'], elem['name'], elem['photo'], elem['genre']
			debug_MS(f"(navigator.playCODE[1]) ### WORKS_FILE-Line : {elem} ###")
	if TRAILER_LINK:
		DATA_ONE = getContent(TRAILER_LINK, REF=f"{BASE_URL}/")
		EXTRACTION = re.compile(r'''(?:class=["']player  js-player["']|class=["']player player-auto-play js-player["']|<div id=["']btn-export-player["'].*?) data-model=["'](.+?),&quot;disablePostroll&quot;''', re.S).findall(DATA_ONE)
		STREAM = EXTRACTION[0].replace('&quot;', '"')+'}' if EXTRACTION else None
		debug_MS(f"(navigator.playCODE[2]) +++ GET METADATA FOR STREAM : {STREAM} +++")
		if STREAM:
			DM_CODE = json.loads(STREAM)['videos'][0]['idDailymotion']
			debug_MS(f"(navigator.playCODE[3]) ~~~ EXTRACTION OF DAILYMOTION_CODE : {DM_CODE} ~~~")
			DATA_TWO = getContent(f"{API_DAILY}{DM_CODE}", queries='JSON', ORI=BASE_DAILY, REF=f"{BASE_DAILY}/", timeout=20)
			FINAL_URL = DATA_TWO['qualities']['auto'][0]['url']
	if FINAL_URL:
		LPM = xbmcgui.ListItem(CLEAR_TITLE, path=FINAL_URL, offscreen=True)
		LPM.setMimeType('application/vnd.apple.mpegurl')
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive') and '.m3u8' in FINAL_URL:
			IA_NAME = 'inputstream.adaptive'
			IA_VERSION = re.sub(r'(~[a-z]+(?:.[0-9]+)?|\+[a-z]+(?:.[0-9]+)?$|[.^]+)', '', xbmcaddon.Addon(IA_NAME).getAddonInfo('version'))[:4]
			LPM.setContentLookup(False), LPM.setProperty('inputstream', IA_NAME)
			if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
				LPM.setProperty(f"{IA_NAME}.manifest_type", STREAM.lower())
			if KODI_ov20:
				LPM.setProperty(f"{IA_NAME}.manifest_headers", f"User-Agent={get_userAgent()}") # On KODI v20 and above
			else: LPM.setProperty(f"{IA_NAME}.stream_headers", f"User-Agent={get_userAgent()}") # On KODI v19 and below
			if int(IA_VERSION) >= 2150:
				LPM.setProperty(f"{IA_NAME}.drm_legacy", 'org.w3.clearkey')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LPM)
		log(f"(navigator.playCODE) HLS_stream : {FINAL_URL}")
	else:
		failing(f"(navigator.playCODE[3]) ##### Die angeforderte Video-Url wurde NICHT gefunden !!! #####\n ##### URL : {SOURCE} #####")
		return dialog.notification(translation(30521).format('PLAY'), translation(30527), icon, 8000)

def addDir(params, listitem, folder=True, higher=False):
	uws, entries = build_mass(params), []
	listitem.setPath(uws)
	if enableBACK and PLACEMENT == 1 and higher is True:
		entries.append([translation(30650), f"RunPlugin({build_mass({'mode': 'callingMain'})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
