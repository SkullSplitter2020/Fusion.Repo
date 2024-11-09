#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmcvfs


def fix_encoding(path):
    if sys.platform.startswith('win'):
        return unicode(path, 'utf-8')
    else:
        return unicode(path, 'utf-8').encode('ISO-8859-1')


addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')


def set_content(content):
    xbmcplugin.setContent(int(sys.argv[1]), content)


def set_view_mode(view_mode):
    xbmc.executebuiltin('Container.SetViewMode(%s)' % (view_mode))


def set_end_of_directory(succeeded=True, updateListing=False, cacheToDisc=False):
    xbmcplugin.endOfDirectory(
        handle=int(sys.argv[1]),
        succeeded=succeeded,
        updateListing=updateListing,
        cacheToDisc=cacheToDisc
    )


def get_youtube_live_stream(channel_id):
    return 'plugin://plugin.video.youtube/play/?channel_id=%s&live=1' % channel_id


def get_youtube_video(video_id):
    return 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id


def get_youtube_playlist(playlist_id):
    return 'plugin://plugin.video.youtube/playlist/%s/' % playlist_id


def get_youtube_channel(channel_id):
    return 'plugin://plugin.video.youtube/channel/%s/' % channel_id


addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path, 'icon')
xbmcplugin.setContent(handle=int(sys.argv[1]), content='files')
fanart=xbmcvfs.translatePath('special://home/addons/'+addonID+'/fanart.png')

def add_item(name, url, icon='', fanart=fanart, isFolder=True, IsPlayable=False):
    fanart=xbmcvfs.translatePath('special://home/addons/'+addonID+'/fanart.png')
    urlParams = {'name': name, 'url': url, 'icon': icon, 'fanart': fanart}
    liz = xbmcgui.ListItem(name, icon, fanart)
    liz.setArt({'icon': icon, 'fanart' : fanart})
    ok = xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]),
        url=url,
        listitem=liz,
        isFolder=isFolder
    )
    return ok


# ------------------- #
set_view_mode('50')
#set_content('music')
# ----------------------------------------------------------------------------------------------- #

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
icon1 = xbmcvfs.translatePath('special://home/addons/'+addonID+'/GT100.jpg')
icon2 = xbmcvfs.translatePath('special://home/addons/'+addonID+'/100SChlager.jpg')
icon4=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Itunes.webp')
icon5=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Billboard.jpg')
icon6=xbmcvfs.translatePath('special://home/addons/'+addonID+'/MTV.jpg')
icon7=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Tomorrow.jpg')
icon8=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Pop Music.jpeg')
icon9=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Dance2.jpg')
icon10=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Dance5.jpg')
icon11=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Dance4.jpg')
icon12=xbmcvfs.translatePath('special://home/addons/'+addonID+'/vevo.jpg')
icon13=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Deluxemusic.png')
icon14=xbmcvfs.translatePath('special://home/addons/'+addonID+'/2000er Hits.jpg')
icon15=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Eurodance.jpg')
icon16=xbmcvfs.translatePath('special://home/addons/'+addonID+'/90s.jpg')
icon17=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Disco.jpg')
icon18=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Neue deutsche Welle.jpg')
icon19=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Top 70er.jpg')
icon20=xbmcvfs.translatePath('special://home/addons/'+addonID+'/60Ss.jpg')
icon21=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Heavy Metal Rock.png')
icon22=xbmcvfs.translatePath('special://home/addons/'+addonID+'/AC-DC.jpg')
icon23=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Metallica.jpg')
icon24=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Rock Musik.jpg')
icon25=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Party Rock.jpg')
icon26=xbmcvfs.translatePath('special://home/addons/'+addonID+'/70er Rock.png')
icon27=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Love Songs.jpg')
icon3=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Musik Mix.jpg')
icon28=xbmcvfs.translatePath('special://home/addons/'+addonID+'/Kuschel Rock.jpg')
icon29=xbmcvfs.translatePath('special://home/addons/'+addonID+'/reggea.png')
fanart=xbmcvfs.translatePath('special://home/addons/'+addonID+'/fanart.png')



