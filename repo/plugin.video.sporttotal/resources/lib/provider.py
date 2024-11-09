# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon


def translation(id):
	return xbmcaddon.Addon().getLocalizedString(id)


class Client(object):
	CONFIG_SPORTTOTAL = {
		'HOME_MENU': 'https://sporttotal.tv/api/v2/config/menu',
		'HOME_LIVENEXT': 'https://sporttotal.tv/api/v2/75a0f3c0-33b9-4b92-b09b-94f2858f729c/events?event_type={}&resource_type={}',
		'EVENT_DATES': 'https://sporttotal.tv/api/v2/event_dates',
		'EVENT_STARTS': 'https://sporttotal.tv/api/v2/75a0f3c0-33b9-4b92-b09b-94f2858f729c/events?event_type=all_events&resource_type={}&start_time_gt={}&start_time_lt={}&page={}&per_page={}',
		'SEARCH_ALL': 'https://sporttotal.tv/api/v2/searches?query={}&page={}&per_page={}',
		'LIVE_EVENT': 'https://sporttotal.tv/api/v2/{}/events?event_type=live&resource_type={}&page={}&per_page={}',
		'COMING_EVENT': 'https://sporttotal.tv/api/v2/{}/events?event_type=upcoming&resource_type={}&page={}&per_page={}',
		'LATEST_EVENT': 'https://sporttotal.tv/api/v2/{}/events?event_type=latest&resource_type={}&page={}&per_page={}',
		'HIGH_EVENT': 'https://sporttotal.tv/api/v2/{}/events?event_type=highlights&resource_type={}&page={}&per_page={}',
		'SPORT_CONTESTS': 'https://sporttotal.tv/api/v2/sports/{}/competitions?page={}&per_page={}',
		'SPORT_TEAMS': 'https://sporttotal.tv/api/v2/sports/{}/teams?page={}&per_page={}',
		'VIDEO_LINK': 'https://sporttotal.tv/api/v2/{}/{}',
		'picks': [
		{
			'title': translation(30621),
			'member': 'live',
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
			'member': 'competitions',
			'id': 55
		},
		{
			'title': translation(30626),
			'member': 'teams',
			'id': 66
		}],
		'header': {
			'Origin': 'https://sporttotal.tv',
			'Referer': 'https://sporttotal.tv/'
		}
	}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config
