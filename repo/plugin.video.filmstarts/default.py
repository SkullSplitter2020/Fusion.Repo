# -*- coding: utf-8 -*-

'''
    Copyright (C) 2026 realvito

    FILMSTARTS.de

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
		if params['mode'] == 'listTrailers':
			navigator.listTrailers(params['category'])
		elif params['mode'] == 'listBroadcasts':
			navigator.listBroadcasts(params['category'])
		elif params['mode'] == 'filtrating':
			navigator.filtrating(params['url'], params.get('category', 'standard'))
		elif params['mode'] == 'selectionArticles':
			navigator.selectionArticles(params['url'], params.get('category', 'standard'), params.get('extras', 'standard'))
		elif params['mode'] == 'selectionWeeks':
			navigator.selectionWeeks(params['url'])
		elif params['mode'] == 'listVideos':
			navigator.listVideos(params['url'], params.get('page', 1), params.get('position', 0), params.get('category', 'standard'))
		elif params['mode'] == 'playCODE':
			navigator.playCODE(params['IDENTiTY'])
		elif params['mode'] == 'callingMain':
			navigator.mainMenu()
			xbmc.executebuiltin(f"Container.Update({HOST_AND_PATH}, replace)")
			return sys.exit(0)
		elif params['mode'] == 'blankFUNC':
			pass # do nothing
		elif params['mode'] == 'aConfigs':
			addon.openSettings()
			xbmc.executebuiltin('Container.Refresh')
	else: ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False ##### [plugin.video.filmstarts v.1.1.0+v.1.1.2] - 31.12.23 + 28.02.24 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}addons{os.sep}{addon_id}{os.sep}lib{os.sep}")).encode('utf-8').decode('utf-8')
		UNO = xbmcvfs.translatePath(os.path.join(firstSCRIPT, 'only_at_FIRSTSTART'))
		if xbmcvfs.exists(UNO):
			SOURCE = xbmcvfs.translatePath(os.path.join(f"special://home{os.sep}userdata{os.sep}addon_data{os.sep}{addon_id}{os.sep}")).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(SOURCE):
				try:
					xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{addon_id}","enabled":false}}}}')
					shutil.rmtree(SOURCE, ignore_errors=True)
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
