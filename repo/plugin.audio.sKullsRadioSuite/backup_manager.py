import os
import xbmc
import xbmcvfs
from datetime import datetime


class BackupManager:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        backup_folder = self.addon.getSetting("backup_folder")
        # Default: userdata/addon_data/plugin.audio.sKullsRadioSuite/Backups
        if not backup_folder:
            profile_dir = xbmcvfs.translatePath(self.addon.getAddonInfo("profile"))
            backup_folder = os.path.join(profile_dir, "Backups")
        self.backup_dir = xbmcvfs.translatePath(backup_folder)

        # Erstelle Backup-Ordner falls nicht existent
        if not xbmcvfs.exists(self.backup_dir):
            xbmcvfs.mkdirs(self.backup_dir)

    def get_backup_path(self, filename):
        """Generiert vollständigen Backup-Pfad"""
        if self.addon.getSetting("zip_structure") == "dated":
            date_folder = datetime.now().strftime("%Y-%m")
            full_path = os.path.join(self.backup_dir, date_folder)
            if not xbmcvfs.exists(full_path):
                xbmcvfs.mkdirs(full_path)
            return os.path.join(full_path, filename)
        return os.path.join(self.backup_dir, filename)

    def cleanup_old_backups(self):
        """Löscht alte Backups nach Einstellung"""
        max_backups = int(self.addon.getSetting("max_backups"))
        if max_backups <= 0:
            return

        backups = []
        for root, _, files in xbmcvfs.walk(self.backup_dir):
            for file in files:
                if file.startswith(self.addon.getSetting("backup_prefix")):
                    path = os.path.join(root, file)
                    backups.append((path, xbmcvfs.Stat(path).st_mtime()))

        backups.sort(key=lambda x: x[1], reverse=True)

        for backup in backups[max_backups:]:
            try:
                xbmcvfs.delete(backup[0])
                xbmc.log(f"Altes Backup gelöscht: {backup[0]}", xbmc.LOGINFO)
            except:
                xbmc.log(f"Fehler beim Löschen: {backup[0]}", xbmc.LOGERROR)
