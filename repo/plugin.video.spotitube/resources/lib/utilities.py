# -*- coding: utf-8 -*-

from .common import *


def _header(REFERRER=None, USERTOKEN=None):
	header = {}
	header['Pragma'] = 'no-cache'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	if REFERRER:
		header['Referer'] = REFERRER
	if USERTOKEN:
		header['Authorization'] = f"Bearer {USERTOKEN}"
	return header

class Transmission(object):

	def __init__(self):
		self.tempSPOT_folder = tempSPOT
		self.spotitfy_file = spotFile
		self.NOW_UTC = datetime.utcnow() # Actual UTC-Time
		self.verify_ssl = (True if addon.getSetting('verify_ssl') == 'true' else False)
		self.cache = cache
		self.session = requests.Session()

	def load_pagination(self, walk, resource='albums'):
		first_page = self.makeREQUEST(walk, AUTH='SPOTIFY')
		DATA_ONE = first_page[resource] if resource == 'content' else first_page
		for item in DATA_ONE.get('items', []): yield item
		ALLPAGES = (int(DATA_ONE['total']) // int(DATA_ONE['limit']))+1 if DATA_ONE.get('total', '') and DATA_ONE.get('limit', '') else -1
		if 'users/' in walk: ALLPAGES = 4
		debug_MS(f"(utilities.load_pagination) ### Total-Items : {str(DATA_ONE.get('total', None))} || Result of PAGES : {str(ALLPAGES)} ###")
		if ALLPAGES > 1 and DATA_ONE.get('next', ''):
			second_page =  self.makeREQUEST(DATA_ONE['next'], AUTH='SPOTIFY')
			DATA_TWO = second_page[resource] if resource == 'content' else second_page
			for item in DATA_TWO.get('items', []): yield item
		if ALLPAGES > 2 and DATA_TWO.get('next', ''):
			third_page =  self.makeREQUEST(DATA_TWO['next'], AUTH='SPOTIFY')
			DATA_THREE = third_page[resource] if resource == 'content' else third_page
			for item in DATA_THREE.get('items', []): yield item
		if ALLPAGES > 3 and DATA_THREE.get('next', ''):
			fourth_page =  self.makeREQUEST(DATA_THREE['next'], AUTH='SPOTIFY')
			DATA_FOUR = fourth_page[resource] if resource == 'content' else fourth_page
			for item in DATA_FOUR.get('items', []): yield item

	def playlist_tracks(self, playlist_id, CYSO):
		endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?platform=web&country={CYSO}&offset=0&limit=100"
		return self.load_pagination(endpoint, resource='tracks')

	def user_playlists(self, endpoint, resource='content'):
		return self.load_pagination(endpoint, resource)

	def countries_alpha(self):
		COUNTRIES = [{'ne': 'Algeria','cd': 'DZ'},{'ne': 'Argentina','cd': 'AR'},{'ne': 'Australia','cd': 'AU'},{'ne': 'Austria','cd': 'AT'},{'ne': 'Azerbaijan','cd': 'AZ'},
			{'ne': 'Belarus','cd': 'BY'},{'ne': 'Belgium','cd': 'BE'},{'ne': 'Brazil','cd': 'BR'},{'ne': 'Bulgaria','cd': 'BG'},{'ne': 'Canada','cd': 'CA'},{'ne': 'Chile','cd': 'CL'},
			{'ne': 'China','cd': 'CN'},{'ne': 'Central Africa','cd': 'CF'},{'ne': 'Colombia','cd': 'CO'},{'ne': 'Costa Rica','cd': 'CR'},{'ne': 'Croatia','cd': 'HR'},{'ne': 'Cuba','cd': 'CU'},
			{'ne': 'Cyprus','cd': 'CY'},{'ne': 'Czech Republic','cd': 'CZ'},{'ne': 'Denmark','cd': 'DK'},{'ne': 'Dominican Republic','cd': 'DO'},{'ne': 'Ecuador','cd': 'EC'},{'ne': 'El Salvador','cd': 'SV'},
			{'ne': 'Estonia','cd': 'EE'},{'ne': 'Ethiopia','cd': 'ET'},{'ne': 'Finland','cd': 'FI'},{'ne': 'France','cd': 'FR'},{'ne': 'Gambia','cd': 'GM'},{'ne': 'Georgia','cd': 'GE'},
			{'ne': 'Germany','cd': 'DE'},{'ne': 'Ghana','cd': 'GH'},{'ne': 'Greece','cd': 'GR'},{'ne': 'Grenada','cd': 'GD'},{'ne': 'Haiti','cd': 'HT'},{'ne': 'Honduras','cd': 'HN'},
			{'ne': 'Hong Kong','cd': 'HK'},{'ne': 'Hungary','cd': 'HU'},{'ne': 'Iceland','cd': 'IS'},{'ne': 'India','cd': 'IN'},{'ne': 'Indonesia','cd': 'ID'},{'ne': 'Ireland','cd': 'IE'},
			{'ne': 'Israel','cd': 'IL'},{'ne': 'Italy','cd': 'IT'},{'ne': 'Jamaica','cd': 'JM'},{'ne': 'Japan','cd': 'JP'},{'ne': 'Jordan','cd': 'JO'},{'ne': 'Kenya','cd': 'KE'},
			{'ne': 'Korea','cd': 'KR'},{'ne': 'Kuwait','cd': 'KW'},{'ne': 'Latvia','cd': 'LV'},{'ne': 'Liberia','cd': 'LR'},{'ne': 'Libya','cd': 'LY'},{'ne': 'Liechtenstein','cd': 'LI'},
			{'ne': 'Luxembourg','cd': 'LU'},{'ne': 'Macedonia','cd': 'MK'},{'ne': 'Malta','cd': 'MT'},{'ne': 'Mexico','cd': 'MX'},{'ne': 'Monaco','cd': 'MC'},{'ne': 'Montenegro','cd': 'ME'},
			{'ne': 'Morocco','cd': 'MA'},{'ne': 'Netherlands','cd': 'NL'},{'ne': 'New Zealand','cd': 'NZ'},{'ne': 'Nicaragua','cd': 'NI'},{'ne': 'Nigeria','cd': 'NG'},{'ne': 'Norway','cd': 'NO'},
			{'ne': 'Pakistan','cd': 'PK'},{'ne': 'Panama','cd': 'PA'},{'ne': 'Paraguay','cd': 'PY'},{'ne': 'Peru','cd': 'PE'},{'ne': 'Philippines','cd': 'PH'},{'ne': 'Poland','cd': 'PL'},
			{'ne': 'Portugal','cd': 'PT'},{'ne': 'Puerto Rico','cd': 'PR'},{'ne': 'Romania','cd': 'RO'},{'ne': 'Russia','cd': 'RU'},{'ne': 'San Marino','cd': 'SM'},{'ne': 'Saudi Arabia','cd': 'SA'},
			{'ne': 'Senegal','cd': 'SN'},{'ne': 'Serbia','cd': 'RS'},{'ne': 'Singapore','cd': 'SG'},{'ne': 'Slovakia','cd': 'SK'},{'ne': 'Slovenia','cd': 'SI'},{'ne': 'Somalia','cd': 'SO'},
			{'ne': 'South Africa','cd': 'ZA'},{'ne': 'Spain','cd': 'ES'},{'ne': 'Sri Lanka','cd': 'LK'},{'ne': 'Sudan','cd': 'SD'},{'ne': 'Sweden','cd': 'SE'},{'ne': 'Switzerland','cd': 'CH'},
			{'ne': 'Taiwan','cd': 'TW'},{'ne': 'Tanzania','cd': 'TZ'},{'ne': 'Thailand','cd': 'TH'},{'ne': 'Tunisia','cd': 'TN'},{'ne': 'Turkey','cd': 'TR'},{'ne': 'Uganda','cd': 'UG'},
			{'ne': 'Ukraine','cd': 'UA'},{'ne': 'United Kingdom','cd': 'GB'},{'ne': 'United States','cd': 'US'},{'ne': 'Uruguay','cd': 'UY'},{'ne': 'Uzbekistan','cd': 'UZ'},{'ne': 'Venezuela','cd': 'VE'},
			{'ne': 'Viet Nam','cd': 'VN'},{'ne': 'Yemen','cd': 'YE'},{'ne': 'Zimbabwe','cd': 'ZW'}]
		return COUNTRIES

	def genres_strong(self):
		GENRES = [{'ne': '140 / Deep Dubstep / Grime','slug': '140-deep-dubstep-grime','id': '95'},{'ne': 'Afro House','slug': 'afro-house','id': '89'},{'ne': 'Amapiano','slug': 'amapiano','id': '98'},
			{'ne': 'Bass / Club','slug': 'bass-club','id': '85'},{'ne': 'Bass House','slug': 'bass-house','id': '91'},{'ne': 'Breaks / Breakbeat / UK Bass','slug': 'breaks-breakbeat-uk-bass','id': '9'},
			{'ne': 'Dance / Electro Pop','slug': 'dance-electro-pop','id': '39'},{'ne': 'Deep House','slug': 'deep-house','id': '12'},{'ne': 'DJ Tools','slug': 'dj-tools','id': '16'},
			{'ne': 'Drum & Bass','slug': 'drum-bass','id': '1'},{'ne': 'Dubstep','slug': 'dubstep','id': '18'},{'ne': 'Electro (Classic / Detroit / Modern)','slug': 'electro-classic-detroit-modern','id': '94'},
			{'ne': 'Electronica','slug': 'electronica','id': '3'},{'ne': 'Funky House','slug': 'funky-house','id': '81'},{'ne': 'Hard Dance / Hardcore','slug': 'hard-dance-hardcore','id': '8'},
			{'ne': 'Hard Techno','slug': 'hard-techno','id': '2'},{'ne': 'House','slug': 'house','id': '5'},{'ne': 'Indie Dance','slug': 'indie-dance','id': '37'},{'ne': 'Jackin House','slug': 'jackin-house','id': '97'},
			{'ne': 'Mainstage','slug': 'mainstage','id': '96'},{'ne': 'Melodic House & Techno','slug': 'melodic-house-techno','id': '90'},{'ne': 'Minimal / Deep Tech','slug': 'minimal-deep-tech','id': '14'},
			{'ne': 'Nu Disco / Disco','slug': 'nu-disco-disco','id': '50'},{'ne': 'Organic House / Downtempo','slug': 'organic-house-downtempo','id': '93'},
			{'ne': 'Progressive House','slug': 'progressive-house','id': '15'},{'ne': 'Psy-Trance','slug': 'psy-trance','id': '13'},{'ne': 'Tech House','slug': 'tech-house','id': '11'},
			{'ne': 'Techno (Peak Time / Driving)','slug': 'techno-peak-time-driving','id': '6'},{'ne': 'Techno (Raw / Deep / Hypnotic)','slug': 'techno-raw-deep-hypnotic','id': '92'},
			{'ne': 'Trance (Main Floor)','slug': 'trance-main-floor','id': '7'},{'ne': 'Trance (Raw / Deep / Hypnotic)','slug': 'trance-raw-deep-hypnotic','id': '99'},
			{'ne': 'Trap / Wave','slug': 'trap-wave','id': '38'},{'ne': 'UK Garage / Bassline','slug': 'uk-garage-bassline','id': '86'}]
		return GENRES

	def check_FreeToken(self, provider):
		debug_MS("(utilities.check_FreeToken) -------------------------------------------------- START = check_FreeToken --------------------------------------------------")
		CODING, forceRenew, free_ACCESS, expires = False, False, '000', 1688947200000 # Monday, 10. July 2023 00:00:00
		SELECT_FILE = self.spotitfy_file
		SELECT_PATH = self.tempSPOT_folder
		if provider == 'SPOTIFY' and SELECT_FILE is not None and os.path.isfile(SELECT_FILE):
			try:
				with open(SELECT_FILE, 'r') as output:
					DATA = json.load(output)
				expires = DATA['accessTokenExpirationTimestampMs']
				EXPIRE_UTC = datetime(1970,1,1) + timedelta(milliseconds=expires - 120000) # 2 minutes minus for safety
				debug_MS(f"(utilities.check_FreeToken) {provider} ### SESSION-Time (utc NOW) = {str(self.NOW_UTC)[:19]} || VALID until (utc SESSION) = {str(EXPIRE_UTC)[:19]} ###")
				if self.NOW_UTC < EXPIRE_UTC:
					debug_MS(f"(utilities.check_FreeToken) ##### NOTHING CHANGED - TOKENFILE FOR *{provider}* IS OKAY #####")
					free_ACCESS = DATA['accessToken']
				else:
					debug_MS(f"(utilities.check_FreeToken) ##### TIMEOUT FOR SESSION - DELETE *{provider}* TOKENFILE #####")
					forceRenew = True
			except:
				failing(f"(utilities.check_FreeToken) XXXXX !!! ERROR = {provider}-TOKENFILE [TOKENFORMAT IS INVALID] = ERROR !!! XXXXX")
				forceRenew = True
		else:
			debug_MS(f"(utilities.check_FreeToken) ##### NOTHING FOUND - CREATE TOKENFILE FOR *{provider}* #####")
			forceRenew = True
		if forceRenew:
			if SELECT_FILE is not None and os.path.isfile(SELECT_FILE):
				shutil.rmtree(SELECT_PATH, ignore_errors=True)
			CODING = self.retrieveContent('https://open.spotify.com/get_access_token?reason=transport&productType=web_player')
			if CODING:
				debug_MS(f"(utilities.check_FreeToken) ### NEW TOKENFILE FOR *{provider}* CREATED : {CODING} ###")
				if not xbmcvfs.exists(SELECT_PATH) and not os.path.isdir(SELECT_PATH):
					xbmcvfs.mkdirs(SELECT_PATH)
				with open(SELECT_FILE, 'w') as input:
					json.dump(CODING, input, indent=4, sort_keys=True)
				free_ACCESS = CODING['accessToken']
		return free_ACCESS

	def makeREQUEST(self, url, method='GET', REF=None, AUTH=None):
		content = self.cache.cacheFunction(self.retrieveContent, url, method, REF, AUTH)
		return content

	def retrieveContent(self, url, method='GET', REF=None, AUTH=None, headers=None, cookies=None, allow_redirects=True, stream=None, data=None, json=None):
		authtoken = self.check_FreeToken(AUTH) if AUTH else None
		ANSWER, NEW_CODING = (None for _ in range(2))
		self.session.keep_alive = False
		retries = 0
		if url[:4] == 'http':
			try:
				response = self.session.get(url, headers=_header(REF, authtoken), allow_redirects=allow_redirects, verify=self.verify_ssl, stream=stream, timeout=30)
				ANSWER = response.json() if method in ['GET', 'POST'] else response.text
				debug_MS(f"(common.getUrl) === CALLBACK === status : {str(response.status_code)} || url : {response.url} || header : {_header(REF, authtoken)} ===")
			except requests.exceptions.RequestException as e:
				failing(f"(common.getUrl) ERROR - ERROR - ERROR ##### url : {url} === error : {str(e)} #####")
				dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 12000)
				return sys.exit(0)
		else:
			def getCollected(suffix_URL, token_TRANSFER=None):
				debug_MS(f"(common.getCollected) === suffix_URL : {suffix_URL} || token_TRANSFER : {str(token_TRANSFER)} ===")
				recentURL = API_BEAT+token_TRANSFER+suffix_URL if token_TRANSFER else API_BEAT+BPT_staticCODE+suffix_URL
				return recentURL
			while not ANSWER and retries < 3: # 2 x Wiederholungen (gesamt=3) für den URL-Request ::: da der Code für die API_BEAT evtl. wieder geändert wurde
				retries += 1
				try:
					endURL = getCollected(url, NEW_CODING)
					response = self.session.get(endURL, headers=_header(REF, authtoken), allow_redirects=allow_redirects, verify=self.verify_ssl, stream=stream, timeout=30)
					ANSWER = response.json() if method in ['GET', 'POST'] else response.text
					debug_MS(f"(common.getUrl) === CALLBACK === retries_no : {str(retries)} === status : {str(response.status_code)} || url : {response.url} || header : {_header(REF, authtoken)} ===")
				except Exception as e: # No JSON object could be decoded
					failing(f"(common.getUrl) ERROR - CURRENT_TOKEN - ERROR ##### retries_no : {str(retries)} === status : {str(response.status_code)} === url : {response.url} === error : {str(e)} #####")
					CONTENT = self.session.get(BASE_URL_BP, headers=_header(REF, authtoken), allow_redirects=allow_redirects, verify=self.verify_ssl, stream=stream, timeout=10)
					SCAN_REQ = re.compile('</script><script src="/_next/static/([^/]+?)/_ssgManifest.js" defer=', re.S).findall(CONTENT.text)
					#SCAN_REQ = re.compile('"query":{},"buildId":"([^"]+?)","isFallback"', re.S).findall(CONTENT.text)
					if SCAN_REQ:
						NEW_CODING = SCAN_REQ[0]
						addon.setSetting('new_staticCODE', NEW_CODING)
					elif retries > 1 and not SCAN_REQ:
						ANSWER = ''
						retries += 2
						dialog.notification(translation(30521).format('URL'), translation(30524), icon, 12000)
						break
					time.sleep(2)
		return ANSWER
