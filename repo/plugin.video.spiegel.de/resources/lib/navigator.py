# -*- coding: utf-8 -*-

from .common import *
from .external.scrapetube import *


def mainMenu():
	for TITLE, IMG, PATH in [(30601, 'uebersicht', {'mode': 'listArticles', 'url': f"{BASE_URL}video/", 'limit': '2'}), (30602, 'thema', {'mode': 'listSpiegelTV'}),
		(30603, 'panorama', {'mode': 'listArticles', 'url': f"{BASE_URL}panorama/", 'limit': '20'}), (30604, 'ausland', {'mode': 'listArticles', 'url': f"{BASE_URL}ausland/", 'limit': '20'}),
		(30605, 'ukraine', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/russlands-krieg-gegen-die-ukraine-videos/", 'limit': '-3'}),
		(30606, 'deutschland', {'mode': 'listArticles', 'url': f"{BASE_URL}politik/deutschland/", 'limit': '10'}),
		(30607, 'talk', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spitzengespraech-der-talk-mit-markus-feldenkirchen/", 'limit': '-3'}),
		(30608, 'bestseller', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-bestseller-mehr-lesen-mit-elke-heidenreich/"}),
		(30609, 'autotests', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/auto-tests-im-video/", 'limit': '-3'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}{IMG}.png"}))
	if enableYOUTUBE:
		addDir({'mode': 'listPlaylists'}, create_entries({'Title': translation(30610), 'Image': f"{artpic}youtube.png"}))
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30611), 'Image': f"{artpic}settings.png"}), folder=False)
		if enableINPUTSTREAM and plugin_operate('inputstream.adaptive'):
			addDir({'mode': 'iConfigs'}, create_entries({'Title': translation(30612), 'Image': f"{artpic}settings.png"}), folder=False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSpiegelTV():
	for TITLE, IMG, PATH in [(30621, 'magazin', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'limit': '-4'}),
		(30622, 'reportage', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_reportage'}),
		(30623, 'arte', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_für_arte_re:'}),
		(30624, 'geld', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'reden_wir_über_geld'}),
		(30625, 'crime', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_true_crime'}),
		(30626, 'verhoer', {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'im_verhör'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{genpic}{IMG}.png"}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listArticles(TARGET, ADDITION, EXTRA):
	debug_MS("(navigator.listArticles) -------------------------------------------------- START = listArticles --------------------------------------------------")
	debug_MS(f"(navigator.listArticles) ### URL = {TARGET} ### PAGINATION = {PAGINATION} ### ADDITION = {ADDITION} ### EXTRA = {EXTRA} ###")
	COMBI_PAGES, COMBI_ARTICLES, COMBI_LINKS, COMBI_MEDIA, COMBI_FIRST, COMBI_SECOND, COMBI_THIRD, COMBI_FOURTH = ([] for _ in range(8))
	counter, UNIKAT, (RESULT_ONE, RESULT_TWO) = 0, set(), (None for _ in range(2))
	AMOUNT_PAGES = 2 if EXTRA != 'DEFAULT' else PAGINATION+int(ADDITION)
	for ii in range(1, AMOUNT_PAGES, 1):
		WLINK_1 = f"{TARGET}p{str(ii)}/" if int(ii) > 1 else TARGET
		debug_MS(f"(navigator.listArticles[1]) THEME-PAGES XXX POS = {str(ii)} || URL = {WLINK_1} XXX")
		COMBI_PAGES.append([int(ii), 'THEME', WLINK_1, WLINK_1])
	if COMBI_PAGES:
		COMBI_ARTICLES = getMultiData(COMBI_PAGES)
		if COMBI_ARTICLES:
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listArticles[2]) XXXXX COMBI_ARTICLES-02 : {COMBI_ARTICLES} XXXXX")
			debug_MS("------------------------------------------------")
			for num, THEME_2, WLINK_2, DDURL_2, item in sorted(COMBI_ARTICLES, key=lambda asx: int(asx[0])):
				if item is not None:
					results = []
					if EXTRA != 'DEFAULT':
						results += re.findall(r'<section class="relative flex flex-wrap w-full" data-size="full" (?:data-last="true" )?data-area="block>topic:{}"(.+?)(?:<section class="relative flex flex-wrap w-full"|data-area="article-teaser-list")'.format(EXTRA), item, re.S)
					else:
						results += re.findall(r'<section class="relative flex flex-wrap w-full" data-size="full" data-first="true" data-area="block>topic(.+?)<section class="relative flex flex-wrap w-full"', item, re.S)
						results += re.findall(r'data-area="article-teaser-list"(.+?)data-area="pagination-bar"', item, re.S)
					for chtml in results:
						articles = re.findall(r'data-block-el="articleTeaser"(.+?)</article>', chtml, re.S)
						for entry in articles:
							entry, markID_1 = entry.replace('&#34;', '"'), '00'
							(NAV_1, THUMB_1, TAGLINE_1, META_1, AIRED_1, JSURL_1), (DESC_1, PLAY_1) = (None for _ in range(6)), ("" for _ in range(2))
							debug_MS(f"(navigator.listArticles[2]) xxxxx ENTRY-02 : {entry} xxxxx")
							NAME = re.compile(r'<article aria-label="(.+?)" (?:data-|class=)', re.S).findall(entry)[0]
							TITLE_1 = cleaning(NAME)
							STREAM = re.compile('<a href="([^"]+?)" target=', re.S).findall(entry)
							if STREAM: NAV_1 = STREAM[0]
							if NAV_1 is None or NAV_1 in UNIKAT:
								continue
							UNIKAT.add(NAV_1)
							# <img data-image-el="img" class="block lazyload h-full mx-auto" src= || <img data-video-el="poster" class="block lazyload h-full mx-auto" src=
							IMG = re.compile('<img data-(?:image|video)-el=".*?src="(https://cdn.prod.www.spiegel.de/images[^"]+?)"', re.S).findall(entry)
							THUMB_1 = IMG[-1].replace('_w288_r1.778_', '_w1200_r1.778_').replace('_w300_r1.778_', '_w1200_r1.778_').replace('_w488_r1.778_', '_w1200_r1.778_') if IMG else None
							THUMB_1 = f"{THUMB_1.split('_fd')[0]}.jpg" if THUMB_1 and '_fd' in THUMB_1 else THUMB_1
							# <span class="mb-4 block text-primary-base dark:text-dm-primary-base focus:text-primary-darker hover:text-primary-dark font-sansUI font-bold text-base" data-target-teaser-el="topMark">
							TAG_1 = re.compile(r'data-target-teaser-el="topMark">([^<]+?)</', re.S).findall(entry)
							TAGLINE_1 = cleaning(TAG_1[0]).replace('\n',' ').replace('\t',' ') if TAG_1 else None # Lauterbach und das Scholz-Team
							# <span class="font-sansUI font-normal text-s text-shade-dark dark:text-shade-light" data-target-teaser-el="meta">
							STORY_1 = re.compile(r'data-target-teaser-el="meta">([^<]+?)</', re.S).findall(entry) # Ein Video von Janita Hämäläinen
							STORY_2 = re.compile(r'<span data-auxiliary>(.+?Uhr)</', re.S).findall(entry) # 9. September 2023, 13.37 Uhr
							if STORY_1 and not 'spitzengespraech' in WLINK_2:
								META_1 = cleaning(re.sub(r'\<.*?\>', '', STORY_1[0]))
							if STORY_2 and ' Uhr' in STORY_2[0]:
								try: 
									broadcast = cleaning(STORY_2[0])
									for dt in (('Januar', 'Jan'), ('Februar', 'Feb'), ('März', 'Mar'), ('April', 'Apr'), ('Mai', 'May'), ('Juni', 'Jun'), ('Juli', 'Jul'),
										 ('August', 'Aug'), ('September', 'Sep'), ('Oktober', 'Oct'),('November', 'Nov'), ('Dezember', 'Dec')): broadcast = broadcast.replace(*dt)
									converted = datetime(*(time.strptime(broadcast, '%d. %b %Y, %H.%M Uhr')[0:6])) # 9. September 2023, 13.37 Uhr
									AIRED_1 = converted.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('.', '•', ':')
								except: pass
							# <span class="font-serifUI font-normal text-base leading-loose mr-6" data-target-teaser-el="text">
							STORY_3 = re.compile(r'data-target-teaser-el="text">(.+?)</', re.S).findall(entry) # Beschreibung long
							if STORY_3: DESC_1 = cleaning(re.sub(r'\<.*?\>', '', STORY_3[0]))
							# </svg>\n</span>\n<span class="text-white dark:text-shade-lightest font-sansUI text-s font-bold">27:09</span>\n</span> || </svg>\n</span>\n<span>7 Min</span>\n</span>
							DUR_1 = re.compile('</svg>\s*</span>\s*<spa.+?>([^<]+?)</span>\s*</span>', re.S).findall(entry)
							DURATION_1 = get_RunTime(DUR_1[0].strip()) if DUR_1 else 0
							if re.search(r'data-contains-flags="Spplus-paid"', entry): continue # SpiegelPlus-Beitrag nur mit ABO abrufbar
							elif re.search(r'<span data-icon-auxiliary="Video"', entry):
								JWID_1 = re.compile('data-component="Video" data-settings=.*?,"(?:jwplayerMedia|media)Id":"(.+?)",', re.S).findall(entry)
								JSURL_1 = f"https://vcdn02.spiegel.de/v2/media/{JWID_1[0]}?poster_width=1280&sources=hls,dash,mp4" if JWID_1 else None
								PLAY_1, markID_1 = 'VIDEO', JWID_1[0] if JWID_1 else '00'
							elif re.search(r'<span data-icon-auxiliary="Audio"', entry):
								if not enableAUDIO: continue # Audioeinträge ausblenden wenn Audio in den Settings ausgeschaltet ist 
								PLAY_1, markID_1 = 'AUDIO', '00'
							else: continue # KEIN Playsymbol (Audio/Video) im THUMB gefunden !!!
							counter += 1
							COMBI_FIRST.append([int(counter), PLAY_1, markID_1, TITLE_1, THUMB_1, NAV_1, META_1, AIRED_1, DESC_1, DURATION_1, TAGLINE_1])
							if JSURL_1 is None and NAV_1:
								COMBI_LINKS.append([int(counter), PLAY_1, NAV_1, NAV_1])
							elif JSURL_1 and NAV_1:
								COMBI_MEDIA.append([int(counter), PLAY_1, NAV_1, JSURL_1])
	if COMBI_FIRST:
		COMBI_SECOND = listSubstances(COMBI_LINKS)
		RESULT_ONE = [a + b for a in COMBI_FIRST for b in COMBI_SECOND if a[5] == b[2]] # Zusammenführung von Liste1 und Liste2 - wenn der LINK überein stimmt !!!
		RESULT_ONE += [c for c in COMBI_FIRST if all(d[2] != c[5] for d in COMBI_SECOND)] # Der übriggebliebene Rest von Liste1 - wenn der LINK nicht in der Liste2 vorkommt !!!
	if COMBI_SECOND or COMBI_MEDIA:
		COMBI_THIRD = getMultiData(COMBI_SECOND+COMBI_MEDIA, queries='JSON')
		if COMBI_THIRD:
			DATA_TWO = json.loads(COMBI_THIRD)
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listArticles[4]) XXXXX DATA_TWO-04 : {DATA_TWO} XXXXX")
			#log("++++++++++++++++++++++++")
			for elem in DATA_TWO:
				if elem is not None and (('playlist' in elem and elem.get('playlist', [])[0]) or (elem.get('Slug', ''))):
					THUMB_2, AIRED_2, BEGINS_2 = (None for _ in range(3))
					POS_2, PLAY_2, NAV_2, DEM_2= elem['Position'], elem['PlayForm'], elem['NaviLink'], elem['Demand']
					SHORT = elem['playlist'][0] if 'playlist' in elem and len(elem.get('playlist', [])[0]) > 0 else elem
					SECTION = {k:v for k,v in SHORT.items() if k[:6] not in ['jwpseg', 'AdMark']}
					debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
					debug_MS(f"(navigator.DetailDescription[4]) ### POS : {POS_2} || PLAY : {PLAY_2} || DEMAND : {DEM_2} || ELEM-04 : {SECTION} ###")
					markID_2 = SHORT['mediaid'] if SHORT.get('mediaid', '') else SHORT['Id'] if SHORT.get('Id', '') else 'Unknown-ID'
					TITLE_2 = (cleaning(SHORT.get('title')) or cleaning(SHORT.get('Title')))
					THUMB_2 = SHORT.get('image', None)
					if THUMB_2 is None and SHORT.get('images', '') and len(SHORT['images']) > 0:
						THUMB_2 = [vid.get('src', []) for vid in SHORT.get('images', {}) if vid.get('type')[:5] == 'image'][-1]
					PUBLISHED = (SHORT.get('pubdate', None) or SHORT.get('PublishedUtc', None))
					if PUBLISHED and str(PUBLISHED).isdecimal():
						LOCALstart = get_CentralTime(datetime(1970, 1, 1) + timedelta(seconds=PUBLISHED))
						AIRED_2 = LOCALstart.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('-', '•', ':')
						BEGINS_2 = LOCALstart.strftime('%Y-%m-%dT%H:%M') if KODI_ov20 else LOCALstart.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
					elif PUBLISHED and not str(PUBLISHED).isdecimal():
						LOCALstart = get_CentralTime(PUBLISHED, 'DATETIME')
						AIRED_2 = LOCALstart.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('-', '•', ':')
						BEGINS_2 = LOCALstart.strftime('%Y-%m-%dT%H:%M') if KODI_ov20 else LOCALstart.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
					DESC_2 = (cleaning(SHORT.get('description', '')) or cleaning(SHORT.get('Description', '')))
					DURATION_2 = (SHORT.get('duration', 0) or SHORT.get('DurationSeconds', 0))
					if DURATION_2 != 0: DURATION_2 = "{0:.0f}".format(DURATION_2)
					COMBI_FOURTH.append([int(POS_2), markID_2, TITLE_2, THUMB_2, NAV_2, BEGINS_2, AIRED_2, DESC_2, DURATION_2])
	if COMBI_FOURTH or RESULT_ONE:
		RESULT_TWO = [e + f for e in RESULT_ONE for f in COMBI_FOURTH if e[5] == f[4]] # Zusammenführung von Liste1 und Liste2 - wenn der LINK überein stimmt !!!
		#log("++++++++++++++++++++++++")
		#log(f"(navigator.listArticles[5]) XXXXX RESULT_TWO-05 : {RESULT_TWO} XXXXX")
		for xev in sorted(RESULT_TWO, key=lambda csx: int(csx[0])): # Liste1 = 0-14 oder 0-10|| Liste2 = 15-23 oder 11-19
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listResults[5]) ### Anzahl : {len(xev)} || Eintrag : {xev} ###")
			(aired, year), (STARTING, Note_1, Note_2, Note_3, Note_4, Note_5) = (None for _ in range(2)), ("" for _ in range(6))
			if len(xev) > 20: ### Liste1+Liste2 ist grösser als Nummer:20 ###
				'''
				Liste-1_SHORT = num1, form1, mediaId1, title1, thumb1, link1, meta1, aired1, desc1, duration1, tagline1 = xev[0], xev[1], xev[2], xev[3], xev[4], xev[5], xev[6], xev[7], xev[8], xev[9], xev[10]
				Liste-2_SHORT = num3, mediaId2, title2, thumb2, link2, begins, aired2, desc2, duration2 = xev[11], xev[12], xev[13], xev[14], xev[15], xev[16], xev[17], xev[18], xev[19]
				Liste-1_LONG = num1, form1, mediaId1, title1, thumb1, link1, meta1, aired1, desc1, duration1, tagline1, num3, form3, link3, mediaId3 = xev[0], xev[1], xev[2], xev[3], xev[4], xev[5], xev[6], xev[7], xev[8], xev[9], xev[10], xev[11], xev[12], xev[13], xev[14]
				Liste-2_LONG = num3, mediaId2, title2, thumb2, link2, begins, aired2, desc2, duration2 = xev[15], xev[16], xev[17], xev[18], xev[19], xev[20], xev[21], xev[22], xev[23]
				'''
				Form1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = xev[1], xev[3], xev[4], xev[6], xev[7], xev[8], xev[9], xev[10]
				episID, Thumb2, begins, Aired2, Desc2, Duration2 = xev[16], xev[18], xev[20], xev[21], xev[22], xev[23]
			elif 16 <= len(xev) <= 20: ### Liste1+Liste2 liegt zwischen Nummer:16-20 ###
				Form1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = xev[1], xev[3], xev[4], xev[6], xev[7], xev[8], xev[9], xev[10]
				episID, Thumb2, begins, Aired2, Desc2, Duration2 = xev[12], xev[14], xev[16], xev[17], xev[18], xev[19]
			elif 12 <= len(xev) <= 15: ### Liste1 liegt zwischen Nummer:12-15 und Liste2 ist AUS ###
				Form1, Media1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline, Form2, Media2 = xev[1], xev[2], xev[3], xev[4], xev[6], xev[7], xev[8], xev[9], xev[10], xev[12], xev[14]
				episID = Media1 if Media1 != '00' else Media2.split('media/')[1].split('?poster')[0] if 'media/' in Media2 else Media2.split('clips/')[1]
				Thumb2, begins, Aired2, Desc2, Duration2 = None, None, None, "", 0
			elif len(xev) <= 11: ### Liste1 ist kleiner als Nummer:12 und Liste2 ist AUS ###
				Form1, episID, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = xev[1], xev[2], xev[3], xev[4], xev[6], xev[7], xev[8], xev[9], xev[10]
				Thumb2, begins, Aired2, Desc2, Duration2 = None, None, None, "", 0
			duration = Duration2 if Duration2 != 0 else Duration1 if Duration1 != 0 else 0
			image = Thumb2 if Thumb2 else Thumb1 if Thumb1 else None
			Note_1 = translation(30641).format(producer) if producer else ""
			if Aired1 or Aired2:
				STARTING = Aired2 if 16 <= len(xev) <= 24 and Aired2 else Aired1
				Note_2 = translation(30642).format(STARTING) if Form1 == 'AUDIO' else translation(30643).format(STARTING)
				aired, year = STARTING[0:10].replace('-', '.'), STARTING[6:10]
			Note_3 = '[CR]' if Note_1 != "" or Note_2 != "" else ""
			Note_4 = Desc2 if 16 <= len(xev) <= 24 and len(Desc2) > len(Desc1) else Desc1
			Note_5 = '[COLOR magenta] ♫[/COLOR]' if Form1 == 'AUDIO' else ""
			plot = Note_1+Note_2+Note_3+Note_4
			name = title+Note_5
			debug_MS(f"(navigator.listResults[5]) ##### POS : {xev[0]} || NAME : {name} || mediaID : {episID} || TIME : {STARTING} || BEGINS : {begins} #####")
			debug_MS(f"(navigator.listResults[5]) ##### TAGLINE : {tagline} || DURATION : {duration} || THUMB : {image} #####")
			for method in getSorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			FETCH_UNO = create_entries({'Title': name, 'Tagline': tagline, 'Plot': plot, 'Duration': duration, \
				'Date': begins, 'Aired': aired, 'Year': year, 'Genre': 'News', 'Mediatype': 'movie', 'Image': image, 'Reference': 'Single'})
			addDir({'mode': 'playMedia', 'url': episID}, FETCH_UNO, folder=False)
	else:
		debug_MS(f'(navigator.listArticles[4]) ##### NO ARTICLES-LIST - NO ENTRY FOR THIS: "{TARGET}" FOUND #####')
		return dialog.notification(translation(30521).format('ARTICLE'), translation(30523).format(TARGET), icon, 10000)
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSubstances(MURLS):
	COMBI_DETAILS, OUTPUTS = ([] for _ in range(2))
	COMBI_DETAILS = getMultiData(MURLS)
	if COMBI_DETAILS:
		for num, PLAY_3, WLINK_3, DDURL_3, each in COMBI_DETAILS:
			if each is not None:
				AREA, DATA_2, JSURL_2 = (None for _ in range(3))
				if PLAY_3 == 'VIDEO':
					AREA = re.compile(r'<div data-area="presentation_element>video">(.+?)data-sara-component=', re.S).findall(each)
					JWID_2 = re.compile('"(?:jwplayerMedia|media)Id":"([^"]+?)",', re.S).findall(AREA[0].replace('&#34;', '"')) if AREA else None
					JSURL_2 = f"https://vcdn02.spiegel.de/v2/media/{JWID_2[0]}?poster_width=1280&sources=hls,dash,mp4" if JWID_2 else None
				elif PLAY_3 == 'AUDIO':
					AREA = re.compile(r'(?:<div data-area="presentation_element>podlove">|<aside aria-label="Artikel zum Hören")(.+?)(?:data-sara-component=|data-area="playlist_button")', re.S).findall(each)
					JWID_2 = re.compile('x-audio-omny="([^"]+?)"', re.S).findall(AREA[0]) if AREA else None
					DATA_2 = base64.b64decode(JWID_2[0]) if JWID_2 else None
					CLIP_2 = re.compile('"omnystudioClipId":"([^"]+?)",', re.S).findall(py3_dec(DATA_2).replace('&#34;', '"')) if DATA_2 else None
					JSURL_2 = f"https://omny.fm/api/orgs/{COMPANY_ID}/clips/{CLIP_2[0]}" if CLIP_2 else None
				CONTENT = AREA[0].replace('&#34;', '"') if AREA else 'EntryNotFound'
				debug_MS(f"(navigator.listSubstances[3]) ### POS : {num} || PLAY : {PLAY_3} || EACH-03 : {CONTENT} ###")
				if JSURL_2 and DDURL_3:
					OUTPUTS.append([int(num), PLAY_3, WLINK_3, JSURL_2])
	return OUTPUTS

def listPlaylists():
	debug_MS("(navigator.listPlaylists) ------------------------------------------------ START = listPlaylists -----------------------------------------------")
	addDir({'url': BASE_YT.format(CHANNEL_CODE, 'UU1w6pNGiiLdZgyNpXUnA4Zw'), 'extras': 'YT_FOLDER'}, create_entries({'Title': translation(30631), 'Plot': 'Neue Uploads: DER SPIEGEL'}))
	playlists = get_videos(f"https://www.youtube.com/{CHANNEL_NAME}/playlists", 'https://www.youtube.com/youtubei/v1/browse', 'contents', 'itemSectionRenderer', 100, 1) # mit "get_videos" die Playlisten eines Channels abrufen
	for each in playlists:
		for item in each['contents'][0]['gridRenderer'].get('items', []):
			if not item.get('lockupViewModel', ''): continue
			debug_MS(f"(navigator.listPlaylists[1]) xxxxx ENTRY-01 : {item} xxxxx")
			title = cleaning(item['lockupViewModel']['metadata']['lockupMetadataViewModel']['title']['content'])
			PYID = item['lockupViewModel']['contentId']
			photo = item['lockupViewModel']['contentImage']['collectionThumbnailViewModel']['primaryThumbnail']['thumbnailViewModel']['image']['sources'][0]['url'].split('?sqp=')[0].replace('hqdefault', 'maxresdefault')
			if title.lower().startswith(('rocker', 'jaafars', 'shortcut', 'spiegel tv vor 20', 'sport')):
				photo = item['lockupViewModel']['contentImage']['collectionThumbnailViewModel']['primaryThumbnail']['thumbnailViewModel']['image']['sources'][0]['url']
			try: numbers = re.sub(r'( episodes| videos)', '', item['lockupViewModel']['contentImage']['collectionThumbnailViewModel']['primaryThumbnail']['thumbnailViewModel']['overlays'][0]['thumbnailOverlayBadgeViewModel']['thumbnailBadges'][0]['thumbnailBadgeViewModel']['text'])
			except: numbers = None
			name = translation(30632).format(title) if numbers is None else translation(30633).format(title, numbers)
			FETCH_UNO = create_entries({'Title': name, 'Plot': 'Playlist: Offizieller YouTube Kanal von SPIEGEL TV und DER SPIEGEL', 'Image': photo})
			addDir({'url': BASE_YT.format(CHANNEL_CODE, PYID), 'extras': 'YT_FOLDER'}, FETCH_UNO)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playMedia(PLID):
	debug_MS("(navigator.playMedia) -------------------------------------------------- START = playMedia --------------------------------------------------")
	MEDIAS = [] # https://omny.fm/api/orgs/5ac1e950-45c7-4eb7-87c0-aa0f018441b8/clips/6a92c18a-3ce2-49a4-9c87-b01a0144dadc
	M3U8_FILE, STREAM, QUALITY, FINAL_URL = (False for _ in range(4)) # https://vcdn02.spiegel.de/v2/media/ed2L0yL7?sources=hls,dash,mp4
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	NEW_URL = f"https://vcdn02.spiegel.de/v2/media/{PLID}?sources=hls,dash,mp4" if len(PLID) < 18 else f"https://omny.fm/api/orgs/{COMPANY_ID}/clips/{PLID}"
	debug_MS(f"(navigator.playMedia) ### NEW_URL = {NEW_URL} ###")
	DATA = getContent(NEW_URL)
	if NEW_URL.startswith('https://vcdn02') and DATA.get('playlist', '') and DATA.get('playlist', {})[0].get('sources', ''):
		for source in DATA['playlist'][0]['sources']:
			TYPE = (source.get('type', 'UNKNOWN') or 'UNKNOWN')
			VIDEO = (source.get('file', None) or None)
			if TYPE.lower() in ['application/x-mpegurl', 'application/vnd.apple.mpegurl'] and VIDEO and 'm3u8' in VIDEO:
				M3U8_FILE = VIDEO
			if TYPE.lower() == 'video/mp4' and VIDEO and 'mp4' in VIDEO:
				HEIGHT = (source.get('height', 0) or 0)
				MEDIAS.append({'url': VIDEO, 'mimeType': TYPE.lower(), 'height': HEIGHT})
				MEDIAS = sorted(MEDIAS, key=lambda xs: int(xs['height']), reverse=True)
		if MEDIAS: debug_MS(f"(navigator.playMedia[1]) SORTED_LIST | MPP4 ### MEDIAS : {MEDIAS} ###")
		if (enableINPUTSTREAM or prefSTREAM == 0) and (M3U8_FILE or MEDIAS):
			STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
			if M3U8_FILE:
				MIME, QUALITY, FINAL_URL = 'application/vnd.apple.mpegurl', 'AUTO', M3U8_FILE
			elif MEDIAS and 'videos/' in MEDIAS[0]['url']: # https://vcdn02.spiegel.de/videos/n1QbH5SV-b8Tmknhy.mp4 // https://docs.jwplayer.com/platform/reference/get_manifests-media-id-manifest-extension
				MIME, QUALITY, FINAL_URL = 'application/vnd.apple.mpegurl', 'BUILD', f"https://vcdn02.spiegel.de/manifests/{MEDIAS[0]['url'].split('videos/')[1][:8]}.m3u8"
			if FINAL_URL: debug_MS(f"(navigator.playMedia[2]) ***** TAKE - {'Inputstream (hls)' if STREAM == 'HLS' else 'Standard (m3u8)'} - FILE *****")
		if not FINAL_URL and MEDIAS:
			for item in MEDIAS:
				if not enableINPUTSTREAM and prefSTREAM == 1 and item['height'] == prefQUALITY:
					debug_MS(f"(navigator.playMedia[3]) ***** TAKE - (mp4) - FILE : {item['url']} *****")
					STREAM, MIME, QUALITY, FINAL_URL = 'MP4', 'video/mp4', f"{str(item['height'])}p", item['url']
		if not FINAL_URL and MEDIAS:
			log("(navigator.playMedia[4]) !!!!! KEINEN passenden Stream gefunden --- nehme jetzt den Reserve-Stream-MP4 !!!!!")
			QUALITY = f"{str(MEDIAS[0]['height'])}p" if MEDIAS[0]['height'] != 0 else 'Unknown'
			STREAM, MIME, FINAL_URL = 'MP4', 'video/mp4', MEDIAS[0]['url']
	elif NEW_URL.startswith('https://omny.fm') and DATA.get('AudioUrl', ''):
		actual_time = int(round(time.time())) # UTC Datetime now
		debug_MS(f"(navigator.playMedia[1]) ***** TAKE - (mp3) - FILE : {DATA['AudioUrl']}?d={str(actual_time)}&utm_source=CustomPlayer1 *****")
		STREAM, MIME, QUALITY, FINAL_URL = 'MP3', 'audio/mp3', 'AUTO', f"{DATA['AudioUrl']}?d={str(actual_time)}&utm_source=CustomPlayer1"
	if FINAL_URL and STREAM:
		LSM = xbmcgui.ListItem(path=FINAL_URL, offscreen=True)
		LSM.setMimeType(MIME)
		if plugin_operate('inputstream.adaptive') and STREAM in ['HLS', 'MPD']:
			IA_NAME, IA_SYSTEM = 'inputstream.adaptive', 'com.widevine.alpha'
			IA_VERSION = re.sub(r'(~[a-z]+(?:.[0-9]+)?|\+[a-z]+(?:.[0-9]+)?$|[.^]+)', '', xbmcaddon.Addon(IA_NAME).getAddonInfo('version'))[:4]
			LSM.setContentLookup(False), LSM.setProperty('inputstream', IA_NAME)
			LSM.setProperty('inputstream', 'inputstream.adaptive')
			if KODI_un21:
				LSM.setProperty(f"{IA_NAME}.manifest_type", STREAM.lower()) # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
			if KODI_ov20:
				LSM.setProperty(f"{IA_NAME}.manifest_headers", f"User-Agent={get_userAgent()}") # On KODI v20 and above
			else: LSM.setProperty(f"{IA_NAME}.stream_headers", f"User-Agent={get_userAgent()}") # On KODI v19 and below
			if int(IA_VERSION) >= 2150:
				LSM.setProperty(f"{IA_NAME}.drm_legacy", 'org.w3.clearkey')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log(f"(navigator.playMedia) [{QUALITY}] {STREAM}_stream : {FINAL_URL} ")
	else:
		failing(f"(navigator.playMedia) ##### Abspielen des Streams NICHT möglich ##### URL : {NEW_URL} #####\n ########## KEINEN passenden Stream-Eintrag gefunden !!! ##########")
		return dialog.notification(translation(30521).format('STREAM'), translation(30527), icon, 8000)

def addDir(params, listitem, folder=True):
	if params.get('extras') == 'YT_FOLDER': uws = params.get('url')
	else: uws = build_mass(params)
	listitem.setPath(uws)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
