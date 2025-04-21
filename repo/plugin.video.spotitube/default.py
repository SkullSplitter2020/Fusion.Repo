# -*- coding: utf-8 -*-

'''
    Copyright (C) 2023 realvito

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


def run():
	if mode == 'root': ##### Delete complete old Userdata-Folder to cleanup old Entries // [plugin.video.spotitube v.2.1.9] - 25.09.2020 #####
		DONE = False    ##### Delete old CACHE-Folder to cleanup old Cache // [plugin.video.spotitube v.3.0.4] - 18.02.2023 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join('special://home{0}addons{0}{1}{0}lib{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
		UNO = os.path.join(firstSCRIPT, 'only_at_FIRSTSTART')
		if xbmcvfs.exists(UNO):
			sourceUSER = xbmcvfs.translatePath(os.path.join('special://home{0}userdata{0}addon_data{0}{1}{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(sourceUSER):
				try:
					xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":false}}}}'.format(addon_id))
					shutil.rmtree(sourceUSER, ignore_errors=True)
				except: pass
				xbmcvfs.delete(UNO)
				xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":true}}}}'.format(addon_id))
				xbmc.sleep(500)
				DONE = True
			else:
				xbmcvfs.delete(UNO)
				xbmc.sleep(500)
				DONE = True
		else:
			DONE = True
		if DONE is True: navigator.mainMenu()
	elif mode == 'beatportMain':
		navigator.beatportMain()
	elif mode == 'listBeatportVideos':
		navigator.listBeatportVideos(url, target, limit)
	elif mode == 'billboardMain':
		navigator.billboardMain()
	elif mode == 'listBillboardCharts':
		navigator.listBillboardCharts(url)
	elif mode == 'listBillboardArchive':
		navigator.listBillboardArchive(url)
	elif mode == 'listBillboardVideos':
		navigator.listBillboardVideos(url, target, limit)
	elif mode == 'ddpMain':
		navigator.ddpMain()
	elif mode == 'listDdpYearCharts':
		navigator.listDdpYearCharts(url)
	elif mode == 'listDdpVideos':
		navigator.listDdpVideos(url, target, limit)
	elif mode == 'hypemMain':
		navigator.hypemMain()
	elif mode == 'listHypemMachine':
		navigator.listHypemMachine()
	elif mode == 'listHypemVideos':
		navigator.listHypemVideos(url, target, limit)
	elif mode == 'itunesMain':
		navigator.itunesMain()
	elif mode == 'listItunesVideos':
		navigator.listItunesVideos(url, target, limit)
	elif mode == 'ocMain':
		navigator.ocMain()
	elif mode == 'listOcVideos':
		navigator.listOcVideos(url, target, limit)
	elif mode == 'shazamMain':
		navigator.shazamMain()
	elif mode == 'listShazamGenres':
		navigator.listShazamGenres(url)
	elif mode == 'listShazamVideos':
		navigator.listShazamVideos(url, target, limit)
	elif mode == 'spotifyMain':
		navigator.spotifyMain()
	elif mode == 'listSpotifyPlaylists':
		navigator.listSpotifyPlaylists(url)
	elif mode == 'listSpotifyVideos':
		navigator.listSpotifyVideos(url, target, limit)
	elif mode == 'SearchDeezer':
		navigator.SearchDeezer()
	elif mode == 'listDeezerSelection':
		navigator.listDeezerSelection(url, extras) 
	elif mode == 'listDeezerVideos':
		navigator.listDeezerVideos(url, target, limit, extras, transmit)
	elif mode == 'playTITLE':
		navigator.playTITLE(url)
	elif mode == 'blankFUNC':
		pass # do nothing
	elif mode == 'clearCache':
		navigator.clearCache()
	elif mode == 'aConfigs':
		addon.openSettings()
		xbmc.executebuiltin('Container.Refresh')

run()
