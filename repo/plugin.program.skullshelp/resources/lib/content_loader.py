#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import xbmc
import xbmcaddon

class ContentLoader:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_path = self.addon.getAddonInfo('path')
        self.content_path = os.path.join(self.addon_path, 'resources', 'content')
        self.images_path = os.path.join(self.addon_path, 'resources', 'images')

    def load_json(self, filename):
        file_path = os.path.join(self.content_path, filename)
        xbmc.log(f"ContentLoader: Trying {file_path}", xbmc.LOGDEBUG)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    xbmc.log(f"ContentLoader: Loaded {filename}", xbmc.LOGDEBUG)
                    return data
            else:
                xbmc.log(f"ContentLoader: File not found: {file_path}", xbmc.LOGERROR)
                # Fallback to addon root
                alt_path = os.path.join(self.addon_path, filename)
                if os.path.exists(alt_path):
                    with open(alt_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                # Fallback to content in addon root
                alt_path2 = os.path.join(self.addon_path, 'content', filename)
                if os.path.exists(alt_path2):
                    with open(alt_path2, 'r', encoding='utf-8') as f:
                        return json.load(f)
                xbmc.log(f"ContentLoader: All paths failed for {filename}", xbmc.LOGERROR)
                return []
        except json.JSONDecodeError as e:
            xbmc.log(f"ContentLoader: Invalid JSON in {filename}: {e}", xbmc.LOGERROR)
            return []
        except Exception as e:
            xbmc.log(f"ContentLoader: Error loading {filename}: {e}", xbmc.LOGERROR)
            return []

    def format_text(self, text):
        if not text:
            return ""

        text = text.replace('\\n', '\n')
        text = text.replace('• ', '• ')
        text = text.replace('→', ' → ')
        text = text.replace('←', ' ← ')

        return text

    def get_image_path(self, image_name):
        if not image_name:
            return ""

        image_path = os.path.join(self.images_path, image_name)
        if os.path.exists(image_path):
            return image_path

        return ""