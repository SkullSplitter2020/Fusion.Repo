#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import xbmcaddon
import json
import os
import urllib.parse
from content_loader import ContentLoader
from search import HelpSearch

ADDON_ID = "plugin.program.skullshelp"
BASE_URL = f"plugin://{ADDON_ID}"

class NavigationController:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_path = self.addon.getAddonInfo('path')
        self.content_loader = ContentLoader()
        self.search = HelpSearch()
        self.current_chapter = None
        self.current_page = 0
        self.total_pages = 0

    def show_main_menu(self):
        try:
            menu_data = self.content_loader.load_json('main_menu.json')
            if not menu_data:
                xbmcgui.Dialog().ok("Fehler", "Hauptmenü konnte nicht geladen werden")
                return

            menu_items = []
            icons = []

            icons_map = {
                "Kodi Schnellstart": "placeholder.jpg",
                "sKulls Radio Suite": "placeholder.jpg",
                "sKulls Wallpapers": "placeholder.jpg",
                "Tastenkuerzel": "shortcuts.png",
                "Problembehebung": "remote_error.jpg",
                "Experten-Einstellungen": "dev_options.jpg"
            }

            for item in menu_data:
                menu_items.append(f"[COLOR gold]{item['title']}[/COLOR]")
                icon = icons_map.get(item['title'], "placeholder.jpg")
                icons.append(os.path.join(self.addon_path, 'resources', 'images', icon))

            menu_items.append("[COLOR cyan]Einstellungen[/COLOR]")
            icons.append(os.path.join(self.addon_path, 'resources', 'images', 'placeholder.jpg'))

            dialog = xbmcgui.Dialog()
            selected = dialog.select("[COLOR gold][B]=== sKulls Help Guide ===[/B][/COLOR]", menu_items)

            if selected == len(menu_data):
                xbmcaddon.Addon().openSettings()
                return

            if selected >= 0:
                chapter_file = menu_data[selected]['file'].replace('.json', '')
                self.show_chapter(chapter_file)

        except Exception as e:
            xbmc.log(f"Main menu error: {str(e)}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification("Fehler", "Hauptmenü konnte nicht geladen werden", xbmcgui.NOTIFICATION_ERROR)

    def show_chapter(self, chapter_id, page=0):
        try:
            chapter_data = self.content_loader.load_json(f'{chapter_id}.json')
            if not chapter_data:
                xbmcgui.Dialog().notification("Fehler", f"Kapitel {chapter_id} nicht gefunden", xbmcgui.NOTIFICATION_ERROR)
                return

            self.current_chapter = chapter_data
            self.current_page = page
            pages = self._get_all_pages(chapter_data)
            self.total_pages = len(pages)

            if not pages:
                xbmcgui.Dialog().notification("Info", "Keine Inhalte verfügbar", xbmcgui.NOTIFICATION_INFO)
                self.show_main_menu()
                return

            if page >= self.total_pages:
                page = 0
                self.current_page = 0

            self.show_current_page(pages, chapter_id)

        except Exception as e:
            xbmc.log(f"Content error: {str(e)}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification("Fehler", "Inhalt konnte nicht geladen werden", xbmcgui.NOTIFICATION_ERROR)
            self.show_main_menu()

    def _get_all_pages(self, node, pages=None):
        if pages is None:
            pages = []

        if isinstance(node, list):
            for item in node:
                self._get_all_pages(item, pages)
        elif isinstance(node, dict):
            if 'text' in node:
                pages.append(node)
            if 'children' in node:
                self._get_all_pages(node['children'], pages)

        return pages

    def show_current_page(self, pages, chapter_id):
        if not pages or self.current_page >= len(pages):
            self.show_main_menu()
            return

        dialog = xbmcgui.Dialog()
        
        while True:
            current_content = pages[self.current_page]

            title = current_content.get('title', 'Hilfe')
            text = self.content_loader.format_text(current_content.get('text', ''))
            image_name = current_content.get('image', '')

            nav_info = f"[COLOR cyan]Seite {self.current_page + 1} von {len(pages)}[/COLOR]"

            display_text = f"[B][COLOR gold]{title}[/COLOR][/B]\n{nav_info}\n\n{text}"

            if image_name:
                image_path = os.path.join(self.addon_path, 'resources', 'images', image_name)
                if os.path.exists(image_path):
                    display_text += f"\n\n[B]Bild verfuegbar:[/B] [COLOR grey]{image_name}[/COLOR]"

            dialog.ok(title, display_text)

            buttons = self._create_navigation_buttons()
            ret = dialog.contextmenu(buttons)

            if ret >= 0:
                self._handle_navigation_choice(ret, pages, chapter_id)
                if self.current_page >= len(pages):
                    break
            else:
                break

    def _create_navigation_buttons(self):
        buttons = []

        if self.current_page > 0:
            buttons.append("<< Erste Seite")
            buttons.append("< Vorherige Seite")

        buttons.append("[+] Seitenuebersicht")

        if self.current_page < self.total_pages - 1:
            buttons.append("Naechste Seite >")
            buttons.append("Letzte Seite >>")

        buttons.extend([
            "[H] Hauptmenu",
            "[S] Suchen",
            "[B] Lesezeichen"
        ])

        return buttons

    def _handle_navigation_choice(self, choice, pages, chapter_id):
        buttons = self._create_navigation_buttons()

        if choice >= len(buttons):
            self.current_page = len(pages)
            return

        selected = buttons[choice]

        if "Erste Seite" in selected:
            self.current_page = 0
        elif "Vorherige" in selected:
            self.current_page = max(0, self.current_page - 1)
        elif "Seitenuebersicht" in selected:
            self.show_page_overview_dialog(pages, chapter_id)
        elif "Naechste" in selected:
            self.current_page = min(len(pages) - 1, self.current_page + 1)
        elif "Letzte Seite" in selected:
            self.current_page = len(pages) - 1
        elif "Hauptmenu" in selected:
            self.current_page = len(pages)
            self.show_main_menu()
        elif "Suchen" in selected:
            self.current_page = len(pages)
            self.show_search_dialog()
        elif "Lesezeichen" in selected:
            self.add_bookmark(pages[self.current_page], chapter_id)

    def add_bookmark(self, page_content, chapter_id):
        title = page_content.get('title', 'Unbekannt')
        xbmcgui.Dialog().notification("Lesezeichen", f"'{title}' als Lesezeichen gespeichert", xbmcgui.NOTIFICATION_INFO, 2000)

    def show_page_overview_dialog(self, pages, chapter_id):
        items = []
        for i, page in enumerate(pages):
            marker = ">> " if i == self.current_page else "   "
            title = page.get('title', f'Seite {i+1}')
            items.append(f"{marker}{i+1:2d}. {title}")

        dialog = xbmcgui.Dialog()
        selected = dialog.select("[+] Seitenuebersicht", items)

        if selected >= 0:
            self.current_page = selected

    def show_search_dialog(self):
        dialog = xbmcgui.Dialog()
        search_term = dialog.input("🔍 Suche:", type=xbmcgui.INPUT_ALPHANUM)

        if search_term:
            results = self.search.search_all_content(search_term)
            if results:
                result_items = []
                for r in results:
                    result_items.append(f"[COLOR cyan]{r['chapter']}[/COLOR]: {r['title']}")

                selected = dialog.select(f"Suchergebnisse für '{search_term}'", result_items)

                if selected >= 0:
                    result = results[selected]
                    self.show_chapter(result['chapter'], result['page'])
                else:
                    self.show_main_menu()

            else:
                dialog.notification("Suche", f"'{search_term}' nicht gefunden", xbmcgui.NOTIFICATION_INFO, 3000)
                self.show_main_menu()
        else:
            self.show_main_menu()