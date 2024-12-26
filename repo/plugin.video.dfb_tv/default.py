# -*- coding: utf-8 -*-

'''
    Copyright (C) 2024 realvito

    DFB - Sport

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
	if mode == 'root':
		navigator.mainMenu()
	elif mode == 'listSports_Men':
		navigator.listSports_Men()
	elif mode == 'listSports_Women':
		navigator.listSports_Women()
	elif mode == 'listBroadcasts':
		navigator.listBroadcasts(searching, category, page, limit)
	elif mode == 'SearchDFBTV':
		navigator.SearchDFBTV()
	elif mode == 'listPlaylists':
		navigator.listPlaylists(extras)
	elif mode == 'playVideo':
		navigator.playVideo(url, extras)
	elif mode == 'aConfigs':
		addon.openSettings()
	elif mode == 'iConfigs':
		xbmcaddon.Addon('inputstream.adaptive').openSettings()

run()
