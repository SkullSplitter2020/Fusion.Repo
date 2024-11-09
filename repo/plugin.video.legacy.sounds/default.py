# -*- coding: utf-8 -*-
#------------------------------------------------------------
# copyright by Team Legacy / 
#------------------------------------------------------------


import os
import sys
import plugintools
import xbmc
import xbmcaddon, xbmcplugin
from xbmcaddon import Addon

addonID = 'plugin.video.legacy.sounds'
addon = Addon(addonID)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')
fanart = local.getAddonInfo('fanart')
xbmcplugin.setContent(handle=int(sys.argv[1]), content='files')

YOUTUBE_CHANNEL_ID1 = "PLRbAgAjyBgD_g1-IIlaXUcjtdj11CIizl"
YOUTUBE_CHANNEL_ID2 = "PL3oW2tjiIxvSPjTj_NCxrW5QtBPvIAbCg"
YOUTUBE_CHANNEL_ID3 = "PLjzeyhEA84sS6ogo2mXWdcTrL2HRfJUv8"
YOUTUBE_CHANNEL_ID4 = "PLZ6k8u-wUAXrGbyfmJERlnIc8frGKJRlt"
YOUTUBE_CHANNEL_ID5 = "PLa_P78159vTOWUeQQSuPLp7R-B9TdTbDu"
YOUTUBE_CHANNEL_ID5a = "PLkqz3S84Tw-RncuqzrzwThBX80FHOHP38"
YOUTUBE_CHANNEL_ID5b = "PLEeYc1iVnEfhVDIEmYnJIux1eQqRSsnNT"
YOUTUBE_CHANNEL_ID6 = "PLB5axqo_BYe1JqK7mXkjhx-4p_qiAw-5I"
YOUTUBE_CHANNEL_ID7 = "PL6Go6XFhidEAH6LrK-RKxR5xwhdZ0g4vm"
YOUTUBE_CHANNEL_ID8 = "PLxA687tYuMWhkqYjvAGtW_heiEL4Hk_Lx"
YOUTUBE_CHANNEL_ID9 = "PLKsiRyayPqRL5sVgd7zL6s24Vbk7yjqS4"
YOUTUBE_CHANNEL_ID10 = "PLgyvcAoYcg6tWTgAaW-01ShB7YAnPdZQ2"
YOUTUBE_CHANNEL_ID11 = "PL4aSZKm23GKZdRcr1MX6iBD-eil5TmQvd"
YOUTUBE_CHANNEL_ID12 = "PL3oW2tjiIxvQWubWyTI8PF80gV6Kpk6Rr"
YOUTUBE_CHANNEL_ID12a = "PL42VaKa05JDZ8X3EE5ZS5jDDLSwgIzUgW"
YOUTUBE_CHANNEL_ID12b = "PLs-kfwmk-th7qSMbgpg3Fq6XQQsgFA02b"
YOUTUBE_CHANNEL_ID13 = "UCPKT_csvP72boVX0XrMtagQ/videos"
YOUTUBE_CHANNEL_ID14 = "/UCUknBTWMDCzSggZ_-AgQAbA"
YOUTUBE_CHANNEL_ID15 = "PL21_DgyQIEJ2m30HP_4ChFsPLroRGmfx9"
YOUTUBE_CHANNEL_ID16 = "PLReWWDR05E6tyX6fBRR-0KzRGlBQB8Gvf"
YOUTUBE_CHANNEL_ID17 = "UUdXETutLndnLf5-DOuZz8ZA"
YOUTUBE_CHANNEL_ID18 = "UCT4bwOkXfaIiP0Ey_8Fsd9A"
YOUTUBE_CHANNEL_ID19 = "PLD054C3FEEDF2A3E4"
YOUTUBE_CHANNEL_ID20 = "PLXd6pgsETjgsn5RFu0LVEzIPUft2z4YaR"
YOUTUBE_CHANNEL_ID21 = "PLImmaOPbiVxrpWGBhQvmUma-Chkv4Y02v"
YOUTUBE_CHANNEL_ID22 = "PLImmaOPbiVxqkg_p4jhem4L7r6hUy-EZ-"
YOUTUBE_CHANNEL_ID23 = "PLZwMgILApDwtOay_hMVDuU2j7_kYGImas"
YOUTUBE_CHANNEL_ID24 = "VEVO"
YOUTUBE_CHANNEL_ID25 = "PLvFYFNbi-IBFeP5ALr50hoOmKiYRMvzUq"
YOUTUBE_CHANNEL_ID26 = "PLirAqAtl_h2pRAtj2DgTa3uWIZ3-0LKTA"
YOUTUBE_CHANNEL_ID27 = "TheWeekndVEVO"
YOUTUBE_CHANNEL_ID28 = "kontor"
YOUTUBE_CHANNEL_ID29 = "PLD59F30B914AD6B1C"
YOUTUBE_CHANNEL_ID30 = "PLn8zSx25Q9jn_OM8ofI2Yvz9TcDo7BRY7"
YOUTUBE_CHANNEL_ID31 = "PLP32wGpgzmIlDFQuxl1qeH33hJJSq8wfe"
YOUTUBE_CHANNEL_ID32 = "PLP32wGpgzmIlDFQuxl1qeH33hJJSq8wfe"
YOUTUBE_CHANNEL_ID33 = "PLRZlMhcYkA2EQSwaeOeZnJ1nOfpZTsMuS"
YOUTUBE_CHANNEL_ID34 = "PLMmqTuUsDkRKlyfBfYUnYrkj1imKn77LM"
YOUTUBE_CHANNEL_ID35 = "hVdJkWvwzHw"


