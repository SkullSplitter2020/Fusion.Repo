# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
# showGenre:    48 Stunden
# showEntries:   6 Stunden

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'flimmerstube'
SITE_NAME = 'Flimmerstube'
SITE_ICON = 'flimmerstube.png'

# Global search function is thus deactivated!
if cConfig().getSetting('global_search_' + SITE_IDENTIFIER) == 'false':
    SITE_GLOBAL_SEARCH = False
    logger.info('-> [SitePlugin]: globalSearch for %s is deactivated.' % SITE_NAME)

# Domain Abfrage
DOMAIN = cConfig().getSetting('plugin_' + SITE_IDENTIFIER + '.domain', 'flimmerstube.com') # Domain Auswahl über die xStream Einstellungen möglich
STATUS = cConfig().getSetting('plugin_' + SITE_IDENTIFIER + '_status') # Status Code Abfrage der Domain
ACTIVE = cConfig().getSetting('plugin_' + SITE_IDENTIFIER) # Ob Plugin aktiviert ist oder nicht

URL_MAIN = 'http://' + DOMAIN
# URL_MAIN = 'http://flimmerstube.com'

URL_MOVIES = URL_MAIN + '/video/vic/alle_filme'
URL_SEARCH = URL_MAIN + '/video/shv'
#

