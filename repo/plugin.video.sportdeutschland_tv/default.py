# -*- coding: utf-8 -*-

'''
    Copyright (C) 2024 realvito

    Sportdeutschland.TV (light)

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
		if params['mode'] == 'create_account':
			navigator.create_account()
		elif params['mode'] == 'erase_account':
			navigator.erase_account()
		elif params['mode'] == 'SELECTION':
			navigator.SELECTION(params['Link'], params.get('Page', '1'), params.get('Limit', '20'), params.get('Wanted', '3'))
		elif params['mode'] == 'listSports':
			navigator.listSports(params['Link'], params.get('Code', ''), params.get('Section', 'Sport'), params.get('Page', '1'), params.get('Limit', '20'), params.get('Wanted', '3'), params.get('Extras', 'standard'), params.get('Name', 'Unknown'))
		elif params['mode'] == 'listCategories':
			navigator.listCategories(params['Slug'], params['Code'], params.get('Section', 'Sport'), params.get('Page', '1'), params.get('Limit', '20'), params.get('Wanted', '3'), params.get('Extras', 'standard'), params.get('Title', 'Unknown'))
		elif params['mode'] == 'SearchSDTV':
			navigator.SearchSDTV(params.get('Extras', 'Standard'))
		elif params['mode'] == 'listVideos':
			navigator.listVideos(params['Link'], params.get('Section', 'Sport'), params.get('Page', '1'), params.get('Limit', '20'), params.get('Meter', '0'), params.get('Kicked', '0'), params.get('Wanted', '3'), params.get('Extras', 'standard'))
		elif params['mode'] == 'playCODE':
			navigator.playCODE(params['IDENTiTY'])
		elif params['mode'] == 'listFavorites':
			navigator.listFavorites()
		elif params['mode'] == 'favorit_construct':
			navigator.favorit_construct(**params)
		elif params['mode'] == 'callingMain':
			navigator.mainMenu()
			xbmc.executebuiltin(f"Container.Update({HOST_AND_PATH}, replace)")
			return sys.exit(0)
		elif params['mode'] == 'blankFUNC':
			pass # do nothing
		elif params['mode'] == 'aConfigs':
			addon.openSettings()
			xbmc.executebuiltin('Container.Refresh')
		elif params['mode'] == 'iConfigs':
			xbmcaddon.Addon('inputstream.adaptive').openSettings()
	else:                     ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False ##### [plugin.video.sportdeutschland_tv v.2.0.5+v.2.06+v.2.12+v.2.13] - 30.09.21+03.10.21+12.05.24+23.12.24 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}addons{os.sep}{addon_id}{os.sep}lib{os.sep}")).encode('utf-8').decode('utf-8')
		UNO = xbmcvfs.translatePath(os.path.join(firstSCRIPT, 'only_at_FIRSTSTART'))
		if xbmcvfs.exists(UNO):
			SOURCE = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}userdata{os.sep}addon_data{os.sep}{addon_id}{os.sep}")).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(SOURCE):
				try:
					xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{addon_id}","enabled":false}}}}')
					if xbmcvfs.exists(FAVORIT_FILE) and os.stat(FAVORIT_FILE).st_size > 0:
						OLD_FAVS = preserve(FAVORIT_FILE)
						newest = {'code': 'Code', 'extras': 'Extras', 'limit': 'Limit', 'name': 'Title', 'pict': 'Image', 'plot': 'Plot', 'section': 'Section', 'url': 'Slug', 'wanted': 'Wanted'}
						for oldest in OLD_FAVS.get('items', []): # Change OLD.KEYS to NEW.KEYS in FAVORIT_FILE
							for key, value in oldest.copy().items():
								if key in newest.keys():
									oldest[newest[key]] = oldest.pop(key)
								else: oldest[key] = oldest.pop(key)
						preserve(FAVORIT_FILE, [tweak for tweak in OLD_FAVS.get('items', [])])
					if xbmcvfs.exists(MENUES_FILE):
						xbmcvfs.delete(MENUES_FILE) # Delete OLD_MENUES File
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
