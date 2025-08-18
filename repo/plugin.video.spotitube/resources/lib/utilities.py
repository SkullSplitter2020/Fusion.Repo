# -*- coding: utf-8 -*-

from .common import *


def _header(REFERRER=None, REALM=None, USERTOKEN=None):
	ACCEPTED = 'de-DE,de;q=0.9,en;q=0.8' if appleRegion in ['at', 'ch', 'de', 'li'] else 'en-US,en;q=0.9,de;q=0.8'
	header = {}
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = 'application/json, application/x-www-form-urlencoded, text/html, */*'
	header['User-Agent'] = get_userAgent()
	if REALM in ['APPLEJAVA', 'APPLEMUSIC']:
		header['Origin'] = 'https://music.apple.com'
		if REALM == 'APPLEJAVA': header['Content-Type'] = 'application/javascript'
	elif REALM == 'BEATPORT':
		header['Origin'] = 'https://www.beatport.com'
	if REALM in ['APPLEMUSIC', 'BEATPORT', 'DEEZER', 'YOUTUBE']:
		header['Content-Type'] = 'application/json; charset=utf-8'
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = ACCEPTED
	if REFERRER: header['Referer'] = REFERRER
	if USERTOKEN: header['Authorization'] = f"Bearer {USERTOKEN}"
	return header