def load(): # Menu structure of the site plugin
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    username = cConfig().getSetting('flimmerstube.user')    # Username
    password = cConfig().getSetting('flimmerstube.pass')    # Password
    if username == '' and password == '':                   # If no username and password were set, close the plugin!
        import xbmcgui
        xbmcgui.Dialog().ok(cConfig().getLocalizedString(30241), cConfig().getLocalizedString(30262))   # Info Dialog!
    else:
        oRequest = cRequestHandler('http://flimmerstube.com/index/sub/')
        oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequest.addHeaderEntry('Referer', URL_MAIN)
        oRequest.addParameters('user', username)
        oRequest.addParameters('password', password)
        oRequest.addParameters('rem', '1')
        oRequest.addParameters('a', '2')
        oRequest.addParameters('ajax', '2')
        oRequest.addParameters('_tp_', 'xml')
        oRequest.request()
        params.setParam('sUrl', URL_MOVIES)
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30502), SITE_IDENTIFIER, 'showEntries'), params)  # Movies
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showGenre'), params)    # Genre
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'))   # Search
        cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl)
    if cConfig().getSetting('global_search_' + SITE_IDENTIFIER) == 'true':
        oRequest.cacheTime = 60 * 60 * 48  # 48 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<a[^>]class=[^>]catName[^>][^>]href="([^"]+)"[^>]>([^"]+)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', URL_MAIN + sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False, sSearchPageText = False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if cConfig().getSetting('global_search_' + SITE_IDENTIFIER) == 'true':
        oRequest.cacheTime = 60 * 60 * 6  # 6 Stunden
    if sSearchText:
        oRequest.addHeaderEntry('Referer', entryUrl)
        oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
        oRequest.addParameters('query', sSearchText)
        if '+' in sSearchText:
            oRequest.addParameters('c', '70')
        else:
            oRequest.addParameters('c', '')
    sHtmlContent = oRequest.request()
    pattern = 've-screen"\s+title="([^"]+).*?url[^>]([^")]+).*?href="([^">]+)' #inklusive sYear
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sName, sThumbnail, sUrl in aResult:
        isQuality, sQuality = cParser.parse(sName, 'HD')
        for t in (('(HD)', ''), ('(OmU/HD)', '')): # Ausblenden der Elemente im sName vorne
            sName = sName.replace(*t)
        isYear, sYear = cParser.parse(sName, '(.*?)\((\d*)\)') # Jahr und Name trennen
        for name, year in sYear:
            sName = name
            sYear = year
            break
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        if sThumbnail.startswith('/'):
            sThumbnail = URL_MAIN + sThumbnail
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('movie')
        if isQuality:
            oGuiElement.setQuality(sQuality)
        oGuiElement.setYear(sYear)
        # Sprache GUI Element English und Originalsprache mit Untertiteln
        if '/english_movies' in sUrl:
            oGuiElement.setLanguage('EN')
        if '/omu_originalsprache' in sUrl:
            oGuiElement.setLanguage('OmU')
        params.setParam('entryUrl', URL_MAIN + sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui and not sSearchText and not sSearchPageText:
        # Start Page Function
        isMatchSiteSearch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, """pagesBlockuz(.*?)<hr\s/>""")
        if isMatchSiteSearch:
            isMatch, aResult = cParser.parse(sHtmlContainer, """swchItemA"><span>([\d]+)</span>.*?class="swchItem".*?([\d]+)</span></a><a class="swchItem\sswchItem-next.*?spages[^>][^>]([^']+)""")
            aResult2 = cParser().parse(sHtmlContent, "<span>&raquo;.*?location.href = '([^']+)")
            if aResult2[0] and aResult2[1][0]:
                for Url in aResult2[1]:
                    sNextPage = URL_MAIN + Url
                    params.setParam('sNextPage', sNextPage)
            for sPageActive, sPageLast, sNextPageID in aResult:
                # sPageName = '[I]Seitensuche starten  >>> [/I] Seite ' + str(sPageActive) + ' von ' + str(sPageLast) + ' Seiten  [I]<<<[/I]'
                sPageName = cConfig().getLocalizedString(30284) + str(sPageActive) + cConfig().getLocalizedString(30285) + str(sPageLast) + cConfig().getLocalizedString(30286)
                params.setParam('sNextPageID', sNextPageID)
                params.setParam('sPageLast', sPageLast)
                oGui.searchNextPage(sPageName, SITE_IDENTIFIER, 'showSearchPage', params)
        # End Page Function
        aResult = cParser().parse(sHtmlContent, "spages[^>][^>]([^']+)[^>][^>];return[^>]false;[^>]><span>&raquo;.*?location.href = '([^']+)")
        if aResult[0] and aResult[1][0]:
            for sNr, Url in aResult[1]:
                params.setParam('sUrl', URL_MAIN + Url + sNr)
                oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)

        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl, caching=False).request()
    isMatch, sUrl = cParser().parse(sHtmlContent, 'class="link"[^>]href="([^"]+)')
    if isMatch:
        sHtmlContent2 = cRequestHandler(sUrl[0]).request()
        isMatch, aResult = cParser().parse(sHtmlContent2, 'p><iframe.*?src="([^"]+)')
        if 'bowfile' in aResult[0]: #Wenn Hoster bowfile ist, dann in Container nach dem HD File suchen und direkt ohne Resolver abspielen, siehe getHosterUrl
            sHtmlContent3 = cRequestHandler(aResult[0]).request()
            isMatch, aResult = cParser().parse(sHtmlContent3, 'mp4HD:.?"([^"]+)')

    if isMatch:
        for sUrl in aResult:
            if sUrl.startswith('//'):
                sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if not isMatch:
        pattern = 'vep-title.*?</h1.*?src=.*?http..([\S]+)'
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
        if isMatch:
            for sUrl in aResult:
                if sUrl.startswith('//'):
                    sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    if 'youtube' in sUrl:
        import xbmc
        if not xbmc.getCondVisibility('System.HasAddon(%s)' % 'plugin.video.youtube'):
            xbmc.executebuiltin('InstallAddon(%s)' % 'plugin.video.youtube')
    if 'bowfile' in sUrl:
        return [{'streamUrl': sUrl, 'resolved': True}]
    else:
        return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard(sHeading=cConfig().getLocalizedString(30287))
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH, oGui, sSearchText)

def showSearchPage(): # Suche für die Page Funktion
    params = ParameterHandler()
    sNextPage = params.getValue('sNextPage') # URL mit nächster Seite
    sPageLast = params.getValue('sPageLast') # Anzahl gefundener Seiten
    #sHeading = 'Bitte eine Zahl zwischen 1 und ' + str(sPageLast) + ' wählen.'
    sHeading = cConfig().getLocalizedString(30282) + str(sPageLast)
    sSearchPageText = cGui().showKeyBoard(sHeading=sHeading)
    if not sSearchPageText: return
    sNextSearchPage = sNextPage.split('*')[0].strip() + '*' + sSearchPageText
    showEntries(sNextSearchPage)
    cGui().setEndOfDirectory()