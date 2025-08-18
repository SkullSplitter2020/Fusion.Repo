# -*- coding: utf-8 -*-

'''
    Copyright (C) 2025 realvito

    You(T) Musicbox

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
		if params['mode'] == 'rootMain':
			navigator.mainMenu()
		elif params['mode'] == 'searchingDeezer':
			navigator.searchingDeezer()
		elif params['mode'] == 'listDeezerSelection':
			navigator.listDeezerSelection(params['url'], params.get('extras', 'DEFAULT'))
		elif params['mode'] == 'listDeezerVideos':
			navigator.listDeezerVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'), params.get('number', '0'), params.get('extras', 'DEFAULT'), params.get('transmit', f"{artpic}deezer.png"))
		elif params['mode'] == 'appleMain':
			navigator.appleMain()
		elif params['mode'] == 'listAppleCharts':
			navigator.listAppleCharts()
		elif params['mode'] == 'listAppleRooms':
			navigator.listAppleRooms(params['url'], params.get('extras', 'DEFAULT'))
		elif params['mode'] == 'listAppleGroups':
			navigator.listAppleGroups(params['url'], params.get('transmit', f"{artpic}apple.png"))
		elif params['mode'] == 'listAppleVideos':
			navigator.listAppleVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'), params.get('extras', 'DEFAULT'))
		elif params['mode'] == 'beatportMain':
			navigator.beatportMain()
		elif params['mode'] == 'listBeatportVideos':
			navigator.listBeatportVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'billboardMain':
			navigator.billboardMain()
		elif params['mode'] == 'listBillboardCharts':
			navigator.listBillboardCharts(params['url'])
		elif params['mode'] == 'listBillboardArchive':
			navigator.listBillboardArchive(params['url'])
		elif params['mode'] == 'listBillboardVideos':
			navigator.listBillboardVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'ddpMain':
			navigator.ddpMain()
		elif params['mode'] == 'listDdpYearCharts':
			navigator.listDdpYearCharts(params['url'])
		elif params['mode'] == 'listDdpVideos':
			navigator.listDdpVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'hypemMain':
			navigator.hypemMain()
		elif params['mode'] == 'listHypemMachine':
			navigator.listHypemMachine()
		elif params['mode'] == 'listHypemVideos':
			navigator.listHypemVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'ocMain':
			navigator.ocMain()
		elif params['mode'] == 'listOcVideos':
			navigator.listOcVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'shazamMain':
			navigator.shazamMain()
		elif params['mode'] == 'listShazamGenres':
			navigator.listShazamGenres()
		elif params['mode'] == 'listShazamVideos':
			navigator.listShazamVideos(params['url'], params.get('target', 'browse'), params.get('limit', '0'))
		elif params['mode'] == 'playTITLE':
			navigator.playTITLE(params['url'])
		elif params['mode'] == 'blankFUNC':
			pass # do nothing
		elif params['mode'] == 'aConfigs':
			addon.openSettings()
			xbmc.executebuiltin('Container.Refresh')
	else: ##### Delete old Files in Userdata-Folder 'settings' to cleanup old Entries #####
		DONE = False ##### [plugin.video.spotitube v.2.1.9+v.3.0.8] - 25.09.20+22.06.25 #####
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
			if not xbmcvfs.exists(dataPath):
				xbmcvfs.mkdirs(dataPath)
			if addon.getSetting('pers_apiKey') == 'AIzaSy.................................':
				xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")
			navigator.mainMenu()

run()
