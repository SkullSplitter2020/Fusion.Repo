#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,xbmcvfs

try:
    #py2
    import urlparse
except:
    #py3
    import urllib.parse as urlparse
import os

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')

def get_youtube_playlist(playlist_id):
    return 'plugin://plugin.video.youtube/playlist/%s/' % playlist_id

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path,'resources','icon')
xbmcplugin.setContent(handle=int(sys.argv[1]), content='files')
				
def add_item(name, url, iconimage='', fanart='', isFolder=True, IsPlayable=False):
    urlParams = {'name': name, 'url': url, 'iconimage': iconimage}
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': iconimage, 'thumb': iconimage})
    liz.setInfo('video', {'title': name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=isFolder)
    return ok

icon1=xbmcvfs.translatePath('special://home/addons/'+addonID+'/terrax.jpeg')
icon2=xbmcvfs.translatePath('special://home/addons/'+addonID+'/terrax2.jpeg')
icon4=xbmcvfs.translatePath('special://home/addons/'+addonID+'/zdfh.jpeg')
icon5=xbmcvfs.translatePath('special://home/addons/'+addonID+'/n24d.jpg')
icon6=xbmcvfs.translatePath('special://home/addons/'+addonID+'/arteh.png')
icon7=xbmcvfs.translatePath('special://home/addons/'+addonID+'/arte.jpg')
icon8=xbmcvfs.translatePath('special://home/addons/'+addonID+'/dokustreams.jpg')
icon9=xbmcvfs.translatePath('special://home/addons/'+addonID+'/centauri.jpeg')
icon10=xbmcvfs.translatePath('special://home/addons/'+addonID+'/mayday.jpg')
icon11=xbmcvfs.translatePath('special://home/addons/'+addonID+'/crime.jpg')
icon12=xbmcvfs.translatePath('special://home/addons/'+addonID+'/crime3.jpg')
icon13=xbmcvfs.translatePath('special://home/addons/'+addonID+'/crime2.jpg')
icon14=xbmcvfs.translatePath('special://home/addons/'+addonID+'/gang.jpg')
icon15=xbmcvfs.translatePath('special://home/addons/'+addonID+'/universe.jpg')
icon16=xbmcvfs.translatePath('special://home/addons/'+addonID+'/physik.jpg')
icon17=xbmcvfs.translatePath('special://home/addons/'+addonID+'/history.jpg')
icon18=xbmcvfs.translatePath('special://home/addons/'+addonID+'/wild5.jpg')
icon19=xbmcvfs.translatePath('special://home/addons/'+addonID+'/anna.jpeg')
icon20=xbmcvfs.translatePath('special://home/addons/'+addonID+'/wild12.jpg')
icon21=xbmcvfs.translatePath('special://home/addons/'+addonID+'/reich.jpg')
icon22=xbmcvfs.translatePath('special://home/addons/'+addonID+'/wwt.jpg')
icon23=xbmcvfs.translatePath('special://home/addons/'+addonID+'/schlacht.jpg')
icon24=xbmcvfs.translatePath('special://home/addons/'+addonID+'/war.jpg')
icon25=xbmcvfs.translatePath('special://home/addons/'+addonID+'/tauchen.jpg')
icon26=xbmcvfs.translatePath('special://home/addons/'+addonID+'/tauchen2.jpg')
icon27=xbmcvfs.translatePath('special://home/addons/'+addonID+'/welt.jpg')


def index():
    add_item('WELT Dokus & Reportagen',get_youtube_playlist('PLslDofkqdKI9Lt5PKR2BE3y4LULTMfT3A'),icon27, isFolder=True)
    add_item('Terra X',get_youtube_playlist('PLJY8yZ_0jFwewo3WgBV-Sw3LZO5qdfaZ_'),icon1, isFolder=True)
#    add_item('Terra X II',get_youtube_playlist('PLg-rKdrKbDtlX-Alj0pyJ8BV2UUcU0yEZ'),icon2, isFolder=True)
    add_item('ZDF-History',get_youtube_playlist('PLdLAXSFIvN9E0cUbUNrLmqbaady8WQFK3'),icon4, isFolder=True)
    add_item('N24 Doku',get_youtube_playlist('PLKvsCCC7Bc3AYRXCgI2akIvBikpP7r-fY'),icon5, isFolder=True)
    add_item('ARTE- History ',get_youtube_playlist('PL-t786AQxGO_7Rt3_4O01qKZXm6D-G-Od'),icon6, isFolder=True)
    add_item('ARTE- Dokus und Reportagen ',get_youtube_playlist('PLlQWnS27jXh846YQxXL9VeyoU47xCAmpY'),icon7, isFolder=True)
    add_item('Dokustreams',get_youtube_playlist('PLikmWKyGm7w68KLLD6Vx3brMDnEqwiUHK'),icon8, isFolder=True)
    add_item('Alpha Centauri',get_youtube_playlist('PLikmWKyGm7w4foHDk9XjMc7udzX-lS9ir'),icon9, isFolder=True)
    add_item('MAYDAY -Alarm Im Cockpit',get_youtube_playlist('PLBnu-yd5vmDE5CEiK-2wiY_4_Hae_8MNO'),icon10, isFolder=True)
    add_item('Crime Dokus',get_youtube_playlist('PL8vy1Dmnedmpjwe51g22ts-GjhKYeqnL1'),icon11, isFolder=True)
    add_item('Dokus Kriminalfälle',get_youtube_playlist('PLD9tXDfn3aaOiQsMHzpPQK3fVBtYqo5Hl'),icon12, isFolder=True)
    add_item('Mord Dokus',get_youtube_playlist('PL71TJK-M7RX27K06Bj2-bEDNUiPRU_dPG'),icon13)
    add_item('Ganster Dokus',get_youtube_playlist('PLk9HPyqc6AILC4JrdbTCWRp5jNJqLx4kg'),icon14, isFolder=True)
    add_item('Universum Dokumentationen',get_youtube_playlist('PLybSgyzzjOmk0GXvMkEW0PPiVPUvs3Rgg'),icon15, isFolder=True)
    add_item('DOKU // Physik // Science // Technik // Raumfahrt',get_youtube_playlist('PLEs1C_0f4i7-Y9fQbGjHqxhm6oRMerEEx'),icon16, isFolder=True)
    add_item('Geschichte, chronologisch',get_youtube_playlist('PLCmAcRSgj3IQy579zESYlbuEUn0UILucl'),icon17, isFolder=True)
    add_item('Natur- und Tierdokumentationen',get_youtube_playlist('PL4d-w5KrJjTZZxEb0XKIKLLkZbdWK5iJn'),icon18, isFolder=True)
    add_item('Tier Dokus Anna, Paula und die wilden Tiere ',get_youtube_playlist('PLydq0NtegKH-KFQMy20gfaS4Wee80zCkv'),icon19, isFolder=True)
    add_item('Tierdokumentationen ',get_youtube_playlist('PLOtxwk6mlZ-vOwYSa_EZgtF_6Xs9QrNXm'),icon20, isFolder=True)
    add_item('Doku-Das Dritte Reich',get_youtube_playlist('PLWCh1VrmvgDmxqpmRyslpSzE1XucQ63lO'),icon21, isFolder=True)
    add_item('Doku-2.Weltkrieg 1',get_youtube_playlist('PLPdh1srUHkHMBSQSyoCxRX_Tft7UPtZKI'),icon22, isFolder=True)
    add_item('Doku-2.Weltkrieg 2',get_youtube_playlist('PLB5Igv7tds-k1Z55IIM94K9eUoIsPlgBF'),icon22, isFolder=True)
    add_item('Doku-2.Weltkrieg 3',get_youtube_playlist('PLas7oA026StNicIR-pGRDTbLC9w-i9KMh'),icon22, isFolder=True)
    add_item('Legendäre Schlachten',get_youtube_playlist('PLexOauvOy9YExEsobKvMOXRN8Q1MmymjT'),icon23, isFolder=True)
    add_item('Kriegsfilme  ',get_youtube_playlist('PLsGK3aH9-P9koGCe60moCG4P3Y3SXEwAM'),icon24, isFolder=True)
    add_item('Tauchen',get_youtube_playlist('PL34ba0YZpTzq9ybHk8OOH1RMxnsxm8Lvq'),icon25, isFolder=True)
    add_item('Unterwasser Doku 1.',get_youtube_playlist('PLsGK3aH9-P9kICi2pgw6ygjBgBCZioT83'),icon26, isFolder=True)
    add_item('Unterwasser Doku 2.',get_youtube_playlist('PLi1BIRwUIrR0HX0zhHiHIErpDRLWAtkpC'),icon26, isFolder=True)

    xbmcplugin.endOfDirectory(pluginhandle)
def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

index()