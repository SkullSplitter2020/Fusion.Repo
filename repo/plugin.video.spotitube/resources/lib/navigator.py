# -*- coding: utf-8 -*-

from .common import *
from .utilities import Transmission


iTunesRegion = itunesCountry.lower() if itunesForceCountry and itunesCountry != '' else region.lower()
spotifyRegion = spotifyCountry.upper() if spotifyForceCountry and spotifyCountry != '' else region.upper()

if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

if myTOKEN == 'AIzaSy.................................':
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")


def mainMenu():
	addDir(translation(30601), artpic+'deepsearch.gif', {'mode': 'SearchDeezer'})
	addDir(translation(30602), artpic+'beatport.png', {'mode': 'beatportMain'})
	addDir(translation(30603), artpic+'billboard.png', {'mode': 'billboardMain'})
	addDir(translation(30604), artpic+'ddp_home.png', {'mode': 'ddpMain'})
	addDir(translation(30605), artpic+'hypem.png', {'mode': 'hypemMain'})
	addDir(translation(30606), artpic+'itunes.png', {'mode': 'itunesMain'})
	addDir(translation(30607), artpic+'official.png', {'mode': 'ocMain'})
	addDir(translation(30608), artpic+'shazam.png', {'mode': 'shazamMain'})
	addDir(translation(30609), artpic+'spotify.png', {'mode': 'spotifyMain'})
	addDir(translation(30610).format(str(cachePERIOD)), artpic+'remove.png', {'mode': 'clearCache'}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30611), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def beatportMain():
	addDir(translation(30620), artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': '/en/top-100.json'}, automatic=True)
	for pick in Transmission().genres_strong():
		NEW_URL = f"/en/genre/{pick['slug']}/{pick['id']}/top-100.json" # /en/genre/140-deep-dubstep-grime/95/top-100.json
		addDir(pick['ne'], artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': NEW_URL}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listBeatportVideos(url, TYPE, LIMIT):
	musicVideos, SHORT = [], {}
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url)
	if content and len(content) > 0:
		SHORT = content['pageProps']['dehydratedState']['queries'][0]['state']['data']
	for item in SHORT.get('results', []):
		composers = [cleaning(at.get('name', '')) for at in item.get('artists', [])]
		artists = composers[0]
		for ii, value in enumerate(composers):
			if 1 <= ii <= 2: artists = f"{artists}, {value}" ### Listenauswahl der Composers liegt zwischen Nummer:1-2 ###
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
			thumb = item['release']['image']['dynamic_uri'].replace('{w}x{h}', '500x500') # https://geo-media.beatport.com/image_size/{w}x{h}/ab2d1d04-233d-4b08-8234-9782b34dcab8.jpg
		else: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(counter), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def billboardMain():
	addDir(translation(30630), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/hot-100/"}, automatic=True)
	addDir(translation(30631), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-200/"}, automatic=True)
	addDir(translation(30632), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-global-200/"}, automatic=True)
	addDir(translation(30633), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'genre'})
	addDir(translation(30634), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'country'})
	addDir(translation(30635), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'other'})
	addDir(translation(30636), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'archive'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBillboardCharts(SELECT):
	if SELECT == 'genre':
		addDir('Alternative', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/alternative-airplay/"}, automatic=True)
		addDir('Country', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/country-songs/"}, automatic=True)
		addDir('Dance/Club', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/dance-club-play-songs/"}, automatic=True)
		addDir('Dance/Electronic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/dance-electronic-songs/"}, automatic=True)
		addDir('Gospel', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/gospel-songs/"}, automatic=True)
		addDir('Latin', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/latin-songs/"}, automatic=True)
		addDir('Pop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/pop-songs/"}, automatic=True)
		addDir('Rap', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/rap-song/"}, automatic=True)
		addDir('R&B', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/r-and-b-songs/"}, automatic=True)
		addDir('R&B/Hip-Hop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/r-b-hip-hop-songs/"}, automatic=True)
		addDir('Rhythmic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/rhythmic-40/"}, automatic=True)
		addDir('Rock', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/rock-songs/"}, automatic=True)
		addDir('Smooth Jazz', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/jazz-songs/"}, automatic=True)
		addDir('Soundtracks', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/soundtracks/"}, automatic=True)
		addDir('Tropical', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/latin-tropical-airplay/"}, automatic=True)
	elif SELECT == 'country':
		addDir('Argentina Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-argentina-hot-100/"}, automatic=True)
		addDir('Canada Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/canadian-hot-100/"}, automatic=True)
		addDir('Italy Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/billboard-italy-hot-100/"}, automatic=True)
		addDir('U.K. - Singles Chart', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/official-uk-songs/"}, automatic=True)
		addDir('Australia Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/australia-songs-hotw/"}, automatic=True)
		addDir('Belgium Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/belgium-songs-hotw/"}, automatic=True)
		addDir('Brazil Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/brazil-songs-hotw/"}, automatic=True)
		addDir('Croatia Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/croatia-songs-hotw/"}, automatic=True)
		addDir('Denmark Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/denmark-songs-hotw/"}, automatic=True)
		addDir('Finland Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/finland-songs-hotw/"}, automatic=True)
		addDir('France Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/france-songs-hotw/"}, automatic=True)
		addDir('Germany Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/germany-songs-hotw/"}, automatic=True)
		addDir('Greece Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greece-songs-hotw/"}, automatic=True)
		addDir('Hungary Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/hungary-songs-hotw/"}, automatic=True)
		addDir('Ireland Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/ireland-songs-hotw/"}, automatic=True)
		addDir('Netherlands Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/netherlands-songs-hotw/"}, automatic=True)
		addDir('Norway Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/norway-songs-hotw/"}, automatic=True)
		addDir('Poland Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/poland-songs-hotw/"}, automatic=True)
		addDir('Portugal Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/portugal-songs-hotw/"}, automatic=True)
		addDir('Spain Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/spain-songs-hotw/"}, automatic=True)
		addDir('Sweden Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/sweden-songs-hotw/"}, automatic=True)
		addDir('Turkey Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/turkey-songs-hotw/"}, automatic=True)
	elif SELECT == 'other':
		addDir('Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/digital-song-sales/"}, automatic=True)
		addDir('Streaming Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/streaming-songs/"}, automatic=True)
		addDir('Radio Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/radio-songs/"}, automatic=True)
		addDir('TOP Songs of the ’90s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-billboards-top-songs-90s/"}, automatic=True)
		addDir('TOP Songs of the ’80s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-billboards-top-songs-80s/"}, automatic=True)
		addDir('All Time Hot 100 Singles', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-hot-100-singles/"}, automatic=True)
		addDir('All Time Greatest Alternative Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-alternative-songs/"}, automatic=True)
		addDir('All Time Greatest Country Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-country-songs/"}, automatic=True)
		addDir('All Time Greatest Latin Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-hot-latin-songs/"}, automatic=True)
		addDir('All Time Greatest Pop Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': f"{BASE_URL_BB}/charts/greatest-of-all-time-pop-songs/"}, automatic=True)
	elif SELECT == 'archive':
		addDir('Hot 100 Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-100-songs/"}) # bis 2006
		addDir('Global 200 Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/billboard-global-200/"}) # bis 2021
		addDir('Streaming Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/streaming-songs/"}) # bis 2013
		addDir('Radio Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/radio-songs/"}) # bis 2006
		addDir('Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/digital-songs/"}) # bis 2006
		addDir('Alternative Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-alternative-songs/"}) # bis 2021
		addDir('Country Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-country-songs/"}) # bis 2002
		addDir('Dance/Electronic Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-dance-electronic-songs/"}) # bis 2013
		addDir('Gospel Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-gospel-songs/"}) # bis 2006
		addDir('Latin Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-latin-songs/"}) # bis 2006
		addDir('Pop Airplay Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/pop-songs/"}) # bis 2008
		addDir('Rap Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-rap-songs/"}) # bis 2013
		addDir('R&B Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-r-and-and-b-songs/"}) # bis 2013
		addDir('R&B/Hip-Hop Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-r-and-and-b-hip-hop-songs/"}) # bis 2002
		addDir('Rhytmic Airplay Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/rhythmic-songs/"}) # bis 2006
		addDir('Rock Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-rock-songs/"}) # bis 2009
		addDir('Hard Rock Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/hot-hard-rock-songs/"}) # bis 2021
		addDir('Tropical Airplay Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/tropical-airplay-songs/"}) # bis 2006
		addDir('Smooth Jazz Airplay Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': f"{BASE_URL_BB}/charts/year-end/smooth-jazz-songs/"}) # bis 2006
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listBillboardArchive(url):
	content = Transmission().makeREQUEST(url, 'LOAD')
	result = re.findall(r'All Year-end Charts(.*?)</ul>', content, re.S)[0]
	match = re.compile(r'href="('+BASE_URL_BB+'[^"]+).+?>([^<]+?)</a>', re.S).findall(result)
	for link, title in match:
		addDir(title.strip(), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': link}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listBillboardVideos(url, TYPE, LIMIT):
	musicVideos = []
	startURL = url
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url, 'LOAD')
	spl = content.split('class="o-chart-results-list-row-container">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		AT = re.compile(r'id="title-of-a-story" class="c-title.+?<span class="c-label.+?>([^<]+?)</span>', re.S).findall(entry)[0]
		SG = re.compile(r'id="title-of-a-story" class="c-title.+?>([^<]+?)</', re.S).findall(entry)[0]
		artist = cleaning(re.sub(r'\<.*?>', '', AT))
		song = cleaning(re.sub(r'\<.*?>', '', SG))
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		completeTitle = firstTitle
		if not 'charts/greatest' in startURL and not 'charts/year-end' in startURL:
			results = re.findall(r'<div class="a-chart-plus-minus-icon">(.+?)<div class="charts-result-detail', entry, re.S)
			for item in results:
				match = re.compile(r'<span class="c-label.+?>([^<]+?)</span>', re.S).findall(item)
				if match and len(match) > 2:
					plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {str(match[0]).strip().replace('-', '~')}[/COLOR][/B][CR]Week:  [B][COLOR violet]{str(match[2]).strip().replace('-', '~')}[/COLOR][/B]"
					completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {str(match[0]).strip().replace('-', '~')}|WK: {str(match[2]).strip().replace('-', '~')}][/COLOR]"
		img = re.compile(r'data-lazy-src="(https?://charts-static.billboard.com.+?(?:\.jpg|\.jpeg|\.png))', re.S).findall(entry)
		thumb = re.sub(r'-[0-9]+x[0-9]+', '-480x480', img[0]).strip() if img else artpic+'noimage.png' # -53x53.jpg || -87x87.jpg || -106x106.jpg || -180x180.jpg || -224x224.jpg || -344x344.jpg
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(counter), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def ddpMain():
	content = Transmission().makeREQUEST(BASE_URL_DDP, 'LOAD')
	result = re.findall(r'<nav id="menu">(.*?)</nav>', content, re.S)[0]
	addDir(translation(30650), artpic+'ddp_dance.png', {'mode': 'blankFUNC', 'url': '00'}, folder=False)
	addDir(translation(30651), artpic+'ddp_dance.png', {'mode': 'listDdpVideos', 'url': f"{BASE_URL_DDP}/top-30/video"}, automatic=True)
	match = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.S).findall(result)
	for link, title in match:
		title = cleaning(title)
		if not title.lower().startswith(('ddp', 'top 30')):
			if not 'schlager' in link.lower():
				if title.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addDir('..... '+title, artpic+'ddp_dance.png', {'mode': 'listDdpVideos', 'url': f"{BASE_URL_DDP}{link}"}, automatic=True)
				elif title.lower() in ['highscores', 'jahrescharts']:
					addDir('..... '+title, artpic+'ddp_dance.png', {'mode': 'listDdpYearCharts', 'url': f"{BASE_URL_DDP}{link}"})
	addDir(translation(30652), artpic+'ddp_schlager.png', {'mode': 'blankFUNC', 'url': '00'}, folder=False)
	for link, title in match:
		title = cleaning(title)
		if not title.lower().startswith(('ddp', 'top 30')):
			if 'schlager' in link.lower():
				if title.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addDir('..... '+title, artpic+'ddp_schlager.png', {'mode': 'listDdpVideos', 'url': f"{BASE_URL_DDP}{link}"}, automatic=True)
				elif title.lower() in ['highscores', 'jahrescharts']:
					addDir('..... '+title, artpic+'ddp_schlager.png', {'mode': 'listDdpYearCharts', 'url': f"{BASE_URL_DDP}{link}"})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listDdpYearCharts(url):
	musicVideos = []
	content = Transmission().makeREQUEST(url, 'LOAD')
	result = re.findall(r'<div class="year-selection">(.*?)</div>', content, re.S)[0]
	musicVideos = re.compile(r'<a href="([^"]+).*?>([^<]+)</a>', re.S).findall(result)
	for link, title in sorted(musicVideos, key=lambda d: d[1], reverse=True):
		thumb = artpic+'ddp_dance.png' if 'dance' in url.lower() else artpic+'ddp_schlager.png'
		addDir(cleaning(title), thumb, {'mode': 'listDdpVideos', 'url': f"{BASE_URL_DDP}{link}"}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listDdpVideos(url, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url, 'LOAD')
	if 'highscores' in url or 'jahrescharts' in url:
		result = re.findall(r'<div class="charts big" style(.*?)<div class="charts big mobile" style', content, re.S)[0]
	else:
		result = re.findall(r'<div class="charts big mobile" style(.*?)<div class="footer">', content, re.S)[-1]
	spl = result.split('<div class="entry">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		rank = re.compile(r'<div class="rank">(.*?)</div>', re.S).findall(entry)
		AT = re.compile(r'<div class="artist">(.*?)</div>', re.S).findall(entry)
		SG = re.compile(r'<div class="title">(.*?)</div>', re.S).findall(entry)
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
			POINT = re.compile(r'<div class="s-pkt"><div>(.*?)</div>', re.S).findall(entry)
			WEEK = re.compile(r'<div class="s-wk"><div>(.*?)</div>', re.S).findall(entry)
			if WEEK and not POINT:
				plot += f"[CR]Week:  [B][COLOR violet]{str(WEEK[0].strip())}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][WK: {str(WEEK[0].strip())}][/COLOR]"
			elif WEEK and POINT:
				plot += f"[CR]Point:  [B][COLOR FFFFA500]{str(POINT[0]).strip()}[/COLOR][/B][CR]Week:  [B][COLOR violet]{str(WEEK[0]).strip()}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][PT: {str(POINT[0]).strip()}|WK: {str(WEEK[0]).strip()}][/COLOR]"
		else:
			match = re.compile(r'<div class="name">(.*?)</div>\s*<div class="value">(.*?)</div>', re.S).findall(entry)
			CHANGE = match[0][1].strip().replace('<img src="img/icons/charts/dance/re.svg" width="16px" alt="">', 'RE') if match and len(match) > 0 and \
				cleaning(match[0][0]) == 'TW' else None
			NEW = CHANGE if CHANGE and CHANGE in ['NEU', 'RE'] else None
			ONE = str(match[1][1]).strip() if match and len(match) > 1 and cleaning(match[1][0]) == 'LW' else None
			TWO = str(match[2][1]).strip() if match and len(match) > 2 and cleaning(match[2][0]) == '2W' else None
			TRE = str(match[3][1]).strip() if match and len(match) > 3 and cleaning(match[3][0]) == '3W' else None
			if NEW:
				plot += f"[CR]Rank:  [B][COLOR chartreuse]{NEW}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][{NEW}][/COLOR]"
			elif NEW is None and ONE and TWO and TRE:
				plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {ONE.replace('-', '~')}|2W = {TWO.replace('-', '~')}|3W = {TRE.replace('-', '~')}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {ONE.replace('-', '~')}|2W: {TWO.replace('-', '~')}|3W: {TRE.replace('-', '~')}][/COLOR]"
		img = re.compile(r'<div class="cover".+?//poolposition.mp3([^"]+)"', re.S).findall(entry)
		thumb = 'https://poolposition.mp3'+img[0].split('&width')[0] if img else artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([rank[0].strip(), firstTitle, completeTitle, thumb, plot])
	musicVideos = sorted(musicVideos, key=lambda d: int(d[0]), reverse=False)
	if TYPE == 'browse':
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(rank), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def hypemMain():
	addDir(translation(30660), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular?ax=1&sortby=shuffle"}, automatic=True)
	addDir(translation(30661), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular/lastweek?ax=1&sortby=shuffle"}, automatic=True)
	addDir(translation(30662), artpic+'hypem.png', {'mode': 'listHypemMachine'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listHypemMachine():
	for i in range(1, 201, 1):
		dt = date.today()
		while dt.weekday() != 0:
			dt -= timedelta(days=1)
		dt -= timedelta(weeks=i)
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		month = months[int(dt.strftime('%m')) - 1]
		name = dt.strftime('%d. %b - %Y').replace('Mar', translation(30663)).replace('May', translation(30664)).replace('Oct', translation(30665)).replace('Dec', translation(30666))
		addDir(name, artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': f"{BASE_URL_HM}/popular/week:{month}-{dt.strftime('%d-%Y')}?ax=1&sortby=shuffle"}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listHypemVideos(url, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url, 'LOAD')
	response = re.compile(r'id="displayList-data">(.*?)</', re.S).findall(content)[0]
	DATA = json.loads(response)
	for item in DATA['tracks']:
		artist = cleaning(item['artist'])
		song = cleaning(item['song'])
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT or artist == "":
			continue
		UNIKAT.add(firstTitle)
		img = re.compile(r'href="/track/'+item['id']+'/.+?background:url\\((.+?)\\)', re.S).findall(content)
		thumb = img[0] if img else artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, thumb, plot in musicVideos:
			counter += 1
			name = translation(30801).format(str(counter), firstTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def itunesMain():
	content = Transmission().makeREQUEST(f"https://itunes.apple.com/{iTunesRegion}/genre/music/id34", 'LOAD')
	content = content[content.find('id="genre-nav"'):]
	content = content[:content.find('</div>')]
	match = re.compile(r'<li><a href="https?://(?:itunes.|music.)apple.com/.+?/genre/.+?/id(.*?)"(.*?)title=".+?">(.*?)</a>', re.S).findall(content)
	addDir(translation(30680), artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': '00'}, automatic=True)
	for genreID, genreTYPE, genreTITLE in match:
		title = cleaning(genreTITLE)
		if 'class="top-level-genre"' in genreTYPE:
			if itunesShowSubGenres:
				title = translation(30681).format(title)
			addDir(title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID}, automatic=True)
		elif itunesShowSubGenres:
			addDir('..... '+title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listItunesVideos(genreID, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	url = f"https://itunes.apple.com/{iTunesRegion}/rss/topsongs/limit=100"
	if genreID != '00':
		url += '/genre='+genreID
	url += '/explicit=true/json'
	content = Transmission().makeREQUEST(url)
	for item in content['feed']['entry']:
		artist = cleaning(item['im:artist']['label'])
		song = cleaning(item['im:name']['label'])
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if item.get('im:releaseDate', '') and item['im:releaseDate'].get('attributes', '') and item['im:releaseDate']['attributes'].get('label', ''):
			newDate = item['im:releaseDate']['attributes']['label']
			plot += f"[CR]Date:  [B][COLOR deepskyblue]{newDate}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][{newDate}][/COLOR]"
		if item.get('im:image', '') and item.get('im:image', {})[2].get('label', ''):
			thumb = re.sub(r'/[0-9]+x[0-9]+bb', '/512x512bb', item['im:image'][2]['label']).replace('bb.png', 'bb.jpg').strip() # /55x55bb.png || /60x60bb.png || /170x170bb.png
		else: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(counter), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def ocMain():
	addDir(translation(30700), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/singles-chart/"}, automatic=True)
	addDir(translation(30701), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/uk-top-40-singles-chart/"}, automatic=True)
	addDir(translation(30702), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/singles-chart-update/"}, automatic=True)
	addDir(translation(30703), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/singles-downloads-chart/"}, automatic=True)
	addDir(translation(30704), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/singles-sales-chart/"}, automatic=True)
	addDir(translation(30705), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/video-streaming-chart/"}, automatic=True)
	addDir(translation(30706), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/audio-streaming-chart/"}, automatic=True)
	addDir(translation(30707), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/dance-singles-chart/"}, automatic=True)
	addDir(translation(30708), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/official-hip-hop-and-r-and-b-singles-chart/"}, automatic=True)
	addDir(translation(30709), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/rock-and-metal-singles-chart/"}, automatic=True)
	addDir(translation(30710), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/irish-singles-chart/"}, automatic=True)
	addDir(translation(30711), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/french-singles-chart/"}, automatic=True)
	addDir(translation(30712), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/end-of-year-singles-chart/"}, automatic=True)
	addDir(translation(30713), artpic+'official.png', {'mode': 'listOcVideos', 'url': f"{BASE_URL_OC}/charts/physical-singles-chart/"}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listOcVideos(url, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url, 'LOAD')
	result = re.findall(r'<section class="chart-list(.*?)</section>', content, re.S)[0]
	spl = result.split('<div class="chart-item-content')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		AT = re.compile(r'class="chart-artist.+?><span>(.*?)</span></a>', re.S).findall(entry)[0]
		SG = re.compile(r'class="chart-name.+?</span>(?:<!---->)?<span>(.*?)</span></a>', re.S).findall(entry)[0]
		artists = AT.replace('/', ', ')
		artists = TitleCase(cleaning(artists))
		song = TitleCase(cleaning(SG))
		plot = f"Artist:  [B]{artists}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artists} - {song}"
		completeTitle = firstTitle
		ONE = re.compile(r'<li class="movement.+?<span class="text-brand.*?">(.*?)</span>', re.S).findall(entry)
		PEAK = re.compile(r'<li class="peak.+?<span class="text-brand.*?">(.*?)</span>', re.S).findall(entry)
		WEEK = re.compile(r'<li class="weeks.+?<span class="text-brand.*?">(.*?)</span>', re.S).findall(entry)
		if ONE and PEAK and WEEK:
			plot += f"[CR]Rank:  [B][COLOR chartreuse]LW = {str(ONE[0]).strip().replace('-', '~')}[/COLOR][/B][CR]Peak:  [B][COLOR FFFFA500]{str(PEAK[0]).strip().replace('-', '~')}[/COLOR][/B]"\
				f"[CR]Week:  [B][COLOR violet]{str(WEEK[0]).strip().replace('-', '~')}[/COLOR][/B]"
			completeTitle = f"{firstTitle}   [COLOR deepskyblue][LW: {str(ONE[0]).strip().replace('-', '~')}|PK: {str(PEAK[0]).strip().replace('-', '~')}|WK: {str(WEEK[0]).strip().replace('-', '~')}][/COLOR]"
		img = re.compile(r'<div class="chart-image".+?src="(https?://[^"]+)" width=', re.S).findall(entry)
		thumb = re.sub(r'/[0-9]+x[0-9]+bb', '/512x512bb', img[0]).replace('item_artwork_small', 'item_artwork_large').replace('-250.jpg', '-500.jpg').strip() if img else artpic+'noimage.png'
		for snippet in blackList: # coverartarchive.org = -250.jpg > -500.jpg // backstage.officialcharts.com = item_artwork_small > item_artwork_large // ssl.mzstatic.com = /80x80bb.jpg > /512x512bb.jpg
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(counter), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def shazamMain():
	Supported = ['AU', 'BR', 'CA', 'FR', 'DE', 'IT', 'MX', 'RU', 'ZA', 'ES', 'TR', 'GB', 'US'] # these lists are supported for genrefolders
	addDir(translation(30730), artpic+'shazam.png', {'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/ip-global-chart?pageSize=200&startFrom=0"}, automatic=True)
	for pick in Transmission().countries_alpha():
		if any(x in pick['cd'] for x in Supported):
			addDir(translation(30731).format(pick['ne']), artpic+'shazam.png', {'mode': 'listShazamGenres', 'url': pick['cd']})
		else:
			addDir(translation(30732).format(pick['ne']), artpic+'shazam.png', {'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/ip-country-chart-{pick['cd']}?pageSize=200&startFrom=0"}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listShazamGenres(COUNTRY):
	GENRES = [{'ne': 'Pop','cd': '1'},{'ne': 'Hip-Hop/Rap','cd': '2'},{'ne': 'Dance','cd': '3'},{'ne': 'Electronic','cd': '4'},{'ne': 'R&B/Soul','cd': '5'},{'ne': 'Alternative','cd': '6'},
		{'ne': 'Rock','cd': '7'},{'ne': 'Latin','cd': '8'},{'ne': 'Film, TV & Stage','cd': '9'},{'ne': 'Country','cd': '10'},{'ne': 'AfroBeats','cd': '11'},{'ne': 'Worldwide','cd': '12'},
		{'ne': 'Reggae/Dancehall','cd': '13'},{'ne': 'House','cd': '14'},{'ne': 'K-Pop','cd': '15'},{'ne': 'French Pop','cd': '16'},{'ne': 'Singer/Songwriter','cd': '17'}]
	addDir(translation(30733).format(COUNTRY), artpic+'shazam.png', {'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/ip-country-chart-{COUNTRY}?pageSize=200&startFrom=0"}, automatic=True)
	for elem in sorted(GENRES, key=lambda n: n['ne'], reverse=False):
		addDir(elem['ne'], artpic+'shazam.png', {'mode': 'listShazamVideos', 'url': f"{BASE_URL_SZ}/genre-country-chart-{COUNTRY}-{elem['cd']}?pageSize=200&startFrom=0"}, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDGenres})")

def listShazamVideos(url, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = Transmission().makeREQUEST(url)
	for item in content.get('tracks', []):
		artist = cleaning(item['subtitle'])
		song = cleaning(item['title'])
		ATID = item['artists'][0]['adamid'] if item.get('artists', '') and item.get('artists', {})[0].get('adamid', '') else None
		# https://www.shazam.com/services/amapi/v1/catalog/GB/artists/487277?extend=origin&views=top-songs%2Ctop-music-videos = ATID
		plot = f"Artist:  [B]{artist}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artist} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		if item.get('images', '') and len(item['images']) > 0:
			img = (item['images'].get('coverarthq', '') or item['images'].get('coverart', ''))
			thumb = img.replace('/400x400cc.', '/500x500cc.')
		else: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, thumb, plot in musicVideos:
			counter += 1
			name = translation(30801).format(str(counter), firstTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def spotifyMain():
	addDir(translation(30750), artpic+'spotify.png', {'mode': 'listSpotifyPlaylists', 'url': f"{BASE_URL_SY}/views/charts-regional?platform=web&country={spotifyRegion}&offset=0&limit=50"})
	addDir(translation(30751), artpic+'spotify.png', {'mode': 'listSpotifyPlaylists', 'url': f"{BASE_URL_SY}/views/charts-viral?platform=web&country={spotifyRegion}&offset=0&limit=50"})
	addDir(translation(30752), artpic+'spotify.png', {'mode': 'listSpotifyPlaylists', 'url': f"{BASE_URL_SY}/views/charts-regional-weekly?platform=web&country={spotifyRegion}&offset=0&limit=50"})
	addDir(translation(30753), artpic+'spotify.png', {'mode': 'listSpotifyPlaylists', 'url': f"{BASE_URL_SY}/views/charts-featured?platform=web&country={spotifyRegion}&offset=0&limit=50"})
	addDir(translation(30754), artpic+'spotify.png', {'mode': 'listSpotifyPlaylists', 'url': f"{BASE_URL_SY}/users/spotify/playlists?platform=web&country={spotifyRegion}&offset=0&limit=50"})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSpotifyPlaylists(url):
	resource = '' if 'users/' in url else 'content'
	for item in Transmission().user_playlists(url, resource):
		PID = item['id']
		name = cleaning(item['name'])
		plot = (cleaning(re.sub(r'\<.*?>', '', item.get('description', ''))) or "...")
		total = item['tracks']['total'] if item.get('tracks', '') and item['tracks'].get('total', '') else 0
		if item.get('images', '') and item.get('images', {})[0].get('url', ''):
			thumb = item['images'][0]['url']
		else: thumb = artpic+'noimage.png'
		addDir(name, thumb, {'mode': 'listSpotifyVideos', 'url': PID}, plot, automatic=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listSpotifyVideos(url, TYPE, LIMIT):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	for item in Transmission().playlist_tracks(url, spotifyRegion):
		song = cleaning(item['track']['name']) if item.get('track', '') and item['track'].get('name', '') else None
		if item.get('track', None) is None or song is None: continue
		composers = [cleaning(at.get('name', '')) for at in item['track'].get('artists', [])]
		artists = composers[0]
		for ii, value in enumerate(composers):
			if 1 <= ii <= 2: artists = f"{artists}, {value}" ### Listenauswahl der Composers liegt zwischen Nummer:1-2 ###
		popular = item['track']['popularity'] if item['track'].get('popularity', '') else None
		TID = item['track']['id'] if item['track'].get('id', '') else 0
		plot = f"Artist:  [B]{artists}[/B][CR]Song:  [B]{song}[/B]"
		firstTitle = f"{artists} - {song}"
		if firstTitle in UNIKAT:
			continue
		UNIKAT.add(firstTitle)
		completeTitle = firstTitle
		if item['track'].get('album', ''):
			if item['track']['album'].get('release_date', '') and str(item['track']['album']['release_date'])[:4].isdigit() and len(str(item['track']['album']['release_date'])[:10]) == 10:
				released = time.strptime(item['track']['album']['release_date'][:10], '%Y-%m-%d')
				newDate = time.strftime('%d.%m.%Y', released)
				plot += f"[CR]Date:  [B][COLOR deepskyblue]{newDate}[/COLOR][/B]"
				completeTitle = f"{firstTitle}   [COLOR deepskyblue][{newDate}][/COLOR]"
			if item['track']['album'].get('images', '') and item['track']['album'].get('images', {})[0].get('url', ''):
				thumb = item['track']['album']['images'][0]['url']
			else: thumb = artpic+'noimage.png'
		if popular:
			plot += f"[CR]Fame:  [B][COLOR FFFFA500]{str(popular)}[/COLOR][/B]"
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			counter += 1
			SUFFIX = completeTitle if showDETAILS else firstTitle
			name = translation(30801).format(str(counter), SUFFIX)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def SearchDeezer():
	keyword = None
	someReceived = False
	keyword = dialog.input(translation(30770), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
	if keyword: keyword = quote_plus(keyword, safe='')
	else: return
	FOUNDATION = [
		{'action': 'artistSEARCH', 'conv': 'strukturARTIST', 'name': translation(30771), 'slug': 'artist', 'turn': 'listDeezerSelection'},
		{'action': 'trackSEARCH', 'conv': 'strukturTRACK', 'name': translation(30772), 'slug': 'track', 'turn': 'listDeezerVideos'},
		{'action': 'albumSEARCH', 'conv': 'strukturALBUM', 'name': translation(30773), 'slug': 'album', 'turn': 'listDeezerSelection'},
		{'action': 'playlistSEARCH', 'conv': 'strukturPLAYLIST', 'name': translation(30774), 'slug': 'playlist', 'turn': 'listDeezerSelection'},
		{'action': 'userlistSEARCH', 'conv': 'strukturUSERLIST', 'name': translation(30775), 'slug': 'user', 'turn': 'listDeezerSelection'}]
	for elem in FOUNDATION:
		elem['conv'] = Transmission().makeREQUEST(f"{BASE_URL_DZ}/{elem['slug']}?q={keyword}&limit={deezerSearchDisplay}&strict=on&output=json&index=0")
		if elem['slug'] == 'track' and elem['conv']['total'] != 0:
			addDir(elem['name'], artpic+elem['slug']+'.png', {'mode': elem['turn'], 'url': keyword, 'extras': elem['slug'], 'transmit': icon}, automatic=True)
			someReceived = True
		elif elem['slug'] in ['artist', 'album', 'playlist', 'user'] and elem['conv']['total'] != 0:
			addDir(elem['name'], artpic+elem['slug']+'.png', {'mode': elem['turn'], 'url': keyword, 'extras': elem['slug']})
			someReceived = True
	if not someReceived:
		addDir(translation(30776), artpic+'noresults.png', {'mode': 'root', 'url': keyword})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDeezerSelection(url, EXTRA):
	musicVideos = []
	UNIKAT = set()
	if url.startswith(BASE_URL_DZ):
		content = Transmission().makeREQUEST(quote_plus(url, safe='/:?=&'))
	else:
		content = Transmission().makeREQUEST(f"{BASE_URL_DZ}/{EXTRA}?q={quote_plus(url)}&limit={deezerSearchDisplay}&strict=on&output=json&index=0")
	for item in content['data']:
		artist = cleaning(item['artist']['name']) if EXTRA == 'album' else cleaning(item['name']) if EXTRA == 'artist' else TitleCase(cleaning(item['title'])) if EXTRA == 'playlist' else None
		album = cleaning(item['title']) if EXTRA == 'album' else None
		user = TitleCase(cleaning(item['user']['name'])) if EXTRA == 'playlist' else TitleCase(cleaning(item['name'])) if EXTRA == 'user' else None
		numbers = str(item['nb_tracks']) if EXTRA in ['album', 'playlist'] else str(item['nb_fan']) if EXTRA == 'artist' else None
		version = cleaning(item['record_type']).title() if EXTRA == 'album' else None
		try:
			thumb = item['picture_big'] if EXTRA in ['artist', 'playlist', 'user'] else item['cover_big']
			if EXTRA in ['artist', 'user'] and thumb.endswith(EXTRA+'//500x500-000000-80-0-0.jpg'):
				thumb = artpic+'noavatar.gif'
		except:
			thumb = artpic+'noavatar.gif' if EXTRA in ['artist', 'user'] else artpic+'noimage.png'
		if item.get('tracklist', '') and item['tracklist'].startswith('https://api.deezer.com/'):
			TRACKS_URL = f"{item['tracklist'].split('top?limit=')[0]}top?limit={deezerVideosDisplay}&index=0" if EXTRA == 'artist' else f"{item['tracklist']}?limit={deezerVideosDisplay}&index=0"
		else: TRACKS_URL = None
		special = f"{artist} - {album}" if EXTRA == 'album' else artist.strip().lower() if EXTRA == 'artist' else f"{artist} - {user}" if EXTRA == 'playlist' else user
		if TRACKS_URL is None or special in UNIKAT:
			continue
		UNIKAT.add(special)
		musicVideos.append([numbers, artist, album, user, version, TRACKS_URL, special, thumb])
	musicVideos = sorted(musicVideos, key=lambda d: int(d[0]), reverse=True) if EXTRA == 'artist' else musicVideos
	for numbers, artist, album, user, version, TRACKS_URL, special, thumb in musicVideos:
		if EXTRA == 'artist':
			name = translation(30777).format(artist, numbers) if showDETAILS else artist
			plot = f"Artist:  [B]{artist}[/B][CR]Fans:  [B][COLOR chartreuse]{numbers}[/COLOR][/B]"
		elif EXTRA == 'album':
			name = translation(30778).format(special, version, numbers) if showDETAILS else special
			plot = f"Artist:  [B]{artist}[/B][CR]Album:  [B][COLOR yellow]{album}[/COLOR][/B][CR]Version:  [B][COLOR deepskyblue]{version}[/COLOR][/B][CR]Tracks:  [B][COLOR FFFFA500]{numbers}[/COLOR][/B]"
		elif EXTRA == 'playlist':
			name = translation(30779).format(artist, user, numbers) if showDETAILS else artist
			plot = f"Artist:  [B]{artist}[/B][CR]User:  [B][COLOR chartreuse]{user}[/COLOR][/B][CR]Tracks:  [B][COLOR FFFFA500]{numbers}[/COLOR][/B]"
		elif EXTRA == 'user':
			name = user
			plot = f"User:  [B][COLOR chartreuse]{user}[/COLOR][/B]"
		addDir(name, thumb, {'mode': 'listDeezerVideos', 'url': TRACKS_URL, 'extras': EXTRA, 'transmit': thumb}, plot, automatic=True)
	if musicVideos and content.get('next', '') and content['next'].startswith(BASE_URL_DZ):
		addDir(translation(30802), artpic+'nextpage.png', {'mode': 'listDeezerSelection', 'url': content['next'], 'extras': EXTRA})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin(f"Container.SetViewMode({viewIDPlaylists})")

def listDeezerVideos(url, TYPE, LIMIT, EXTRA, PHOTO):
	musicVideos = []
	UNIKAT = set()
	counter = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	if EXTRA == 'track' and not 'index=' in url:
		content = Transmission().makeREQUEST(f"{BASE_URL_DZ}/{EXTRA}?q={quote_plus(url)}&limit={deezerVideosDisplay}&strict=on&output=json&index=0")
	else:
		content = Transmission().makeREQUEST(quote_plus(url, safe='/:?=&'))
	for item in content['data']:
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
			PHOTO = item['album']['cover_big'] if item.get('album', '') and item['album'].get('cover_big', '') else artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, album, PHOTO, plot])
	if TYPE == 'browse':
		for firstTitle, album, PHOTO, plot in musicVideos:
			counter += 1
			name = translation(30780).format(firstTitle, album) if EXTRA == 'track' and showDETAILS else translation(30801).format(str(counter), firstTitle)
			addLink(name, PHOTO, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		if musicVideos and content.get('next', '') and content['next'].startswith('https://api.deezer.com/'):
			addDir(translation(30802), artpic+'nextpage.png', {'mode': 'listDeezerVideos', 'url': content['next'], 'extras': EXTRA, 'transmit': PHOTO}, automatic=True)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin(f"Container.SetViewMode({viewIDVideos})")
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, album, PHOTO, plot in musicVideos:
			uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(uvz, listitem)
		xbmc.Player().play(PLT)

def playTITLE(SUFFIX):
	query = 'official+'+quote_plus(SUFFIX.lower()).replace('%5B', '').replace('%5D', '').replace('%28', '').replace('%29', '').replace('%2F', '')
	FINAL_URL = False
	COMBI_VIDEO = []
	content = Transmission().retrieveContent(f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&order=relevance&q={query}&key={myTOKEN}")
	for item in content.get('items', []):
		if item.get('id', {}).get('kind', '') == 'youtube#video':
			title = cleaning(item['snippet']['title'])
			IDD = item['id']['videoId']
			COMBI_VIDEO.append([title, IDD])
	if COMBI_VIDEO:
		parts = COMBI_VIDEO[:]
		matching = [s for s in parts if not 'audio' in s[0].lower() and not 'hörprobe' in s[0].lower()]
		youtubeID = matching[0][1] if matching else parts[0][1]
		FINAL_URL = f"plugin://plugin.video.youtube/play/?video_id={youtubeID}"
		log(f"(navigator.playTITLE) StreamURL : {FINAL_URL}")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=FINAL_URL))
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
	if xbmc.Player().isPlaying() and infoType == '0':
		xbmc.sleep(1500)
		xbmc.executebuiltin('ActivateWindow(12901)')
		xbmc.sleep(infoDuration*1000)
		xbmc.executebuiltin('ActivateWindow(12005)')
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(Back)')
	elif xbmc.Player().isPlaying() and infoType == '1':
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
		dialog.notification(translation(30803), translation(30804).format(TITLE, RUNTIME), PHOTO, infoDuration*1000)

def addDir(name, image, params={}, plot='...', automatic=False, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	debug_MS(f"(navigator.{params.get('mode', '')}) ### NAME = {name} || PHOTO = {image} ###")
	debug_MS(f"(navigator.{params.get('mode', '')}) xxx PARAM = {u} xxx")
	liz = xbmcgui.ListItem(name)
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot)
	else:
		liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	if automatic is True:
		entries = []
		entries.append([translation(30831), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		entries.append([translation(30832), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'limit': '10', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		entries.append([translation(30833), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'limit': '20', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		entries.append([translation(30834), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'limit': '30', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		entries.append([translation(30835), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'limit': '40', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		entries.append([translation(30836), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'target': 'play', 'limit': '50', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
		liz.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot='...'):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	debug_MS(f"(navigator.{params.get('mode', '')}) ### NAME = {name} || PHOTO = {image} ###")
	debug_MS(f"(navigator.{params.get('mode', '')}) xxx PARAM = {u} xxx")
	liz = xbmcgui.ListItem(name)
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot), vinfo.setMediaType('musicvideo')
	else:
		liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Mediatype': 'musicvideo'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([(translation(30805), 'Action(Queue)')])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)
