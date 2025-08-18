# -*- coding: utf-8 -*-

from .common import *
from .utilities import Transmission


def mainMenu():
	for TITLE, IMG, PATH in [(30601, 'deepsearch', {'mode': 'searchingDeezer'}), (30602, 'apple', {'mode': 'appleMain'}),
		(30603, 'beatport', {'mode': 'beatportMain'}), (30604, 'billboard', {'mode': 'billboardMain'}), (30605, 'ddp_home', {'mode': 'ddpMain'}),
		(30606, 'hypem', {'mode': 'hypemMain'}), (30607, 'official', {'mode': 'ocMain'}), (30608, 'shazam', {'mode': 'shazamMain'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}{IMG}.gif" if IMG == 'deepsearch' else f"{artpic}{IMG}.png"}))
	if enableADJUSTMENT:
		addDir({'mode': 'aConfigs'}, create_entries({'Title': translation(30610), 'Image': f"{artpic}settings.png"}), False)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def searchingDeezer():
	keyword, received = None, False
	keyword = dialog.input(translation(30621), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
	if keyword: keyword = quote_plus(keyword, safe='')
	else: return
	for item in [{'conv': 'strukturARTIST', 'name': 30622, 'turn': 'listDeezerSelection', 'slug': 'artist'},
		{'conv': 'strukturTRACK', 'name': 30623, 'turn': 'listDeezerVideos', 'slug': 'track'}, {'conv': 'strukturALBUM', 'name': 30624, 'turn': 'listDeezerSelection', 'slug': 'album'},
		{'conv': 'strukturPLAYLIST', 'name': 30625, 'turn': 'listDeezerSelection', 'slug': 'playlist'}, {'conv': 'strukturUSERLIST', 'name': 30626, 'turn': 'listDeezerSelection', 'slug': 'user'}]:
		item['conv'] = Transmission().retrieveContent(f"{BASE_URL_DZ}/{item['slug']}?q={keyword}&limit={deezerFoldersDisplay}&strict=on&output=json&index=0", REF='https://www.deezer.com/', AUTH='DEEZER')
		if item['slug'] == 'track' and item['conv']['total'] != 0:
			addDir({'mode': item['turn'], 'url': keyword, 'extras': item['slug'], 'transmit': icon}, create_entries({'Title': translation(item['name']), 'Image': f"{artpic}{item['slug']}.png"}), automatic=True)
			received = True
		elif item['slug'] in ['artist', 'album', 'playlist', 'user'] and item['conv']['total'] != 0:
			addDir({'mode': item['turn'], 'url': keyword, 'extras': item['slug']}, create_entries({'Title': translation(item['name']), 'Image': f"{artpic}{item['slug']}.png"}))
			received = True
	if not received:
		addDir({'mode': 'rootMain', 'url': keyword}, create_entries({'Title': translation(30627), 'Image': f"{artpic}noresults.png"}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDeezerSelection(url, EXTRA):
	musicVideos, UNIKAT = [], set()
	if url.startswith(BASE_URL_DZ):
		content = Transmission().retrieveContent(quote_plus(url, safe='/:?=&'), REF='https://www.deezer.com/', AUTH='DEEZER')
	else:
		content = Transmission().retrieveContent(f"{BASE_URL_DZ}/{EXTRA}?q={quote_plus(url)}&limit={deezerFoldersDisplay}&strict=on&output=json&index=0", REF='https://www.deezer.com/', AUTH='DEEZER')
	for item in content.get('data', []):
		artist = cleaning(item['artist']['name']) if EXTRA == 'album' else cleaning(item['name']) if EXTRA == 'artist' else TitleCase(cleaning(item['title'])) if EXTRA == 'playlist' else None
		album = cleaning(item['title']) if EXTRA == 'album' else None
		user = TitleCase(cleaning(item['user']['name'])) if EXTRA == 'playlist' else TitleCase(cleaning(item['name'])) if EXTRA == 'user' else None
		numbers = str(item['nb_tracks']) if EXTRA in ['album', 'playlist'] else str(item['nb_fan']) if EXTRA == 'artist' else None
		version = cleaning(item['record_type']).title() if EXTRA == 'album' else None
		try:
			thumb = item['picture_big'] if EXTRA in ['artist', 'playlist', 'user'] else item['cover_big']
			if EXTRA in ['artist', 'user'] and thumb.endswith(EXTRA+'//500x500-000000-80-0-0.jpg'):
				thumb = f"{artpic}noavatar.gif"
		except:
			thumb = f"{artpic}noavatar.gif" if EXTRA in ['artist', 'user'] else f"{artpic}noimage.png"
		if item.get('tracklist', '') and item['tracklist'].startswith('https://api.deezer.com/'):
			TRACKS_URL = f"{item['tracklist'].split('top?limit=')[0]}top?limit={deezerVideosDisplay}&index=0" if EXTRA == 'artist' else f"{item['tracklist']}?limit={deezerVideosDisplay}&index=0"
		else: TRACKS_URL = None
		special = f"{artist} - {album}" if EXTRA == 'album' else artist.strip().lower() if EXTRA == 'artist' else f"{artist} - {user}" if EXTRA == 'playlist' else user
		if TRACKS_URL is None or special in UNIKAT:
			continue
		UNIKAT.add(special)
		musicVideos.append([numbers, artist, album, user, version, TRACKS_URL, special, thumb])
	musicVideos = sorted(musicVideos, key=lambda mv: int(mv[0]), reverse=True) if EXTRA == 'artist' else musicVideos
	for numbers, artist, album, user, version, TRACKS_URL, special, thumb in musicVideos:
		if EXTRA == 'artist':
			name = translation(30628).format(artist, numbers) if showDETAILS else artist
			plot = f"Artist:  [B]{artist}[/B][CR]Fans:  [B][COLOR chartreuse]{numbers}[/COLOR][/B]"
		elif EXTRA == 'album':
			name = translation(30629).format(special, version, numbers) if showDETAILS else special
			plot = f"Artist:  [B]{artist}[/B][CR]Album:  [B][COLOR yellow]{album}[/COLOR][/B][CR]Version:  [B][COLOR deepskyblue]{version}[/COLOR][/B][CR]Tracks:  [B][COLOR FFFFA500]{numbers}[/COLOR][/B]"
		elif EXTRA == 'playlist':
			name = translation(30630).format(artist, user, numbers) if showDETAILS else artist
			plot = f"Artist:  [B]{artist}[/B][CR]User:  [B][COLOR chartreuse]{user}[/COLOR][/B][CR]Tracks:  [B][COLOR FFFFA500]{numbers}[/COLOR][/B]"
		elif EXTRA == 'user':
			name = user
			plot = f"User:  [B][COLOR chartreuse]{user}[/COLOR][/B]"
		addDir({'mode': 'listDeezerVideos', 'url': TRACKS_URL, 'extras': EXTRA, 'transmit': thumb}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot}), automatic=True)
	if musicVideos and content.get('next', '') and content['next'].startswith(BASE_URL_DZ):
		addDir({'mode': 'listDeezerSelection', 'url': content['next'], 'extras': EXTRA}, create_entries({'Title': translation(30802), 'Image': f"{artpic}nextpage.png"}))
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listDeezerVideos(url, TYPE, LIMIT, NUMBER, EXTRA, PHOTO):
	musicVideos, UNIKAT, NUMBER = [], set(), int(NUMBER)
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	if EXTRA == 'track' and not 'index=' in url:
		content = Transmission().retrieveContent(f"{BASE_URL_DZ}/{EXTRA}?q={quote_plus(url)}&limit={deezerVideosDisplay}&strict=on&output=json&index=0", REF='https://www.deezer.com/', AUTH='DEEZER')
	else:
		content = Transmission().retrieveContent(quote_plus(url, safe='/:?=&'), REF='https://www.deezer.com/', AUTH='DEEZER')
	for item in content.get('data', []):
		artist = cleaning(item['artist']['name'])
		song = cleaning(item['title'])
		if song.isupper() or song.islower():
			song = TitleCase(song)
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT or artist == "":
			continue
		UNIKAT.add(firstTitle)
		album = cleaning(item['album']['title']) if EXTRA == 'track' and item.get('album', '') and item['album'].get('title', '') else ""
		if album != "": plot += f"[CR]Album:  [B][COLOR yellow]{album}[/COLOR][/B]"
		if EXTRA == 'track':
			PHOTO = item['album']['cover_big'] if item.get('album', '') and item['album'].get('cover_big', '') else f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, album, PHOTO, plot])
	if TYPE == 'browse':
		for firstTitle, album, PHOTO, plot in musicVideos:
			NUMBER += 1
			name = translation(30631).format(firstTitle, album) if EXTRA == 'track' and showDETAILS else translation(30801).format(NUMBER, firstTitle)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': PHOTO, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		if musicVideos and content.get('next', '') and content['next'].startswith('https://api.deezer.com/'):
			addDir({'mode': 'listDeezerVideos', 'url': content['next'], 'number': NUMBER, 'extras': EXTRA, 'transmit': PHOTO}, create_entries({'Title': translation(30802), 'Image': f"{artpic}nextpage.png"}), automatic=True)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, album, PHOTO, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def appleMain(): # https://amp-api-music.apple.com/v1/editorial/us/groupings?genre=34&l=en-US&platform=web
	# https://amp-api-music.apple.com/v1/editorial/us/rooms/6456176470/contents?l=en-US&platform=web
	for item in [{'name': 30641, 'turn': 'listAppleGroups', 'slug': '/groupings?genre=34'},{'name': 30642, 'turn': 'listAppleCharts', 'slug': '/new/top-charts'},
		{'name': 30643, 'turn': 'listAppleRooms', 'slug': '/rooms/6456176473'},{'name': 30644, 'turn': 'listAppleRooms', 'slug': '/rooms/6456176472'},
		{'name': 30645, 'turn': 'listAppleRooms', 'slug': '/rooms/6456176470'},{'name': 30646, 'turn': 'listAppleRooms', 'slug': '/rooms/6456176471'}]:
		LINK = f"{BASE_URL_MA}/editorial/{appleRegion}{item['slug']}/contents?l={appleLocale}&platform=web&limit=150" if item['turn'] == 'listAppleRooms' else \
			f"{BASE_URL_MA}/editorial/{appleRegion}{item['slug']}&l={appleLocale}&platform=web&limit=100"
		addDir({'mode': item['turn'], 'url': LINK}, create_entries({'Title': translation(item['name']), 'Image': f"{artpic}apple.png"}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listAppleCharts(): # https://amp-api.music.apple.com/v1/catalog/us/charts?genre=34&chartId=135&limit=150&l=en-US&platform=web
	# https://amp-api.music.apple.com/v1/catalog/us/charts?genre=34&chart=most-played&types=playlists&limit=100&l=en-US&platform=web
	for item in [{'name': 30647, 'turn': 'listAppleRooms', 'slug': 'chartId=135&limit=150', 'plate': 'cityCharts'},
		{'name': 30648, 'turn': 'listAppleRooms', 'slug': 'chartId=119&limit=150', 'plate': 'dailyGlobalTopCharts'},
		{'name': 30649, 'turn': 'listAppleRooms', 'slug': 'chart=most-played&types=playlists&limit=200', 'plate': 'playlists'},
		{'name': 30650, 'turn': 'listAppleVideos', 'slug': 'chart=most-played&types=songs&limit=100', 'plate': 'songs'},
		{'name': 30651, 'turn': 'listAppleVideos', 'slug': 'chart=most-played&types=music-videos&limit=100', 'plate': 'music-videos'}]:
		addDir({'mode': item['turn'], 'url': f"{BASE_URL_MA}/catalog/{appleRegion}/charts?genre=34&{item['slug']}&l={appleLocale}&platform=web", 'extras': item['plate']}, \
			create_entries({'Title': translation(item['name']), 'Image': f"{artpic}apple.png"}), automatic=True if item['turn'] == 'listAppleVideos' else False)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listAppleRooms(url, EXTRA): # https://amp-api.music.apple.com/v1/editorial/de/rooms/6456176473/contents?l=de-DE&platform=web
	musicEntries, content = [], Transmission().retrieveContent(url, REF='https://music.apple.com/', AUTH='APPLEMUSIC')
	DATA_ONE = content.get('data', []) if EXTRA in ['DEFAULT', 'TRACKS'] else content['results'][EXTRA][0].get('data', [])
	for item in DATA_ONE:
		shorts = item['attributes']
		PLID = item['id']
		PLTE = item['type']
		NAME = (cleaning(shorts.get('shortName', '')) or cleaning(shorts.get('name', '')))
		DESC = shorts['description']['short'] if shorts.get('description', '') and shorts['description'].get('short', '') else None # shorts['description']['standard']
		if shorts.get('artwork', '') and shorts['artwork'].get('url', ''):
			THUMB = re.sub(r'/{w}x{h}', '/1080x1080', shorts['artwork']['url']) # /1080x1080SC.DN01.jpg?l=de-DE
		else: THUMB = f"{artpic}apple.png"
		musicEntries.append([NAME, PLID, PLTE, DESC, THUMB])
	musicEntries = sorted(musicEntries, key=lambda vsx: cleanUmlaut(vsx[0]).lower()) if EXTRA.endswith('Charts') or any(xe in url for xe in ['/6503417678', '/6503417844']) else musicEntries
	for NAME, PLID, PLTE, DESC, THUMB in musicEntries: # dailyGlobalTopCharts=6503417678 // cityCharts=6503417844
		if PLTE == 'playlists':# https://amp-api.music.apple.com/v1/catalog/de/playlists/pl.a2bebcf1035e456aba4109a414c4c2d5/tracks?platform=web
			LINK = f"{BASE_URL_MA}/catalog/{appleRegion}/{PLTE}/{PLID}/tracks?l={appleLocale}&platform=web&limit=100"
			addDir({'mode': 'listAppleVideos', 'url': LINK}, create_entries({'Title': NAME, 'Image': THUMB, 'Plot': DESC}), automatic=True)
		else: # https://amp-api.music.apple.com/v1/catalog/de/apple-curators/988574300/grouping?l=de-DE&platform=web
			LINK = f"{BASE_URL_MA}/catalog/{appleRegion}/{PLTE}/{PLID}/grouping?l={appleLocale}&platform=web&limit=100"
			addDir({'mode': 'listAppleGroups', 'url': LINK, 'transmit': THUMB}, create_entries({'Title': NAME, 'Image': THUMB, 'Plot': DESC}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listAppleGroups(url, PHOTO): # https://amp-api.music.apple.com/v1/catalog/de/apple-curators/988574300/grouping?l=de-DE&platform=web
	counter, supported, undesired = 0, ['music-videos', 'playlists', 'songs'], ['albums', 'uploaded-videos', 'stations']
	content = Transmission().retrieveContent(url, REF='https://music.apple.com/', AUTH='APPLEMUSIC')
	for item in content['data'][0]['relationships']['tabs']['data'][0]['relationships']['children'].get('data', {}):
		counter += 1
		if counter == 1: continue # Hide first category
		if item.get('attributes', '') and item['attributes'].get('resourceTypes', '') and any(xs in item['attributes']['resourceTypes'] for xs in supported) and \
			not any(xu in item['attributes']['resourceTypes'] for xu in undesired) and item.get('relationships', '') and item['relationships'].get('room', '') and \
			item['relationships']['room'].get('data', {}) and item['relationships']['room'].get('data', {})[0].get('href', ''): # Hide anything thats not supported
			PLID = item['relationships']['room']['data'][0]['id']
			NAME = cleaning(item['attributes']['name'])
			if 'interview' in NAME.lower(): continue # Hide interviews
			if any(xw in item['attributes']['resourceTypes'] for xw in ['music-videos', 'songs']): # https://amp-api-edge.music.apple.com/v1/editorial/us/rooms/6746612880/contents?l=en-US&platform=web&limit=100
				LINK = f"{BASE_URL_MA}/editorial/{appleRegion}/rooms/{PLID}/contents?l={appleLocale}&platform=web&limit=100"
				addDir({'mode': 'listAppleVideos', 'url': LINK}, create_entries({'Title': NAME, 'Image': PHOTO}), automatic=True)
			else: # https://amp-api-edge.music.apple.com/v1/editorial/de/rooms/6737138481/contents?l=de-DE&platform=web
				LINK = f"{BASE_URL_MA}/editorial/{appleRegion}/rooms/{PLID}/contents?l={appleLocale}&platform=web&limit=150"
				addDir({'mode': 'listAppleRooms', 'url': LINK, 'extras': 'TRACKS'}, create_entries({'Title': NAME, 'Image': PHOTO}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listAppleVideos(url, TYPE, LIMIT, EXTRA):
	musicVideos, UNIKAT, counter = [], set(), 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, REF='https://music.apple.com/', AUTH='APPLEMUSIC')
	DATA_ONE = content.get('data', []) if EXTRA == 'DEFAULT' else content['results'][EXTRA][0].get('data', [])
	for item in DATA_ONE:
		shorts = item['attributes']
		composers = [cleaning(at) for at in shorts['artistName'].split(', ')]
		artists = ', '.join(composers[:3]) # maximum three artists
		song = cleaning(shorts['name'])
		plot = f"Artist:  [B]{artists}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artists} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if shorts.get('releaseDate', ''):
			released = time.strptime(shorts['releaseDate'][:10], '%Y-%m-%d')
			newDate = time.strftime('%d.%m.%Y', released)
			plot += f"[CR]Date:  [B][COLOR deepskyblue]{newDate}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][{newDate}][/COLOR]"
		if shorts.get('albumName', ''):
			plot += f"[CR]Album:  [B][COLOR FFFFA500]{shorts['albumName']}[/COLOR][/B]"
		if shorts.get('artwork', '') and shorts['artwork'].get('url', ''):
			thumb = re.sub(r'/{w}x{h}', '/1080x1080', shorts['artwork']['url']) # /1400x1400bb.jpg or /3000x3000bb.jpg
		else: thumb = f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(counter, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def beatportMain():
	addDir({'mode': 'listBeatportVideos', 'url': '/en/top-100.json'}, create_entries({'Title': translation(30661), 'Image': f"{artpic}beatport.png"}), automatic=True)
	for pick in Transmission().genres_strong():
		LINK = f"/en/genre/{pick['slug']}/{pick['id']}/top-100.json" # /en/genre/140-deep-dubstep-grime/95/top-100.json
		addDir({'mode': 'listBeatportVideos', 'url': LINK}, create_entries({'Title': pick['ne'], 'Image': f"{artpic}beatport.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listBeatportVideos(url, TYPE, LIMIT):
	musicVideos, SHORT, UNIKAT, counter = [], {}, set(), 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, REF='https://www.beatport.com/', AUTH='BEATPORT')
	if content and len(content) > 0:
		SHORT = content['pageProps']['dehydratedState']['queries'][0]['state']['data']
	for item in SHORT.get('results', []):
		log(f"(utilities.listBeatportVideos) XXX {item} XXX")
		composers = [cleaning(at.get('name', '')) for at in item.get('artists', [])]
		artists = ', '.join(composers[:3]) # maximum three artists
		song = cleaning(item['name'])
		if item.get('mix_name', '') and not 'original' in item.get('mix_name').lower():
			song += f" [{cleaning(item['mix_name'])}]"
		plot = f"Artist:  [B]{artists}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artists} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if item.get('publish_date', ''):
			released = time.strptime(item['publish_date'], '%Y-%m-%d')
			newDate = time.strftime('%d.%m.%Y', released)
			plot += f"[CR]Date:  [B][COLOR deepskyblue]{newDate}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][{newDate}][/COLOR]"
		if item.get('release', '') and item['release'].get('label', '') and item['release']['label'].get('name', ''):
			plot += f"[CR]Label:  [B][COLOR FFFFA500]{item['release']['label']['name']}[/COLOR][/B]"
		if item.get('release', '') and item['release'].get('image', '') and item['release']['image'].get('dynamic_uri', ''):
			thumb = re.sub(r'/{w}x{h}', '/500x500', item['release']['image']['dynamic_uri']) # https://geo-media.beatport.com/image_size/{w}x{h}/ab2d1d04-233d-4b08-8234-9782b34dcab8.jpg
		else: thumb = f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(counter, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def billboardMain():
	for TITLE, PATH in [(30671, {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/hot-100/"}), (30672, {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-200/"}),
		(30673, {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-global-200/"}), (30674, {'mode': 'listBillboardCharts', 'url': 'genre'}),
		(30675, {'mode': 'listBillboardCharts', 'url': 'country'}), (30676, {'mode': 'listBillboardCharts', 'url': 'other'}), (30677, {'mode': 'listBillboardCharts', 'url': 'archive'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}billboard.png"}), automatic=True if TITLE in [30671, 30672, 30673] else False)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listBillboardCharts(SELECT):
	if SELECT == 'genre':
		for gen_item in [
			{'name': 'Alternative', 'slug': 'alternative-airplay/'},{'name': 'Country', 'slug': 'country-songs/'},{'name': 'Dance/Club', 'slug': 'dance-club-play-songs/'},
			{'name': 'Dance/Electronic', 'slug': 'dance-electronic-songs/'},{'name': 'Gospel', 'slug': 'gospel-songs/'},{'name': 'Latin', 'slug': 'latin-songs/'},{'name': 'Pop', 'slug': 'pop-songs/'},
			{'name': 'Rap', 'slug': 'rap-song/'},{'name': 'R&B', 'slug': 'r-and-b-songs/'},{'name': 'R&B/Hip-Hop', 'slug': 'r-b-hip-hop-songs/'},{'name': 'Rhythmic', 'slug': 'rhythmic-40/'},
			{'name': 'Rock', 'slug': 'rock-songs/'},{'name': 'Smooth Jazz', 'slug': 'jazz-songs/'},{'name': 'Soundtracks', 'slug': 'soundtracks/'},{'name': 'Tropical', 'slug': 'latin-tropical-airplay/'}]:
			addDir({'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/{gen_item['slug']}"}, create_entries({'Title': gen_item['name'], 'Image': f"{artpic}billboard.png"}), automatic=True)
	elif SELECT == 'country':
		for cou_item in [
			{'name': 'Argentina Hot-100', 'slug': 'billboard-argentina-hot-100/'},{'name': 'Canada Hot-100', 'slug': 'canadian-hot-100/'},{'name': 'Italy Hot-100', 'slug': 'billboard-italy-hot-100/'},
			{'name': 'U.K. - Singles Chart', 'slug': 'official-uk-songs/'},{'name': 'Australia Songs', 'slug': 'australia-songs-hotw/'},{'name': 'Belgium Songs', 'slug': 'belgium-songs-hotw/'},
			{'name': 'Brazil Songs', 'slug': 'brazil-songs-hotw/'},{'name': 'Croatia Songs', 'slug': 'croatia-songs-hotw/'},{'name': 'Denmark Songs', 'slug': 'denmark-songs-hotw/'},
			{'name': 'Finland Songs', 'slug': 'finland-songs-hotw/'},{'name': 'France Songs', 'slug': 'france-songs-hotw/'},{'name': 'Germany Songs', 'slug': 'germany-songs-hotw/'},
			{'name': 'Greece Songs', 'slug': 'greece-songs-hotw/'},{'name': 'Hungary Songs', 'slug': 'hungary-songs-hotw/'},{'name': 'Ireland Songs', 'slug': 'ireland-songs-hotw/'},
			{'name': 'Netherlands Songs', 'slug': 'netherlands-songs-hotw/'},{'name': 'Norway Songs', 'slug': 'norway-songs-hotw/'},{'name': 'Poland Songs', 'slug': 'poland-songs-hotw/'},
			{'name': 'Portugal Songs', 'slug': 'portugal-songs-hotw/'},{'name': 'Spain Songs', 'slug': 'spain-songs-hotw/'},{'name': 'Sweden Songs', 'slug': 'sweden-songs-hotw/'},
			{'name': 'Turkey Songs', 'slug': 'turkey-songs-hotw/'}]:
			addDir({'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/{cou_item['slug']}"}, create_entries({'Title': cou_item['name'], 'Image': f"{artpic}billboard.png"}), automatic=True)
	elif SELECT == 'other':
		for oth_item in [
			{'name': 'Digital Song Sales', 'slug': 'digital-song-sales/'},{'name': 'Streaming Songs', 'slug': 'streaming-songs/'},{'name': 'Radio Songs', 'slug': 'radio-songs/'},
			{'name': 'TOP Songs of the ’90s', 'slug': 'greatest-billboards-top-songs-90s/'},{'name': 'TOP Songs of the ’80s', 'slug': 'greatest-billboards-top-songs-80s/'},
			{'name': 'All Time Hot 100 Singles', 'slug': 'greatest-hot-100-singles/'},{'name': 'All Time Greatest Alternative Songs', 'slug': 'greatest-alternative-songs/'},
			{'name': 'All Time Greatest Country Songs', 'slug': 'greatest-country-songs/'},{'name': 'All Time Greatest Latin Songs', 'slug': 'greatest-hot-latin-songs/'},
			{'name': 'All Time Greatest Pop Songs', 'slug': 'greatest-of-all-time-pop-songs/'}]:
			addDir({'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/{oth_item['slug']}"}, create_entries({'Title': oth_item['name'], 'Image': f"{artpic}billboard.png"}), automatic=True)
	elif SELECT == 'archive':
		for arc_item in [
			{'name': 'Hot 100 Songs', 'slug': 'hot-100-songs/'},{'name': 'Global 200 Songs', 'slug': 'billboard-global-200/'},{'name': 'Streaming Songs', 'slug': 'streaming-songs/'},
			{'name': 'Radio Songs', 'slug': 'radio-songs/'},{'name': 'Digital Song Sales', 'slug': 'digital-songs/'},{'name': 'Alternative Songs', 'slug': 'hot-alternative-songs/'},
			{'name': 'Country Songs', 'slug': 'hot-country-songs/'},{'name': 'Dance/Electronic Songs', 'slug': 'hot-dance-electronic-songs/'},
			{'name': 'Gospel Songs', 'slug': 'hot-gospel-songs/'},{'name': 'Latin Songs', 'slug': 'hot-latin-songs/'},{'name': 'Pop Airplay Songs', 'slug': 'pop-songs/'},
			{'name': 'Rap Songs', 'slug': 'hot-rap-songs/'},{'name': 'R&B Songs', 'slug': 'hot-r-and-and-b-songs/'},{'name': 'R&B/Hip-Hop Songs', 'slug': 'hot-r-and-and-b-hip-hop-songs/'},
			{'name': 'Rhytmic Airplay Songs', 'slug': 'rhythmic-songs/'},{'name': 'Rock Songs', 'slug': 'hot-rock-songs/'},{'name': 'Hard Rock Songs', 'slug': 'hot-hard-rock-songs/'},
			{'name': 'Tropical Airplay Songs', 'slug': 'tropical-airplay-songs/'},{'name': 'Smooth Jazz Airplay Songs', 'slug': 'smooth-jazz-songs/'}]:
			addDir({'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/{arc_item['slug']}"}, create_entries({'Title': arc_item['name'], 'Image': f"{artpic}billboard.png"}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listBillboardArchive(url):
	content = Transmission().retrieveContent(url, queries='TEXT')
	result = re.compile(r'All Year-end Charts(.*?)</ul>', re.S).findall(content)[0]
	match = re.findall(r'href="('+BASE_URL_BB+'[^"]+).+?>([^<]+)</a>', result, re.S)
	for link, title in match:
		addDir({'mode': 'listBillboardVideos', 'url': link}, create_entries({'Title': title.strip(), 'Image': f"{artpic}billboard.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listBillboardVideos(url, TYPE, LIMIT):
	musicVideos, counter = [], 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, queries='TEXT')
	spl = content.split('class="o-chart-results-list-row-container">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		AT = re.compile(r'''id=["']title-of-a-story["'] class=["']c-title.+?<span class=["']c-label.+?>([^<]+)</span>''', re.S).findall(entry)[0]
		SG = re.compile(r'''id=["']title-of-a-story["'] class=["']c-title.+?>([^<]+)</''', re.S).findall(entry)[0]
		artist = cleaning(re.sub(r'\<.*?>', '', AT))
		song = cleaning(re.sub(r'\<.*?>', '', SG))
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		completeTitle = firstTitle
		if not 'charts/greatest' in url and not 'charts/year-end' in url:
			results = re.findall(r'''<div class=["']a-chart-plus-minus-icon["']>(.*?)<div class=["']charts-result-detail''', entry, re.S)
			for item in results:
				match = re.compile(r'''<span class=["']c-label.+?>([^<]+)</span>''', re.S).findall(item)
				if match and len(match) > 2:
					plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {str(match[0]).strip().replace('-', '~')}[/COLOR][/B][CR]Week:  [B][COLOR violet]{str(match[2]).strip().replace('-', '~')}[/COLOR][/B]"
					completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {str(match[0]).strip().replace('-', '~')}|WK: {str(match[2]).strip().replace('-', '~')}][/COLOR]"
		img = re.compile(r'''data-lazy-src=["'](https?://charts-static.billboard.com.+?(?:\.jpg|\.jpeg|\.png))''', re.S).findall(entry)
		thumb = re.sub(r'-[0-9]+x[0-9]+', '-480x480', img[0]).strip() if img else f"{artpic}noimage.png" # -53x53.jpg || -87x87.jpg || -106x106.jpg || -180x180.jpg || -224x224.jpg || -344x344.jpg
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(counter, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def ddpMain():
	content = Transmission().retrieveContent(BASE_URL_DP, queries='TEXT')
	result = re.compile(r'''<nav id=["']menu["']>(.*?)</nav>''', re.S).findall(content)[0]
	addDir({'mode': 'blankFUNC', 'url': '00'}, create_entries({'Title': translation(30691), 'Image': f"{artpic}ddp_dance.png"}), False)
	addDir({'mode': 'listDdpVideos', 'url': f"{BASE_URL_DP}/top-30/video"}, create_entries({'Title': translation(30692), 'Image': f"{artpic}ddp_dance.png"}), automatic=True)
	match = re.findall(r'''<a href=["']([^"']+)["']>(.*?)</a>''', result, re.S)
	for link, title in match:
		title = cleaning(title)
		if not title.lower().startswith(('ddp', 'top 30')) and not 'schlager' in link.lower():
			if title.lower() in ['top 100','hot 50', 'neueinsteiger']:
				addDir({'mode': 'listDdpVideos', 'url': f"{BASE_URL_DP}{link}"}, create_entries({'Title': f"..... {title}", 'Image': f"{artpic}ddp_dance.png"}), automatic=True)
			elif title.lower() in ['highscores', 'jahrescharts']:
				addDir({'mode': 'listDdpYearCharts', 'url': f"{BASE_URL_DP}{link}"}, create_entries({'Title': f"..... {title}", 'Image': f"{artpic}ddp_dance.png"}))
	addDir({'mode': 'blankFUNC', 'url': '00'}, create_entries({'Title': translation(30693), 'Image': f"{artpic}ddp_schlager.png"}), False)
	for link, title in match:
		title = cleaning(title)
		if not title.lower().startswith(('ddp', 'top 30')) and 'schlager' in link.lower():
			if title.lower() in ['top 100','hot 50', 'neueinsteiger']:
				addDir({'mode': 'listDdpVideos', 'url': f"{BASE_URL_DP}{link}"}, create_entries({'Title': f"..... {title}", 'Image': f"{artpic}ddp_schlager.png"}), automatic=True)
			elif title.lower() in ['highscores', 'jahrescharts']:
				addDir({'mode': 'listDdpYearCharts', 'url': f"{BASE_URL_DP}{link}"}, create_entries({'Title': f"..... {title}", 'Image': f"{artpic}ddp_schlager.png"}))
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listDdpYearCharts(url):
	musicVideos = []
	content = Transmission().retrieveContent(url, queries='TEXT')
	result = re.compile(r'''<div class=["']year-selection["']>(.*?)</div>''', re.S).findall(content)[0]
	musicVideos = re.findall(r'''<a href=["']([^"']+).*?>([^<]+)</a>''', result, re.S)
	for link, title in sorted(musicVideos, key=lambda xs: xs[1], reverse=True):
		thumb = f"{artpic}ddp_dance.png" if 'dance' in url.lower() else f"{artpic}ddp_schlager.png"
		addDir({'mode': 'listDdpVideos', 'url': f"{BASE_URL_DP}{link}"}, create_entries({'Title': cleaning(title), 'Image': thumb}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listDdpVideos(url, TYPE, LIMIT):
	musicVideos, UNIKAT = [], set()
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, queries='TEXT')
	if 'highscores' in url or 'jahrescharts' in url:
		result = re.compile(r'''<div class=["']charts big["'] style(.*?)<div class=["']charts big mobile["'] style''', re.S).findall(content)[0]
	else:
		result = re.compile(r'''<div class=["']charts big mobile["'] style(.*?)<div class=["']footer["']>''', re.S).findall(content)[-1]
	spl = result.split('<div class="entry">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		rank = re.compile(r'''<div class=["']rank["']>(.*?)</div>''', re.S).findall(entry)
		AT = re.compile(r'''<div class=["']artist["']>(.*?)</div>''', re.S).findall(entry)
		SG = re.compile(r'''<div class=["']title["']>(.*?)</div>''', re.S).findall(entry)
		if not AT or not SG:
			continue
		artist = TitleCase(cleaning(AT[0]))
		song = TitleCase(cleaning(SG[0]))
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if 'highscores' in url or 'jahrescharts' in url:
			POINT = re.compile(r'''<div class=["']s-pkt["']><div>(.*?)</div>''', re.S).findall(entry)
			WEEK = re.compile(r'''<div class=["']s-wk["']><div>(.*?)</div>''', re.S).findall(entry)
			if WEEK and not POINT:
				plot += f"[CR]Week:  [B][COLOR violet]{str(WEEK[0].strip())}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][WK: {str(WEEK[0].strip())}][/COLOR]"
			elif WEEK and POINT:
				plot += f"[CR]Point:  [B][COLOR FFFFA500]{str(POINT[0]).strip()}[/COLOR][/B][CR]Week:  [B][COLOR violet]{str(WEEK[0]).strip()}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][PT: {str(POINT[0]).strip()}|WK: {str(WEEK[0]).strip()}][/COLOR]"
		else:
			match = re.compile(r'''<div class=["']name["']>(.*?)</div>\s*<div class=["']value["']>(.*?)</div>''', re.S).findall(entry)
			CHANGE = match[0][1].strip().replace('<img src="img/icons/charts/dance/re.svg" width="16px" alt="">', 'RE') if match and len(match) > 0 and \
				cleaning(match[0][0]) == 'TW' else None
			NEW = CHANGE if CHANGE and CHANGE in ['NEU', 'RE'] else None
			UNO = str(match[1][1]).strip() if match and len(match) > 1 and cleaning(match[1][0]) == 'LW' else None
			DUE = str(match[2][1]).strip() if match and len(match) > 2 and cleaning(match[2][0]) == '2W' else None
			TRE = str(match[3][1]).strip() if match and len(match) > 3 and cleaning(match[3][0]) == '3W' else None
			if NEW:
				plot += f"[CR]Rank:  [B][COLOR chartreuse]{NEW}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][{NEW}][/COLOR]"
			elif NEW is None and UNO and DUE and TRE:
				plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {UNO.replace('-', '~')}|2W = {DUE.replace('-', '~')}|3W = {TRE.replace('-', '~')}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {UNO.replace('-', '~')}|2W: {DUE.replace('-', '~')}|3W: {TRE.replace('-', '~')}][/COLOR]"
		img = re.compile(r'''<div class=["']cover["'].+?//poolposition.mp3([^"']+)["']''', re.S).findall(entry)
		thumb = 'https://poolposition.mp3'+img[0].split('&width')[0] if img else f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([rank[0].strip(), firstTitle, completeTitle, thumb, plot])
	musicVideos = sorted(musicVideos, key=lambda cn: int(cn[0]))
	if TYPE == 'browse':
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(rank, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def hypemMain():
	for TITLE, PATH in [(30701, {'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular?ax=1&sortby=shuffle"}),
		(30702, {'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular/lastweek?ax=1&sortby=shuffle"}), (30703, {'mode': 'listHypemMachine'})]:
		addDir(PATH, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}hypem.png"}), automatic=True if TITLE in [30701, 30702] else False)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listHypemMachine():
	for i in range(1, 201, 1):
		dt = date.today()
		while dt.weekday() != 0:
			dt -= timedelta(days=1)
		dt -= timedelta(weeks=i)
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		month = months[int(dt.strftime('%m')) - 1]
		name = dt.strftime('%d. %b - %Y').replace('Mar', translation(30704)).replace('May', translation(30705)).replace('Oct', translation(30706)).replace('Dec', translation(30707))
		addDir({'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular/week:{month}-{dt.strftime('%d-%Y')}?ax=1&sortby=shuffle"}, create_entries({'Title': name, 'Image': f"{artpic}hypem.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listHypemVideos(url, TYPE, LIMIT):
	musicVideos, UNIKAT, counter = [], set(), 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, queries='TEXT')
	response = re.compile(r'''(?s)<script\s+type=["']application/json["']\s+id=["']displayList-data["']>(.*?)</script>''', re.S).findall(content)[0]
	DATA = json.loads(response)
	for item in DATA.get('tracks', []):
		artist = cleaning(item['artist'])
		song = cleaning(item['song'])
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT or artist == "":
			continue
		UNIKAT.add(firstTitle)
		img = re.compile(r'href="/track/'+item['id']+'/.+?background:url\((.*?)\)', re.S).findall(content)
		thumb = img[0] if img else f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, thumb, plot in musicVideos:
			counter += 1
			name = translation(30801).format(counter, firstTitle)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def ocMain():
	for TITLE, SLUG in [(30721, 'singles-chart/'), (30722, 'uk-top-40-singles-chart/'), (30723, 'singles-chart-update/'), (30724, 'singles-downloads-chart/'),
		(30725, 'singles-sales-chart/'), (30726, 'video-streaming-chart/'), (30727, 'audio-streaming-chart/'), (30728, 'vinyl-singles-chart/'),
		(30729, 'independent-singles-chart/'), (30730, 'dance-singles-chart/'), (30731, 'official-hip-hop-and-r-and-b-singles-chart/'), (30732, 'rock-and-metal-singles-chart/'),
		(30733, 'french-singles-chart/'), (30734, 'irish-singles-chart/'), (30735, 'end-of-year-singles-chart/'), (30736, 'physical-singles-chart/')]:
		addDir({'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/{SLUG}"}, create_entries({'Title': translation(TITLE), 'Image': f"{artpic}official.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listOcVideos(url, TYPE, LIMIT):
	musicVideos, UNIKAT, counter = [], set(), 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, queries='TEXT')
	result = re.compile(r'''<section class=["']chart-list(.*?)</section>''', re.S).findall(content)[0]
	spl = result.split('<div class="chart-item-content')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		AT = re.compile(r'''class=["']chart-artist.+?><span>(.*?)</span></(?:a|span)></p>''', re.S).findall(entry)[0]
		SG = re.compile(r'''class=["']chart-name.+?</span>(?:<!---->)?<span>(.*?)</span></a>''', re.S).findall(entry)[0]
		artist = TitleCase(cleaning(AT.replace('/', ', ')))
		song = TitleCase(cleaning(SG))
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		completeTitle = firstTitle
		MOVE = re.compile(r'''<li class=["']movement.+?<span class=["']text-brand.+?["']>(.*?)</span>''', re.S).findall(entry)
		PEAK = re.compile(r'''<li class=["']peak.+?<span class=["']text-brand.+?["']>(.*?)</span>''', re.S).findall(entry)
		WEEK = re.compile(r'''<li class=["']weeks.+?<span class=["']text-brand.+?["']>(.*?)</span>''', re.S).findall(entry)
		if MOVE and PEAK and WEEK:
			plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {str(MOVE[0]).strip().replace('-', '~')}[/COLOR][/B][CR]Peak:  [B][COLOR FFFFA500]{str(PEAK[0]).strip().replace('-', '~')}[/COLOR][/B]"\
				f"[CR]Week:  [B][COLOR violet]{str(WEEK[0]).strip().replace('-', '~')}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {str(MOVE[0]).strip().replace('-', '~')}|PK: {str(PEAK[0]).strip().replace('-', '~')}|WK: {str(WEEK[0]).strip().replace('-', '~')}][/COLOR]"
		img = re.compile(r'''<div class=["']chart-image["'].+?src=["'](https?://[^"']+)["'] width=''', re.S).findall(entry)
		thumb = re.sub(r'/[0-9]+x[0-9]+bb', '/512x512bb', img[0]).replace('item_artwork_small', 'item_artwork_large').strip() if img else f"{artpic}noimage.png"
		for snippet in BLACK_LISTING: # backstage.officialcharts.com = item_artwork_small > item_artwork_large // ssl.mzstatic.com = /80x80bb.jpg > /512x512bb.jpg
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(counter, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def shazamMain():
	musicCountries = []
	addDir({'mode': 'listShazamGenres'}, create_entries({'Title': translation(30751), 'Image': f"{artpic}shazam.png"}))
	content = Transmission().retrieveContent(f"{BASE_URL_SZ}/services/charts/locations", REF='https://www.shazam.com/', AUTH='SHAZAM')
	for item in content.get('countries', []): # https://www.shazam.com/services/charts/locations
		NAME = cleaning(item['name'])
		CTIP = item.get('id', None)
		PLID = item.get('listid', None)
		if CTIP and PLID: # https://www.shazam.com/services/amapi/v1/catalog/GB/playlists/pl.f3df92631c43423e866305ea8ba80745/tracks?limit=200&l=de&relate[songs]=artists,music-videos
			musicCountries.append([NAME, CTIP, PLID])
	for NAME, CTIP, PLID in sorted(musicCountries, key=lambda cs: cleanUmlaut(cs[0])): 
		addDir({'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/services/amapi/v1/catalog/{CTIP}/playlists/{PLID}/tracks?limit=200&l={shazamRegion}"}, create_entries({'Title': translation(30752).format(NAME), 'Image': f"{artpic}shazam.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listShazamGenres():
	musicGenres = []
	addDir({'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/services/amapi/v1/catalog/GB/playlists/pl.92d704ba99a3411289a34fab82866a62/tracks?limit=200&l={shazamRegion}"}, create_entries({'Title': translation(30753), 'Image': f"{artpic}shazam.png"}), automatic=True)
	content = Transmission().retrieveContent(f"{BASE_URL_SZ}/services/charts/locations", REF='https://www.shazam.com/', AUTH='SHAZAM')
	for item in content['global'].get('genres', []): # https://www.shazam.com/services/charts/locations
		NAME = cleaning(item['name'])
		PLID = item.get('listid', None)
		if PLID: # https://www.shazam.com/services/amapi/v1/catalog/GB/playlists/pl.f3df92631c43423e866305ea8ba80745/tracks?limit=200&l=de&relate[songs]=artists,music-videos
			musicGenres.append([NAME, PLID])
	for NAME, PLID in sorted(musicGenres, key=lambda gs: cleanUmlaut(gs[0])): 
		addDir({'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/services/amapi/v1/catalog/GB/playlists/{PLID}/tracks?limit=200&l={shazamRegion}"}, create_entries({'Title': NAME, 'Image': f"{artpic}shazam.png"}), automatic=True)
	xbmcplugin.setContent(ADDON_HANDLE, 'files')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listShazamVideos(url, TYPE, LIMIT):
	musicVideos, UNIKAT, counter = [], set(), 0
	PLT = cleanPlaylist() if TYPE == 'playing' else None
	content = Transmission().retrieveContent(url, REF='https://www.shazam.com/', AUTH='SHAZAM')
	for item in content.get('data', []):
		shorts = item['attributes']
		composers = [cleaning(at) for at in shorts['artistName'].split(', ')]
		artists = ', '.join(composers[:3]) # maximum three artists
		song = cleaning(shorts['name'])
		plot = f"Artist:  [B]{artists}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artists} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if shorts.get('releaseDate', ''):
			released = time.strptime(shorts['releaseDate'][:10], '%Y-%m-%d')
			newDate = time.strftime('%d.%m.%Y', released)
			plot += f"[CR]Date:  [B][COLOR deepskyblue]{newDate}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][{newDate}][/COLOR]"
		if shorts.get('albumName', ''):
			plot += f"[CR]Album:  [B][COLOR FFFFA500]{shorts['albumName']}[/COLOR][/B]"
		if shorts.get('artwork', '') and shorts['artwork'].get('url', ''):
			thumb = re.sub(r'/{w}x{h}', '/512x512', shorts['artwork']['url'])
		else: thumb = f"{artpic}noimage.png"
		for snippet in BLACK_LISTING:
			if len(snippet.strip()) > 2 and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(counter, SUFFIX)
			addDir({'mode': 'playTITLE', 'url': fittme(firstTitle)}, create_entries({'Title': name, 'Image': thumb, 'Plot': plot, 'Mediatype': 'episode', 'Reference': 'Single'}), False)
		xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		musicVideos = musicVideos[:int(LIMIT)] if int(LIMIT) > 0 else musicVideos
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			saw = build_mass({'mode': 'playTITLE', 'url': fittme(firstTitle)})
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(saw, listitem)
		xbmc.Player().play(PLT)

def playTITLE(SUFFIX):
	query = 'official+'+quote_plus(SUFFIX.lower()).replace('%5B', '').replace('%5D', '').replace('%28', '').replace('%29', '').replace('%2F', '')
	COMBI_VIDEO = []
	content = Transmission().retrieveContent(f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&order=relevance&q={query}&key={PERS_TOKEN}", REF='https://www.youtube.com/', AUTH='YOUTUBE')
	for item in content.get('items', []):
		if item.get('id', {}).get('kind', '') == 'youtube#video':
			TITLE = cleaning(item['snippet']['title'])
			PLID = item['id']['videoId']
			COMBI_VIDEO.append([TITLE, PLID])
	if COMBI_VIDEO:
		parts = COMBI_VIDEO[:]
		matching = [s for s in parts if not 'audio' in s[0].lower() and not 'hörprobe' in s[0].lower()]
		youtubeID = matching[0][1] if matching else parts[0][1]
		FINAL_URL = f"plugin://plugin.video.youtube/play/?video_id={youtubeID}"
		log(f"(navigator.playTITLE) StreamURL : {FINAL_URL}")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=FINAL_URL, offscreen=True))
		xbmc.sleep(1000)
		if enableINFOS: infoMessage()
	else:
		return dialog.notification(translation(30521).format('VIDEO'), translation(30525).format(SUFFIX), icon, 10000)

def infoMessage():
	counter = 0
	while not xbmc.Player().isPlaying():
		xbmc.sleep(200)
		if counter == 50:
			break
		counter += 1
	xbmc.sleep(int(infoDelay)*1000 - 2000)
	if xbmc.Player().isPlaying() and infoStyle == '0':
		xbmc.sleep(1500)
		xbmc.executebuiltin('ActivateWindow(12901)')
		xbmc.sleep(infoDuration*1000)
		xbmc.executebuiltin('ActivateWindow(12005)')
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(Back)')
	elif xbmc.Player().isPlaying() and infoStyle == '1':
		xbmc.getInfoLabel('Player.Title')
		xbmc.getInfoLabel('Player.Duration')
		xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(500)
		TITLE = xbmc.getInfoLabel('Player.Title')
		if TITLE.isupper() or TITLE.islower():
			TITLE = TitleCase(TITLE)
		RUNTIME = xbmc.getInfoLabel('Player.Duration')
		PHOTO = xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(1000)
		dialog.notification(translation(30803), translation(30804).format(TITLE, RUNTIME), PHOTO, int(infoDuration)*1000)

def addDir(params, listitem, folder=True, automatic=False):
	uws, entries = build_mass(params), []
	debug_MS(f"(navigator.{params.get('mode', '')}) ### PARAM : {urlencode(params, safe='/:?=&')} || FOLDER : {folder} ###")
	listitem.setPath(uws)
	if automatic is True:
		for LABEL, NUMBER in [(30831, 0), (30832, 10), (30833, 20), (30834, 30), (30835, 40), (30836, 50)]:
			entries.append([translation(LABEL), f"RunPlugin({build_mass({**params, **{'target': 'playing', 'limit': NUMBER}})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
