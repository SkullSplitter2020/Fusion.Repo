# -*- coding: utf-8 -*-


class Client(object):
	CONFIG_MYSPASS = {# Startseite=homepage // Videoseite=video
		'START_VIEW': '{}/carousels?filters[page][$eq]={}&sort[0]=order_rank'\
			'&populate[items][populate][video][populate][format][fields]=name'\
			'&populate[items][populate][video][populate][format][fields]=number_of_seasons'\
			'&populate[items][populate][video][populate][format][fields]=long_description'\
			'&populate[items][populate][video][populate][format][fields]=medium_description'\
			'&populate[items][populate][video][populate][format][fields]=short_description'\
			'&populate[items][populate][video][populate][season][fields]=name'\
			'&populate[items][populate][video][populate][episode][fields]=number'
			'&populate[items][populate][format][populate][keyvisual_16_9][fields]=url'\
			'&populate[items][populate][format][populate][keyvisual_5_8][fields]=url'\
			'&populate[items][populate][season][populate][format][fields]=name'\
			'&populate[items][populate][season][populate][format][fields]=medium_description'\
			'&populate[items][populate][season][populate][format][fields]=short_description'\
			'&populate[items][populate][season][populate][keyvisual_16_9][fields]=url'\
			'&populate[items][populate][season][populate][keyvisual_5_8][fields]=url',
		'PAGE_VIEW': '{}/pages?filters[page][$eq]={}&populate[formats][fields]=type'\
			'&populate[formats][fields]=name'\
			'&populate[formats][fields]=number_of_seasons'\
			'&populate[formats][fields]=long_description'\
			'&populate[formats][fields]=medium_description'\
			'&populate[formats][fields]=short_description'\
			'&populate[formats][populate]=keyvisual_16_9'\
			'&populate[formats][populate]=keyvisual_5_8'\
			'&pagination[page]=1&pagination[pageSize]=40',
		'SEAS_VIEW': '{}/formats/{}'\
			'?populate[seasons]=seasons',
		'EPIS_VIEW': '{}/videos?filters[type][$contains]=full_episode'\
			'&filters[format][id][$eq]={}&filters[season][id][$eq]={}'\
			'&populate[format][fields]=name'\
			'&populate[season][fields]=name'\
			'&populate=episode'\
			'&sort[0]=episode.number:asc&sort[1]=special_number:asc'\
			'&pagination[page]={}&pagination[pageSize]=40',
		'CLIPS_VIEW': '{}/videos?filters[type][$contains]=clip'\
			'&filters[format][id][$eq]={}'\
			'&populate[format][fields]=name'\
			'&populate[season][fields]=name'\
			'&populate=episode'\
			'&sort[0]=episode.number:asc&sort[1]=special_number:asc'\
			'&pagination[page]={}&pagination[pageSize]=40',
		'VIDS_VIEW': '{}/videos/{}'\
			'?populate[format][fields]=name'\
			'&populate[season][fields]=name',
		'PLAYS_VIEW': '{}/next-video/{}?',
		'IMAGES_URL': 'https://1403103913.rsc.cdn77.org{}',
		'PLAYER_URL': 'https://1020993654.rsc.cdn77.org{}'
		}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config
