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

icon11=xbmcvfs.translatePath('special://home/addons/'+addonID+'/vavooS.png')
icon15=xbmcvfs.translatePath('special://home/addons/'+addonID+'/vavooF.png')

fanartvavoo=xbmcvfs.translatePath('special://home/addons/'+addonID+'/fanartvavoo.jpg')


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


def index():
    add_item("[B][COLORorange]V[/COLOR]AVOO.FiLME[/B]","plugin://plugin.video.vavooto/?action=indexMovie",icon15)
    add_item("[B][COLORorange]V[/COLOR]AVOO.SERiEN[/B]","plugin://plugin.video.vavooto/?action=indexSerie",icon11)

   

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




