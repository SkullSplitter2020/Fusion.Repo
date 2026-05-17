#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import xbmc
import xbmcaddon

class HelpSearch:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.content_path = os.path.join(self.addon.getAddonInfo('path'), 'resources', 'content')
        self.chapter_names = {
            "basics": "Grundbedienung",
            "shortcuts": "Shortcuts & Tricks",
            "troubleshooting": "Problembehebung",
            "advanced": "Experten-Einstellungen"
        }

    def search_all_content(self, query):
        results = []
        query_lower = query.lower()

        if not os.path.exists(self.content_path):
            return results

        for filename in os.listdir(self.content_path):
            if filename.endswith('.json') and filename != 'main_menu.json':
                chapter_key = filename.replace('.json', '')
                chapter_name = self.chapter_names.get(chapter_key, chapter_key.title())
                file_path = os.path.join(self.content_path, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        page_counter = [0]
                        self._search_recursive(content, query_lower, results, chapter_name, page_counter)
                except Exception as e:
                    xbmc.log(f"Search error in {filename}: {str(e)}", xbmc.LOGWARNING)

        return results

    def _search_recursive(self, node, query, results, chapter, page_counter):
        if isinstance(node, list):
            for item in node:
                self._search_recursive(item, query, results, chapter, page_counter)
        elif isinstance(node, dict):
            if 'text' in node:
                text_content = node.get('text', '').lower()
                title_content = node.get('title', '').lower()

                if query in text_content or query in title_content:
                    results.append({
                        'chapter': chapter,
                        'title': node.get('title', f'Seite {page_counter[0] + 1}'),
                        'page': page_counter[0]
                    })
                page_counter[0] += 1

            if 'children' in node:
                self._search_recursive(node['children'], query, results, chapter, page_counter)