# Entry point
def run():
    plugintools.log("Musik.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        pass
    
    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("Musik.main_list "+repr(params))
   
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Charts----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )


    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[/COLOR][B][COLOR skyblue]Charts [/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID1+"/",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Charts.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Charts.jpg",
        folder=True )


    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]German Top 100[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID2+"/",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/German_100.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/German_100.jpg",
        folder=True )

    
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Charts Mix live set[/COLOR][/B]",
        url="plugin://plugin.video.youtube/channel/UCUknBTWMDCzSggZ_-AgQAbA/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/charts.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/charts.jpg",
        folder=True )	
	
		
   
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Hip Hop and Black----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )

		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Hip Hop Charts[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID4+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/hip_hop.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/hip_hop.jpg",
        folder=True )

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Hip Hop und R&B Songs 2018[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID33+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/mix.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/mix.jpg",
        folder=True )
		
		
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Schlager----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )		
		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Party Schlager[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID5+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Partyschlager.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Partyschlager.jpg",
        folder=True )

		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Schlager Charts[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID6+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/SchlagerCharts.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/SchlagerCharts.jpg",
        folder=True )
		
		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Best of Schlager[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID5a+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/best of s.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/best of s.jpg",
        folder=True )		
				
		
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Rock----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )		
		
		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Rock[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID12+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Rock.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Rock.jpg",
        folder=True )		


    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Rock am Ring[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID12a+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/ring.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/ring.jpg",
        folder=True )		
		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Deutsch Rock[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID12b+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/dr.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/dr.jpg",
        folder=True )				
		
		
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Dance/Pop----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )		
		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Dance[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID7+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Dance.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Dance.jpg",
        folder=True )
	
	
	
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Pop[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID8+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/pop.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/pop.jpg",
        folder=True )	

		
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Electro----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )		
	
	
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Kontor.TV[/COLOR][/B]",
        url="plugin://plugin.video.youtube/user/"+YOUTUBE_CHANNEL_ID28+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/kontor.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/kontor.jpg",
        folder=True )		
		
		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Deep House[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID3+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/deep_house.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/deep_house.jpg",
        folder=True )		
		
		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Electro[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID9+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Electro.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Electro.jpg",
        folder=True )		
		
	
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]House[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID10+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/house.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/house.jpg",
        folder=True )
	

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Minimal[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID11+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/Minimal.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/Minimal.jpg",
        folder=True )	
		
		
    plugintools.add_item( 
        #action="", 
		title=" [COLOR gold]-->[B][COLOR skyblue]EMH Music[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID19+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/EMH Music.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/EMH Music.jpg",
        folder=True )		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]TOP 100 Minimal Songs 2018[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID34+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/minimaltop.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/minimaltop.jpg",
        folder=True )		
		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Goa[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID29+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/goa.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/goa.jpg",
        folder=True )		


    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Goa Waldfrieden[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID30+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/waldf.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/waldf.jpg",
        folder=True )				
		
		
    plugintools.add_item( 
        title=" [B][COLOR gold]----------Vevo----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=False )		
		
		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]Vevo[/COLOR][/B]",
        url="plugin://plugin.video.youtube/user/"+YOUTUBE_CHANNEL_ID24+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/vevo.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/vevo.jpg",
        folder=True )		
		

    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]TaylorSwiftVEVO[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID25+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/TaylorSwiftVEVO.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/TaylorSwiftVEVO.jpg",
        folder=True )		

	
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]LuisFonsiVEVO[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID26+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/LuisFonsiVEVOjpg.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/LuisFonsiVEVOjpg.jpg",
        folder=True )		
	
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]New R&B Videos on Vevo![/COLOR][/B]",
        url="plugin://plugin.video.youtube/user/"+YOUTUBE_CHANNEL_ID27+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/New R&B Videos on Vevo!.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/New R&B Videos on Vevo!.jpg",
        folder=True )	


    plugintools.add_item( 
        title=" [B][COLOR gold]----------MTV----------[/COLOR][/B]",
        url="",
        thumbnail="special://home/addons/plugin.video.legacy.sounds/data/icon.png",
        fanart="special://home/addons/plugin.video.legacy.sounds/fanart.jpg",
        folder=True )	

		
    plugintools.add_item( 
        #action="", 
        title=" [COLOR gold]-->[B][COLOR skyblue]MTV Hits[/COLOR][/B]",
        url="plugin://plugin.video.youtube/playlist/"+YOUTUBE_CHANNEL_ID32+"/",
		thumbnail="special://home/addons/plugin.video.legacy.sounds/data/mtvh.jpg",
        fanart="special://home/addons/plugin.video.legacy.sounds/data/mtvh.jpg",
        folder=True )					
	
	
	
	
	
	
	
run()
