# -*- coding: utf-8 -*-

# edit 2024-12-05 kasi

if __name__ == "__main__":
	import sys, xbmc, json
	from resources.lib import utils, vjackson
	if utils.PY2:
		if not xbmc.getCondVisibility("System.HasAddon(script.module.futures)"):
			xbmc.executebuiltin('InstallAddon(script.module.futures)')
			xbmc.executebuiltin('SendClick(11)')
	else:
		if not xbmc.getCondVisibility("System.HasAddon(script.module.infotagger)"):
			xbmc.executebuiltin('InstallAddon(script.module.infotagger)')
			xbmc.executebuiltin('SendClick(11)')
		if not xbmc.getCondVisibility("System.HasAddon(inputstream.ffmpegdirect)"):
			xbmc.executebuiltin('InstallAddon(inputstream.ffmpegdirect)')
			xbmc.executebuiltin('SendClick(11)')
	params = dict(utils.parse_qsl(sys.argv[2][1:]))

	tv = params.get("name")
	action = params.pop("action", None)
	if action in ["live", "a_z_tv", "group_tv", "makem3u", "favchannels", "channels", "get_genres", "choose", "choose_portal", "new_mac"]:
		from resources.lib import vjlive
	if tv:
		from resources.lib import vjlive
		if action == "addTvFavorit": vjlive.change_favorit(tv)
		elif action == "delTvFavorit": vjlive.change_favorit(tv, True)
		else: vjlive.livePlay(tv, params.get('type'), params.get('group'))
	elif action == None: vjackson._index(params)
	elif action == "choose": vjlive.choose()
	elif action == "get_genres": vjlive.get_genres()
	elif action == "choose_portal": vjlive.choose_portal()
	elif action == "new_mac": vjlive.new_mac()
	elif action == "clear": utils.clear()
	elif action == "delete_search": utils.delete_search(params)
	elif action == "delallTvFavorit":
		utils.addon.setSetting("favs", "[]")
		xbmc.executebuiltin('Container.Refresh')
	# edit kasi
	elif action == "live": vjlive.live()
	elif action == 'a_z_tv': vjlive.a_z_tv()
	elif action == "group_tv": vjlive.group_tv(params.get('type'))
	elif action == "channels": vjlive.channels(params.get('items'), params.get('type'), params.get('group'))
	elif action == "settings": utils.addon.openSettings(sys.argv[1])
	elif action == "favchannels": vjlive.favchannels()
	elif action == "makem3u": vjlive.makem3u()
	else: getattr(vjackson, "_%s" % action)(params)