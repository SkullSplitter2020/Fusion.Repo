import xbmcaddon

__plugin__ = '[COLOR pink]DARKLEGION XXX[/COLOR]'
__author__ = 'Dlp'
__credits__ = 'Dlp'

addon = xbmcaddon.Addon(id='plugin.video.vilhaoxxx')
rootDir = addon.getAddonInfo('path')
if rootDir.endswith(';'):
    rootDir = rootDir[:-1]

class Main:
    def __init__(self):
        self.pDialog = None
        self.run()

    def run(self):
        import vilhaoxxx
        vilhaoxxx.Main()

Main()