add_item('German TOP 100 Single Charts', get_youtube_playlist('PL3-sRm8xAzY89yb_OB-QtcCukQfFe864A'), icon1, fanart=fanart)
add_item('Top 100 Schlager Charts', get_youtube_playlist('PLB5axqo_BYe1JqK7mXkjhx-4p_qiAw-5I'), icon2, fanart=fanart)
add_item('iTunes Top 100 US Hip Hop Rap Songs',get_youtube_playlist('PLUarU1HDBmlwebnr2ynTGDdMxKJEDWNnN'),icon4, fanart=fanart)
add_item('Billboard Charts',get_youtube_playlist('PLD7SPvDoEddZUrho5ynsBfaI7nqhaNN5c'),icon5, fanart=fanart)
add_item('MTV Hits 2021 - Top 100 Charts Germany"',get_youtube_playlist('PL3-sRm8xAzY-YDhgZbycXLPnsue_mhU6B'),icon6, fanart=fanart)
add_item('Tomorrowland,Parokaville,Defcon,Qlimax,Goa und Psytrance Festival',get_youtube_playlist('PLsGK3aH9-P9krMatVVQwTuraacMknlAeB'),icon7, fanart=fanart)
add_item('Best Pop Songs',get_youtube_playlist('PL4o29bINVT4EG_y-k5jGoOu3-Am8Nvi10'),icon8, fanart=fanart)
add_item('Best Sounds of Summer',get_youtube_playlist('PLMC9KNkIncKtsacKpgMb0CVq43W80FKvo'),icon9, fanart=fanart)
add_item('HD Musik Mix',get_youtube_playlist('PLsGK3aH9-P9nqEH-M-TKEnAcBNxhq1ljq'),icon3, fanart=fanart)
add_item('Now Dance Musik',get_youtube_playlist('PLWlTX25IDqIwqowTsJmGhqxUWU_6qgG1W'),icon10, fanart=fanart)
add_item('Dance Hits',get_youtube_playlist('PL6Go6XFhidEAH6LrK-RKxR5xwhdZ0g4vm'),icon11, fanart=fanart)
add_item('Vevo Hits',get_youtube_playlist('PLDIoUOhQQPlWvtxdeVTG3i7-SlSN0jfWj'),icon12, fanart=fanart)
add_item('Deluxe Music',get_youtube_playlist('PLxhnpe8pN3TlDGk0xqmLejhKU8Yi_I-fE'),icon13, fanart=fanart)
add_item('2000s Party Music Hits',get_youtube_playlist('PL39z-AAkkats9VE4V8gdQyIjqp21nao9p'),icon14, fanart=fanart)
add_item('Best Eurodance Songs of 90er',get_youtube_playlist('PLVf3PXRSPQRarUyt_B_X7O1fm9mGpeqn4'),icon15, fanart=fanart)
add_item('Greatest 90s Music Hits',get_youtube_playlist('PL7DA3D097D6FDBC02'),icon16, fanart=fanart)
add_item('Best of 80-90er Hits',get_youtube_playlist('PLGBuKfnErZlCZed3VIG70mQBHPH7tKJ6D'),icon17, fanart=fanart)
add_item('Neue Deutsche Welle 80s',get_youtube_playlist('PLd5xnond3B5Q8RQpGlrlvZv0n4_hpvxNv'),icon18, fanart=fanart)
add_item('Best of the 70er',get_youtube_playlist('PL09eGQfW13QjtcB0nITNYP56g8OMKe0uc'),icon19, fanart=fanart)
add_item('Greatest hits of the 60s',get_youtube_playlist('PLs5nLtKbGBVOZBCzgXxcN9fyCz6sQ1fab'),icon20, fanart=fanart)
add_item('Heavy Metal',get_youtube_playlist('PLWUXmX2htJ7Nx2_luG8WAVEnShOW-lGal'),icon21, fanart=fanart)
add_item('AC/DC',get_youtube_playlist('PLQlc99hV-nkGWDaG-gJxwOfqp8jxyHaaQ'),icon22, fanart=fanart)
add_item('Metallica',get_youtube_playlist('PL2D4A44B959D87893'),icon23, fanart=fanart)
add_item('Best Rock Music',get_youtube_playlist('PLQ1TuSoOt3w3aQr-obgpzr7EeeM_shwvp'),icon24, fanart=fanart)
add_item('Party Rock Songs',get_youtube_playlist('PLoumn5BIsUDdTFSnx5fSfQHQbnFtAJ5D2'),icon25, fanart=fanart)
add_item('70 Rock Music',get_youtube_playlist('PLAB1BFD67033229B4'),icon26, fanart=fanart)
add_item('Love Songs.',get_youtube_playlist('PL6BA2D5208E8EF161'),icon27, fanart=fanart)
add_item('Kuschelrock',get_youtube_playlist('PL4DpwjwvhozHu4cQH7VZAASvcEFF_Hioa'),icon28, fanart=fanart)
add_item('Best Reggae Music',get_youtube_playlist('PLb2aZl2AJg_VpTIQennzYzQVrA_fgRg7-'),icon29, fanart=fanart)


set_end_of_directory()
