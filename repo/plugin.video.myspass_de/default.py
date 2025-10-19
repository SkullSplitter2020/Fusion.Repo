# -*- coding: utf-8 -*-

'''
    Copyright (C) 2025 realvito

    MySpass

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from resources.lib.common import *
from resources.lib import navigator
params = dict(parse_qsl(sys.argv[2][1:]))


def run():
	if params:
		if params['mode'] == 'listShows':
			navigator.listShows(params['target'], params.get('name', ''), params.get('code', ''))
		elif params['mode'] == 'listSeasons':
			navigator.listSeasons(params['target'], params.get('name', ''), params.get('picture', ''))
		elif params['mode'] == 'listEpisodes':
			navigator.listEpisodes(params['target'], params.get('name', None), params.get('code', ''), params.get('number', 1), params.get('page', 1))
		elif params['mode'] == 'playVideo':
			navigator.playVideo(params['url'])
		elif params['mode'] == 'listFavorites':
			navigator.listFavorites()
		elif params['mode'] == 'favorit_construct':
			navigator.favorit_construct(**params)
		elif params['mode'] == 'aConfigs':
			addon.openSettings()
			xbmc.executebuiltin('Container.Refresh')
		elif params['mode'] == 'iConfigs':
			xbmcaddon.Addon('inputstream.adaptive').openSettings()
	else: ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False ##### [plugin.video.myspass_de v.5.0.1+5.0.3] - 03.11.24+14.09.25 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}addons{os.sep}{addon_id}{os.sep}lib{os.sep}")).encode('utf-8').decode('utf-8')
		UNO = xbmcvfs.translatePath(os.path.join(firstSCRIPT, 'only_at_FIRSTSTART'))
		if xbmcvfs.exists(UNO):
			SOURCE = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}userdata{os.sep}addon_data{os.sep}{addon_id}{os.sep}")).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(SOURCE):
				try:
					xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{addon_id}","enabled":false}}}}')
					if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
						OLD_FAVS = preserve(FAVORIT_FILE)
						newest = {'url': 'Cid', 'name': 'Title', 'plot': 'Plot', 'picture': 'Image', 'portrait': 'Poster'}
						for oldest in OLD_FAVS.get('items', []): # Change OLD.KEYS to NEW.KEYS in FAVORIT_FILE
							for key, value in oldest.copy().items():
								if key in newest.keys():
									oldest[newest[key]] = oldest.pop(key)
								else: oldest[key] = oldest.pop(key)
						preserve(FAVORIT_FILE, [tweak for tweak in OLD_FAVS.get('items', [])])
					RECORD_FILE = xbmcvfs.translatePath(os.path.join(SOURCE, 'heros_home.json'))
					if xbmcvfs.exists(RECORD_FILE):
						xbmcvfs.delete(RECORD_FILE) # Delete RECORD_FILE File
				except: pass
				xbmcvfs.delete(UNO)
				xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{addon_id}","enabled":true}}}}')
				xbmc.sleep(500)
				DONE = True
			else:
				xbmcvfs.delete(UNO)
				xbmc.sleep(500)
				DONE = True
		else:
			DONE = True
		if DONE is True:
			if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
				xbmcvfs.mkdirs(dataPath)
				xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")
			navigator.mainMenu()

run()
