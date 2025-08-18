import xbmc
import xbmcaddon

def debug_log(msg):
    addon = xbmcaddon.Addon()
    if addon.getSettingBool('enable_debug'):
        xbmc.log(f"[SKULLS-WP DEBUG] {msg}", xbmc.LOGINFO)