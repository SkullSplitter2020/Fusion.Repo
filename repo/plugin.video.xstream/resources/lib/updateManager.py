# -*- coding: utf-8 -*-
# Python 3

import os, sys
import shutil
import json
import requests
import zipfile

from xbmcaddon import Addon
from requests.auth import HTTPBasicAuth
from xbmcgui import Dialog
from resources.lib.config import cConfig
from xbmc import LOGINFO as LOGNOTICE, LOGERROR, LOGWARNING, log, executebuiltin, getCondVisibility, getInfoLabel
from xbmcvfs import translatePath


# Text/Überschrift im Dialog
PLUGIN_NAME = Addon().getAddonInfo('name')  # ist z.B. 'xstream'
PLUGIN_ID = Addon().getAddonInfo('id')
HEADERMESSAGE = cConfig().getLocalizedString(30151)
LOGMESSAGE = cConfig().getLocalizedString(30166)

# Resolver
def resolverUpdate(silent=False):
    # Nightly Branch
    if Addon().getSetting('resolver.branch') == 'nightly':
        username = 'fetchdevteam'
        resolve_dir = 'snipsolver'
        resolve_id = 'script.module.resolveurl'
        # Abfrage aus den Einstellungen welcher Branch
        branch = 'nightly'
        token = ''

        try:
            return UpdateResolve(username, resolve_dir, resolve_id, branch, token, silent)
        except Exception as e:
            log(' -> [updateManager]: Exception Raised: %s' % str(e), LOGERROR)
            Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + resolve_id + cConfig().getLocalizedString(30157))
            return
    else:
        # Release Branch https://github.com/Gujal00/ResolveURL
        username = 'Gujal00'
        resolve_dir = 'ResolveURL'
        resolve_id = 'script.module.resolveurl'
        # Abfrage aus den Einstellungen welcher Branch
        branch = 'master'
        token = ''

        try:
            return UpdateResolve(username, resolve_dir, resolve_id, branch, token, silent)
        except Exception as e:
            log(' -> [updateManager]: Exception Raised: %s' % str(e), LOGERROR)
            Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + resolve_id + cConfig().getLocalizedString(30157))
            return


# xStream Dev
def xStreamDevUpdate(silent=False):
    username = Addon().getSettingString('xstream.dev.username')
    plugin_id = Addon().getSettingString('xstream.dev.id')
    branch = Addon().getSettingString('xstream.dev.branch')
    token = Addon().getSettingString('xstream.dev.token')
    try:
        return Update(username, plugin_id, branch, token, silent)
    except Exception as e:
        log(' -> [updateManager]: Exception Raised: %s' % str(e), LOGERROR)
        Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + plugin_id + cConfig().getLocalizedString(30157))
        return False

# Update Resolver
def UpdateResolve(username, resolve_dir, resolve_id, branch, token, silent):
    REMOTE_PLUGIN_COMMITS = "https://api.github.com/repos/%s/%s/commits/%s" % (username, resolve_dir, branch)   # Github Commits
    REMOTE_PLUGIN_DOWNLOADS = "https://api.github.com/repos/%s/%s/zipball/%s" % (username, resolve_dir, branch) # Github Downloads
    PACKAGES_PATH = translatePath(os.path.join('special://home/addons/packages/'))  # Packages Ordner für Downloads
    ADDON_PATH = translatePath(os.path.join('special://home/addons/packages/', '%s') % resolve_id)  # Addon Ordner in Packages
    INSTALL_PATH = translatePath(os.path.join('special://home/addons/', '%s') % resolve_id) # Installation Ordner
    
    auth = HTTPBasicAuth(username, token)
    log(LOGMESSAGE + ' -> [updateManager]: %s: - Search for updates.' % resolve_id, LOGNOTICE)
    try:
        ADDON_DIR = translatePath(os.path.join('special://userdata/addon_data/', '%s') % resolve_id) # Pfad von ResolveURL Daten
        LOCAL_PLUGIN_VERSION = os.path.join(ADDON_DIR, "update_sha")    # Pfad der update.sha in den ResolveURL Daten
        LOCAL_FILE_NAME_PLUGIN = os.path.join(ADDON_DIR, 'update-' + resolve_id + '.zip')
        if not os.path.exists(ADDON_DIR): os.mkdir(ADDON_DIR)
        
        if Addon().getSetting('enforceUpdate') == 'true':
            if os.path.exists(LOCAL_PLUGIN_VERSION): os.remove(LOCAL_PLUGIN_VERSION)
            
        commitXML = _getXmlString(REMOTE_PLUGIN_COMMITS, auth)  # Commit Update
        if commitXML:
            isTrue = commitUpdate(commitXML, LOCAL_PLUGIN_VERSION, REMOTE_PLUGIN_DOWNLOADS, PACKAGES_PATH, resolve_dir, LOCAL_FILE_NAME_PLUGIN, silent, auth)
            
            if isTrue is True:
                log(LOGMESSAGE + ' -> [updateManager]: %s: - download new update.' % resolve_id, LOGNOTICE)
                shutil.make_archive(ADDON_PATH, 'zip', ADDON_PATH)
                shutil.unpack_archive(ADDON_PATH + '.zip', INSTALL_PATH)
                log(LOGMESSAGE + ' -> [updateManager]: %s: - install new update.' % resolve_id, LOGNOTICE)
                if os.path.exists(ADDON_PATH + '.zip'): os.remove(ADDON_PATH + '.zip')                
                if silent is False: Dialog().ok(LOGMESSAGE, cConfig().getLocalizedString(30158) + resolve_id + cConfig().getLocalizedString(30159))
                log(LOGMESSAGE + ' -> [updateManager]: %s: - update completed.' % resolve_id, LOGNOTICE)
                return True
            elif isTrue is None:
                log(LOGMESSAGE + ' -> [updateManager]: %s: - no update available.' % resolve_id, LOGNOTICE)
                if silent is False: Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30160) + resolve_id + cConfig().getLocalizedString(30161))
                return None

        log(LOGMESSAGE + ' -> [updateManager]: %s: - Error updating!' % resolve_id, LOGERROR)
        Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + resolve_id + cConfig().getLocalizedString(30157))
        return False
    except:
        log(LOGMESSAGE + ' -> [updateManager]: %s: - Error updating!' % resolve_id, LOGERROR)
        Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + resolve_id + cConfig().getLocalizedString(30157))

