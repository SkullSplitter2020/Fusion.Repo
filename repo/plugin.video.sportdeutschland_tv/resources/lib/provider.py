# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon


def translation(id):
	return xbmcaddon.Addon().getLocalizedString(id)

class Client(object):
	CONFIG_SPORTDEUTSCHLAND = {
		'SPORT_TYPES': 'https://api.sportdeutschland.tv/api/stateless/frontend/menu/sport-types?',
		'SPORT_PROFILE': 'https://search.sportdeutschland.tv/api/v1/profiles/popular?',
		'HOME_LIVENEXT': 'https://api.sportdeutschland.tv/api/stateless/frontend/home/next-livestreams?',
		'TAGS_LIVENEXT': 'https://api.sportdeutschland.tv/api/stateless/frontend/tags/{}/next-livestreams?',
		'TEAM_LIVENEXT': 'https://api.sportdeutschland.tv/api/stateless/frontend/profiles/{}/next-livestreams?',
		'HOME_TOPS': 'https://api.sportdeutschland.tv/api/stateless/frontend/home/top-assets?',
		'TAGS_TOPS': 'https://api.sportdeutschland.tv/api/stateless/frontend/tags/{}/top-assets?',
		'TEAM_TOPS': 'https://api.sportdeutschland.tv/api/stateless/frontend/profiles/{}/top-assets?',
		'TAGS_ASSETS': 'https://api.sportdeutschland.tv/api/stateless/frontend/tags/{}/assets?',
		'TEAM_ASSETS': 'https://api.sportdeutschland.tv/api/stateless/frontend/profiles/{}/assets?',
		'TAGS_TYPES': 'https://api.sportdeutschland.tv/api/stateless/frontend/menu/sport-types/{}?',
		'TAGS_PROFILE': 'https://search.sportdeutschland.tv/api/v1/profiles/by_tag/{}/popular?',
		'SEARCH_PROFILE': 'https://search.sportdeutschland.tv/api/v1/search/profiles?q={}&',
		'SEARCH_VIDEO': 'https://search.sportdeutschland.tv/api/v1/search/assets?q={}&',
		'VIDEO_LINK': 'https://api.sportdeutschland.tv/api/stateless/frontend/assets/{}/{}',
		'PLAY_MUX': 'https://api.sportdeutschland.tv/api/web/personal/asset-token/{}?type={}&playback_id={}',
		'PLAY_LEGACY': 'https://api.sportdeutschland.tv/api/web/personal/asset-token/{}?type=legacy',
		'PLAY_M3U8': 'https://stream.mux.com/{}.m3u8',
		'picks': [
		{
			'title': translation(30621),
			'member': 'livestream',
			'id': 11
		},
		{
			'title': translation(30622),
			'member': 'upcoming',
			'id': 22
		},
		{
			'title': translation(30623),
			'member': 'latest',
			'id': 33
		},
		{
			'title': translation(30624),
			'member': 'highlights',
			'id': 44
		},
		{
			'title': translation(30625),
			'member': 'sporttypes',
			'id': 55
		}],
	}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config
