# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon


def translation(id):
	return xbmcaddon.Addon().getLocalizedString(id)


class Client(object):
	CONFIG_SEVER = {
		'specifications': [
		{
			'name': translation(30671),
			'_index': 'shows',
			'short': 'top20days7'
		},
		{
			'name': translation(30672),
			'_index': 'shows',
			'short': 'top20days2'
		},
		{
			'name': translation(30673),
			'_index': 'shows',
			'short': 'movies'
		},
		{
			'name': translation(30674),
			'_index': 'shows',
			'short': 'series'
		},
		{
			'name': translation(30674),
			'_index': 'shows',
			'short': 'serien'
		},
		{
			'name': translation(30675),
			'_index': 'shows',
			'short': 'stations'
		},
		{
			'name': translation(30676),
			'_index': 'shows',
			'short': 'categories'
		},
		{
			'name': translation(30677),
			'_index': 'shows',
			'short': 'comedy'
		},
		{
			'name': translation(30678),
			'_index': 'shows',
			'short': 'dailySoaps'
		},
		{
			'name': translation(30679),
			'_index': 'shows',
			'short': 'dokus'
		},
		{
			'name': translation(30680),
			'_index': 'shows',
			'short': 'highlights'
		},
		{
			'name': translation(30681),
			'_index': 'shows',
			'short': 'justAdded'
		},
		{
			'name': translation(30681),
			'_index': 'shows',
			'short': 'justFound'
		},
		{
			'name': translation(30682),
			'_index': 'shows',
			'short': 'expiring'
		}]
	}

	def __init__(self, records):
		self._records = records

	def get_records(self):
		return self._records