class Transmission(object):
	def __init__(self):
		self.maxTokenTime = 6*60*60 # max. Token-Time (Seconds) before clear the Token and delete Token-File [6*60*60 = 6 Hours]
		self.tempAPPLE_folder = tempAPPLE
		self.apple_file = appleFile
		self.verify_ssl = verify_connection

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

	def convert_epoch(self, epoch):
		CIPHER = datetime(1970,1,1) + timedelta(seconds=int(epoch))
		return CIPHER.strftime('%d.%m.%Y - %H:%M:%S')

	def check_FreeToken(self, provider):
		debug_MS("(utilities.check_FreeToken) -------------------------------------------------- START = check_FreeToken --------------------------------------------------")
		forceRenew = authorised_access = False
		SELECT_PATH, SELECT_FILE, self.NOW_UTC = self.tempAPPLE_folder, self.apple_file, time.time()
		if provider == 'APPLEMUSIC' and SELECT_FILE is not None and os.path.isfile(SELECT_FILE):
			try:
				self.FILE_UTC = (os.path.getmtime(SELECT_FILE) + self.maxTokenTime)
				debug_MS(f"(utilities.check_FreeToken) {provider} ### SESSION-Time (utc NOW) = {self.convert_epoch(self.NOW_UTC)} || VALID until (utc SESSION) = {self.convert_epoch(self.FILE_UTC)} ###")
				if self.NOW_UTC < self.FILE_UTC:
					debug_MS(f"(utilities.check_FreeToken) ##### NOTHING CHANGED - TOKENFILE FOR *{provider}* IS OKAY #####")
					authorised_access = preserve(SELECT_FILE)['accessToken']
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
			HOME_PAGE = self.retrieveContent(f"https://music.apple.com/{appleRegion}/home", queries='TEXT')
			SCAN_AREA = re.compile(r'''id=["']vite-legacy-entry["'] data-src=["']([^"']+)["']''', re.S).findall(HOME_PAGE)
			JS_URL = f"https://music.apple.com{SCAN_AREA[0]}" if SCAN_AREA and SCAN_AREA[0][:4] != 'http' else SCAN_AREA[0] if SCAN_AREA else None
			JAVA_PAGE = self.retrieveContent(JS_URL, queries='TEXT', REF='https://music.apple.com/', AUTH='APPLEJAVA') if JS_URL else None
			CODING = re.compile(r'''IA.apply\(this,arguments\)\}var FA=["'](eyJ[^"']+)["'],TA=\[["']https://amp-api.music.apple.com["']''', re.S).findall(JAVA_PAGE) if JAVA_PAGE else None
			if CODING:
				debug_MS(f"(utilities.check_FreeToken) ### NEW TOKENFILE FOR >>{provider}<< CREATED : {{'accessToken': {CODING[0]}, 'generateUtc': {self.convert_epoch(self.NOW_UTC)}}} ###")
				if not xbmcvfs.exists(SELECT_PATH) and not os.path.isdir(SELECT_PATH):
					xbmcvfs.mkdirs(SELECT_PATH)
				preserve(SELECT_FILE, {'accessToken': CODING[0], 'generateUtc': self.convert_epoch(self.NOW_UTC)})
				authorised_access = CODING[0]
			else: failing(f"(utilities.check_FreeToken) XXXXX !!! ERROR = {provider} - COULD NOT FIND TOKEN ON PAGE = ERROR !!! XXXXX")
		return authorised_access

	def retrieveContent(self, url, method='GET', queries='JSON', REF=None, AUTH=None, headers={}, redirects=True, data=None, json=None, timeout=30):
		retries, (ANSWER, NEW_CODING) = 0, (None for _ in range(2))
		REALCODE = self.check_FreeToken(AUTH) if AUTH == 'APPLEMUSIC' else None
		if url.startswith('http'):
			try:
				response = requests.request(method, url, headers=_header(REF, AUTH, REALCODE), allow_redirects=redirects, verify=self.verify_ssl, timeout=timeout)
				response.raise_for_status()
				ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
				debug_MS(f"(utilities.retrieveContent[1]) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, AUTH, REALCODE)} ===")
			except requests.exceptions.RequestException as exc:
				failing(f"(utilities.retrieveContent[1]) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
				dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 10000)
				return sys.exit(0)
		else:
			def getCollected(suffix_URL, token_TRANSFER=None):
				debug_MS(f"(utilities.getCollected[1]) === suffix_URL : {suffix_URL} || token_TRANSFER : {token_TRANSFER} ===")
				recentURL = API_BEAT+token_TRANSFER+suffix_URL if token_TRANSFER else API_BEAT+addon.getSetting('new_staticCODE')+suffix_URL
				return recentURL
			while not ANSWER and retries < 3: # 2 x repetitions for the URL request ::: as the code for the API_BEATPORT may have been changed again
				retries += 1
				try:
					endURL = getCollected(url, NEW_CODING)
					response = requests.request(method, endURL, headers=_header(REF, AUTH, REALCODE), allow_redirects=redirects, verify=self.verify_ssl, timeout=timeout)
					response.raise_for_status()
					VALID_JSON = response.json() if queries == 'JSON' else None
					ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
					debug_MS(f"(utilities.retrieveContent[2]) === CALLBACK === RETRIES_no : {retries} === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, AUTH, REALCODE)} ===")
				except Exception as exc: # No JSON object could be decoded
					failing(f"(utilities.retrieveContent[2]) ERROR - CURRENT_TOKEN - ERROR ##### RETRIES_no : {retries} === URL : {url} === FAILURE : {exc} #####")
					CONTENT = requests.get(BASE_URL_BP, headers=_header(REF, AUTH, REALCODE), allow_redirects=redirects, verify=self.verify_ssl, timeout=10)
					SCAN_REQ = re.compile(r'''</script><script src=["']/_next/static/([^/]+)/_ssgManifest.js["']''', re.S).findall(CONTENT.text)
					#SCAN_REQ = re.compile(r'''["']query["']:.*?,["']buildId["']:["']([^"']+)["'],["']isFallback["']''', re.S).findall(CONTENT.text)
					if SCAN_REQ:
						NEW_CODING = SCAN_REQ[0]
						addon.setSetting('new_staticCODE', NEW_CODING)
					elif retries > 1 and not SCAN_REQ:
						retries += 2
						dialog.notification(translation(30521).format('URL'), translation(30524), icon, 12000)
						break
					time.sleep(2)
		debug_MS("---------------------------------------------")
		return ANSWER