# xStream Update
def Update(username, plugin_id, branch, token, silent):
    REMOTE_PLUGIN_COMMITS = "https://api.github.com/repos/%s/%s/commits/%s" % (username, plugin_id, branch)
    REMOTE_PLUGIN_DOWNLOADS = "https://api.github.com/repos/%s/%s/zipball/%s" % (username, plugin_id, branch)
    auth = HTTPBasicAuth(username, token)
    log(LOGMESSAGE + ' -> [updateManager]: %s: - Search for updates.' % plugin_id, LOGNOTICE)
    try:
        ADDON_DIR = translatePath(os.path.join('special://userdata/addon_data/', '%s') % plugin_id)
        LOCAL_PLUGIN_VERSION = os.path.join(ADDON_DIR, "update_sha")
        LOCAL_FILE_NAME_PLUGIN = os.path.join(ADDON_DIR, 'update-' + plugin_id + '.zip')
        if not os.path.exists(ADDON_DIR): os.mkdir(ADDON_DIR)
        # ka - Update erzwingen
        if Addon().getSetting('enforceUpdate') == 'true':
            if os.path.exists(LOCAL_PLUGIN_VERSION): os.remove(LOCAL_PLUGIN_VERSION)

        path = translatePath(os.path.join('special://home/addons/', '%s') % plugin_id)
        commitXML = _getXmlString(REMOTE_PLUGIN_COMMITS, auth)
        if commitXML:
            isTrue = commitUpdate(commitXML, LOCAL_PLUGIN_VERSION, REMOTE_PLUGIN_DOWNLOADS, path, plugin_id,
                                  LOCAL_FILE_NAME_PLUGIN, silent, auth)
            if isTrue is True:
                log(LOGMESSAGE + ' -> [updateManager]: %s: - download new update.' % plugin_id, LOGNOTICE)
                if silent is False: Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30158) + plugin_id + cConfig().getLocalizedString(30159))
                log(LOGMESSAGE + ' -> [updateManager] %s: - install new update.' % plugin_id, LOGNOTICE)
                return True
            elif isTrue is None:
                log(LOGMESSAGE + ' -> [updateManager]: %s: - no update available.' % plugin_id, LOGNOTICE)
                if silent is False: Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30160) + plugin_id + cConfig().getLocalizedString(30161))
                return None

        log(LOGMESSAGE + ' -> [updateManager]: %s: - Error updating!' % plugin_id, LOGERROR)
        Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + plugin_id + cConfig().getLocalizedString(30157))
        return False
    except:
        log(LOGMESSAGE + ' -> [updateManager]: %s: - Error updating!' % plugin_id, LOGERROR)
        Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30156) + plugin_id + cConfig().getLocalizedString(30157))


def commitUpdate(onlineFile, offlineFile, downloadLink, LocalDir, plugin_id, localFileName, silent, auth):
    try:
        jsData = json.loads(onlineFile)
        if not os.path.exists(offlineFile) or open(offlineFile).read() != jsData['sha']:
            log(LOGMESSAGE + ' -> [updateManager]: %s: - Start updating!' % plugin_id, LOGNOTICE)
            isTrue = doUpdate(LocalDir, downloadLink, plugin_id, localFileName, auth)
            if isTrue is True:
                try:
                    open(offlineFile, 'w').write(jsData['sha'])
                    return True
                except:
                    return False
            else:
                return False
        else:
            return None
    except Exception:
        os.remove(offlineFile)
        log(' -> [updateManager]: RateLimit reached')
        return False


