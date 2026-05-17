#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

ADDON_ID = "plugin.program.skullshelp"

try:
    import xbmc
    import xbmcgui
    import xbmcaddon

    ADDON = xbmcaddon.Addon(ADDON_ID)
    ADDON_PATH = ADDON.getAddonInfo('path')

    xbmc.log(f"sKulls Help: Starting from {ADDON_PATH}", xbmc.LOGINFO)

    LIB_PATH = os.path.join(ADDON_PATH, 'resources', 'lib')
    sys.path.insert(0, LIB_PATH)
    xbmc.log(f"sKulls Help: Lib path = {LIB_PATH}", xbmc.LOGINFO)

    from navigation import NavigationController

    controller = NavigationController()
    controller.show_main_menu()

except Exception as e:
    import traceback
    error_msg = traceback.format_exc()
    try:
        xbmc.log(f"sKulls Help Error: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Fehler", f"Fehler: {str(e)}")
    except:
        pass
    print(error_msg)
    sys.exit(1)