def doUpdate(LocalDir, REMOTE_PATH, Title, localFileName, auth):
    try:
        response = requests.get(REMOTE_PATH, auth=auth)  # verify=False,
        if response.status_code == 200:
            open(localFileName, "wb").write(response.content)
        else:
            return False
        updateFile = zipfile.ZipFile(localFileName)
        removeFilesNotInRepo(updateFile, LocalDir)
        for index, n in enumerate(updateFile.namelist()):
            if n[-1] != "/":
                dest = os.path.join(LocalDir, "/".join(n.split("/")[1:]))
                destdir = os.path.dirname(dest)
                if not os.path.isdir(destdir):
                    os.makedirs(destdir)
                data = updateFile.read(n)
                if os.path.exists(dest):
                    os.remove(dest)
                f = open(dest, 'wb')
                f.write(data)
                f.close()
        updateFile.close()
        os.remove(localFileName)
        executebuiltin("UpdateLocalAddons()")
        return True
    except:
        log(LOGMESSAGE + ' -> [updateManager]: doUpdate not possible due download error')
        return False


def removeFilesNotInRepo(updateFile, LocalDir):
    ignored_files = ['settings.xml', 'aniworld.py', 'aniworld.png']
    updateFileNameList = [i.split("/")[-1] for i in updateFile.namelist()]

    for root, dirs, files in os.walk(LocalDir):
        if ".git" in root or "pydev" in root or ".idea" in root:
            continue
        else:
            for file in files:
                if file in ignored_files:
                    continue
                if file not in updateFileNameList:
                    os.remove(os.path.join(root, file))


def _getXmlString(xml_url, auth):
    try:
        xmlString = requests.get(xml_url, auth=auth).content  # verify=False,
        if "sha" in json.loads(xmlString):
            return xmlString
        else:
            log(LOGMESSAGE + ' -> [updateManager]: Update-URL incorrect or bad credentials')
    except Exception as e:
        log(e)


# todo Verzeichnis packen -für zukünftige Erweiterung "Backup"
def zipfolder(foldername, target_dir):
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
    zipobj.close()


def devUpdates():  # für manuelles Updates vorgesehen
    try:
        resolverupdate = False # Resolver Update
        #pluginupdate = False # xStream Update
        # Einleitungstext
        #if Dialog().ok(HEADERMESSAGE, cConfig().getLocalizedString(30152)):
            # Abfrage welches Plugin aktualisiert werden soll (kann erweitert werden)
        #    options = [cConfig().getLocalizedString(30153),
        #               cConfig().getLocalizedString(30096) + ' ' + cConfig().getLocalizedString(30154),
        #               cConfig().getLocalizedString(30030) + ' ' + cConfig().getLocalizedString(30154)]
        #    result = Dialog().select(HEADERMESSAGE, options)
        #else:
            #return False

        #if result == -1:  # Abbrechen
            #return False

        #elif result == 0:  # Alle Addons aktualisieren
            # Abfrage ob ResolveURL Release oder Nightly Branch (kann erweitert werden)
        result = Dialog().yesno(HEADERMESSAGE, cConfig().getLocalizedString(30268), yeslabel='Nightly', nolabel='Release')

        if result == 0:
            Addon().setSetting('resolver.branch', 'release')
        elif result == 1:
            Addon().setSetting('resolver.branch', 'nightly')

        # Voreinstellung beendet
        if Dialog().yesno(HEADERMESSAGE, cConfig().getLocalizedString(30269), yeslabel=cConfig().getLocalizedString(30162), nolabel=cConfig().getLocalizedString(30163)):
            # Updates ausführen
            #pluginupdate = True
            resolverupdate = True
        else:
            return False

        #elif result == 1:  # xStream aktualisieren
        #    if Dialog().yesno(HEADERMESSAGE, cConfig().getLocalizedString(30269),
        #                      yeslabel=cConfig().getLocalizedString(30162),
        #                      nolabel=cConfig().getLocalizedString(30163)):
        #        # Updates ausführen
        #        pluginupdate = True
        #    else:
        #        return False

        #elif result == 2:  # Resolver aktualisieren
        #    # Abfrage ob ResolveURL Release oder Nightly Branch (kann erweitert werden)
        #    result = Dialog().yesno(HEADERMESSAGE, cConfig().getLocalizedString(30268), yeslabel='Nightly',
        #                            nolabel='Release')

        #    if result == 0:
        #        Addon().setSetting('resolver.branch', 'release')
        #    elif result == 1:
        #        Addon().setSetting('resolver.branch', 'nightly')

        #    # Voreinstellung beendet
        #    if Dialog().yesno(HEADERMESSAGE, cConfig().getLocalizedString(30269),
        #                      yeslabel=cConfig().getLocalizedString(30162),
        #                      nolabel=cConfig().getLocalizedString(30163)):
        #        # Updates ausführen
        #        resolverupdate = True
        #    else:
        #        return False

        #if pluginupdate is True:
           #try:
                #xStreamUpdate(False)
            #except:
                #pass
        if resolverupdate is True:
            try:
                resolverUpdate(False)
            except:
                pass

        # Zurücksetzten der Update.sha
        if Addon().getSetting('enforceUpdate') == 'true': Addon().setSetting('enforceUpdate', 'false')
        return
    except Exception as e:
        log(e)