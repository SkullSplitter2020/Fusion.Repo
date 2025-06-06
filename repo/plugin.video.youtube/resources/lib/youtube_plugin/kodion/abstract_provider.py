# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from __future__ import absolute_import, division, unicode_literals

from re import (
    UNICODE as re_UNICODE,
    compile as re_compile,
)

from .constants import (
    CHECK_SETTINGS,
    CONTAINER_ID,
    CONTAINER_POSITION,
    CONTENT,
    PATHS,
    REROUTE_PATH,
    WINDOW_CACHE,
    WINDOW_FALLBACK,
    WINDOW_REPLACE,
    WINDOW_RETURN,
)
from .exceptions import KodionException
from .items import (
    DirectoryItem,
    NewSearchItem,
    NextPageItem,
    SearchHistoryItem,
    UriItem,
)
from .utils import format_stack, to_unicode


class AbstractProvider(object):
    CACHE_TO_DISC = 'provider_cache_to_disc'  # type: bool
    FALLBACK = 'provider_fallback'  # type: bool | str
    FORCE_PLAY = 'provider_force_play'  # type: bool
    FORCE_RESOLVE = 'provider_force_resolve'  # type: bool
    UPDATE_LISTING = 'provider_update_listing'  # type: bool
    CONTENT_TYPE = 'provider_content_type'  # type: tuple[str, str, str]

    # map for regular expression (path) to method (names)
    _dict_path = {}

    def __init__(self):
        # register some default paths
        self.register_path(r''.join((
            '^',
            '(?:', PATHS.HOME, ')?/?$'
        )), self.on_root)

        self.register_path(r''.join((
            '^',
            PATHS.ROUTE,
            '(?P<path>/[^?]+?)(?:/*[?].+|/*)$'
        )), self.on_reroute)

        self.register_path(r''.join((
            '^',
            PATHS.GOTO_PAGE,
            '(?P<page>/[0-9]+)?'
            '(?P<path>/[^?]+?)(?:/*[?].+|/*)$'
        )), self.on_goto_page)

        self.register_path(r''.join((
            '^',
            PATHS.COMMAND,
            '/(?P<command>[^?]+?)(?:/*[?].+|/*)$'
        )), self.on_command)

        self.register_path(r''.join((
            '^',
            PATHS.WATCH_LATER,
            '/(?P<command>add|clear|list|play|remove)/?$'
        )), self.on_watch_later)

        self.register_path(r''.join((
            '^',
            PATHS.BOOKMARKS,
            '/(?P<command>add|clear|list|play|remove)/?$'
        )), self.on_bookmarks)

        self.register_path(r''.join((
            '^',
            '(', PATHS.SEARCH, '|', PATHS.EXTERNAL_SEARCH, ')',
            '/(?P<command>input|input_prompt|query|list|links|remove|clear|rename)?/?$'
        )), self.on_search)

        self.register_path(r''.join((
            '^',
            PATHS.HISTORY,
            '/(?P<command>clear|list|mark_unwatched|mark_watched|play|remove|reset_resume)/?$'
        )), self.on_playback_history)

        self.register_path(r'(?P<path>.*\/)extrafanart\/([\?#].+)?$',
                           self.on_extra_fanart)

    @classmethod
    def register_path(cls, re_path, command=None):
        """
        Registers a new method for the given regular expression
        :param re_path: regular expression of the path
        :param command: command or function to be registered
        :return:
        """

        def wrapper(command):
            if callable(command):
                func = command
            else:
                func = getattr(command, '__func__', None)
                if not callable(func):
                    return None

            cls._dict_path[re_compile(re_path, re_UNICODE)] = func
            return command

        if command:
            return wrapper(command)
        return wrapper

    def run_wizard(self, context, last_run=None):
        localize = context.localize
        # ui local variable used for ui.get_view_manager() in unofficial version
        ui = context.get_ui()

        settings_state = {'state': 'defer'}
        context.wakeup(CHECK_SETTINGS, timeout=5, payload=settings_state)

        if last_run and last_run > 1:
            self.pre_run_wizard_step(provider=self, context=context)
        wizard_steps = self.get_wizard_steps()
        wizard_steps.extend(ui.get_view_manager().get_wizard_steps())

        step = 0
        steps = len(wizard_steps)

        try:
            if wizard_steps and ui.on_yes_no_input(
                    ' - '.join((localize('youtube'), localize('setup_wizard'))),
                    (localize('setup_wizard.prompt')
                     % localize('setup_wizard.prompt.settings'))
            ):
                for wizard_step in wizard_steps:
                    if callable(wizard_step):
                        step = wizard_step(provider=self,
                                           context=context,
                                           step=step,
                                           steps=steps)
                    else:
                        step += 1
        finally:
            settings = context.get_settings(refresh=True)
            settings.setup_wizard_enabled(False)
            settings_state['state'] = 'process'
            context.wakeup(CHECK_SETTINGS, timeout=5, payload=settings_state)

    @staticmethod
    def get_wizard_steps():
        # can be overridden by the derived class
        return []

    @staticmethod
    def pre_run_wizard_step(provider, context):
        # can be overridden by the derived class
        pass

    def navigate(self, context):
        path = context.get_path()
        for re_path, handler in self._dict_path.items():
            re_match = re_path.search(path)
            if not re_match:
                continue

            options = {
                self.CACHE_TO_DISC: True,
                self.UPDATE_LISTING: False,
            }
            result = handler(provider=self, context=context, re_match=re_match)
            if isinstance(result, tuple):
                result, new_options = result
                if new_options:
                    options.update(new_options)

            if context.refresh_requested():
                options[self.CACHE_TO_DISC] = True
                options[self.UPDATE_LISTING] = True

            return result, options

        raise KodionException('Mapping for path "%s" not found' % path)

    def on_extra_fanart_run(self, context, re_match):
        """
        The implementation of the provider can override this behavior.
        :param context:
        :param re_match:
        :return:
        """
        return

    @staticmethod
    def on_extra_fanart(provider, context, re_match):
        path = re_match.group('path')
        new_context = context.clone(new_path=path)
        return provider.on_extra_fanart_run(new_context, re_match)

    @staticmethod
    def on_playback_history(provider, context, re_match):
        raise NotImplementedError()

    @staticmethod
    def on_root(provider, context, re_match):
        raise NotImplementedError()

    @staticmethod
    def on_goto_page(provider, context, re_match):
        ui = context.get_ui()

        page = re_match.group('page')
        if page:
            page = int(page.lstrip('/'))
        else:
            result, page = ui.on_numeric_input(
                title=context.localize('page.choose'),
                default=1,
            )
            if not result:
                return False

        path = re_match.group('path')
        params = context.get_params()
        if 'page_token' in params:
            page_token = NextPageItem.create_page_token(
                page, params.get('items_per_page', 50)
            )
        else:
            page_token = ''
        if 'exclude' in params:
            del params['exclude']
        params = dict(params, page=page, page_token=page_token)

        if (not ui.busy_dialog_active()
                and context.is_plugin_path(
                    context.get_infolabel('Container.FolderPath'),
                    partial=True,
                )):
            return provider.reroute(context=context, path=path, params=params)
        return provider.navigate(context.clone(path, params))

    @staticmethod
    def on_reroute(provider, context, re_match):
        return provider.reroute(
            context=context,
            path=re_match.group('path'),
            params=context.get_params(),
        )

    def reroute(self, context, path=None, params=None, uri=None):
        container_uri = context.get_infolabel('Container.FolderPath')
        current_path, current_params = context.parse_uri(container_uri)

        if uri is None:
            if path is None:
                path = current_path
            if params is None:
                params = current_params
        else:
            uri = context.parse_uri(uri)
            if params:
                uri[1].update(params)
            path, params = uri

        if not path:
            context.log_error('Rerouting - No route path')
            return False
        elif path.startswith(PATHS.ROUTE):
            path = path[len(PATHS.ROUTE):]

        window_cache = params.pop(WINDOW_CACHE, True)
        window_fallback = params.pop(WINDOW_FALLBACK, False)
        window_replace = params.pop(WINDOW_REPLACE, False)
        window_return = params.pop(WINDOW_RETURN, True)

        if window_fallback:
            container_uri = context.get_infolabel('Container.FolderPath')
            if context.is_plugin_path(container_uri):
                context.log_debug('Rerouting - Fallback route not required')
                return False, {self.FALLBACK: False}

        container = None
        position = None
        refresh = params.get('refresh', 0)
        if (refresh or (
                params == current_params
                and path.rstrip('/') == current_path.rstrip('/')
        )):
            if refresh < 0:
                del params['refresh']
            else:
                container = context.get_infolabel('System.CurrentControlId')
                position = context.get_infolabel('Container.CurrentItem')
                params['refresh'] = context.refresh_requested(
                    force=True,
                    on=True,
                    params=params,
                )

        ui = context.get_ui()
        result = None
        try:
            if window_cache:
                function_cache = context.get_function_cache()
                with ui.on_busy():
                    result, options = function_cache.run(
                        self.navigate,
                        _refresh=True,
                        _scope=function_cache.SCOPE_NONE,
                        context=context.clone(path, params),
                    )
        except Exception as exc:
            context.log_error('Rerouting - Error'
                              '\n\tException: {exc!r}'
                              '\n\tStack trace (most recent call last):\n{stack}'
                              .format(exc=exc,
                                      stack=format_stack()))
        finally:
            uri = context.create_uri(path, params)
            if result or not window_cache:
                context.log_debug('Rerouting - Success'
                                  '\n\tURI:      {uri}'
                                  '\n\tCache:    |{window_cache}|'
                                  '\n\tFallback: |{window_fallback}|'
                                  '\n\tReplace:  |{window_replace}|'
                                  '\n\tReturn:   |{window_return}|'
                                  .format(uri=uri,
                                          window_cache=window_cache,
                                          window_fallback=window_fallback,
                                          window_replace=window_replace,
                                          window_return=window_return))
            else:
                context.log_debug('Rerouting - No results'
                                  '\n\tURI: {uri}'
                                  .format(uri=uri))
                return False

            reroute_path = ui.get_property(REROUTE_PATH)
            if reroute_path:
                return True

            if window_cache:
                ui.set_property(REROUTE_PATH, path)
                if container and position:
                    ui.set_property(CONTAINER_ID, container)
                    ui.set_property(CONTAINER_POSITION, position)

            action = ''.join((
                'ReplaceWindow' if window_replace else 'ActivateWindow',
                '(Videos,',
                uri,
                ',return)' if window_return else ')',
            ))

            timeout = 30
            while ui.busy_dialog_active():
                timeout -= 1
                if timeout < 0:
                    context.log_warning('Multiple busy dialogs active'
                                        ' - Rerouting workaround')
                    return UriItem('command://{0}'.format(action))
                context.sleep(1)
            else:
                context.execute(
                    action,
                    # wait=True,
                    # wait_for=(REROUTE_PATH if window_cache else None),
                    # wait_for_set=False,
                    # block_ui=True,
                )
                return True

    @staticmethod
    def on_bookmarks(provider, context, re_match):
        raise NotImplementedError()

    @staticmethod
    def on_watch_later(provider, context, re_match):
        raise NotImplementedError()

    def on_search_run(self, context, query):
        raise NotImplementedError()

    @staticmethod
    def on_search(provider, context, re_match):
        params = context.get_params()
        localize = context.localize
        ui = context.get_ui()

        command = re_match.group('command')
        search_history = context.get_search_history()

        if not command or command == 'query':
            query = to_unicode(params.get('q', ''))
            if query:
                result, options = provider.on_search_run(context, query=query)
                if not options:
                    options = {provider.CACHE_TO_DISC: False}
                if result:
                    fallback = options.setdefault(
                        provider.FALLBACK, context.get_uri()
                    )
                    ui.set_property(provider.FALLBACK, fallback)
                return result, options
            command = 'list'
            context.set_path(PATHS.SEARCH, command)

        if command == 'remove':
            query = to_unicode(params.get('q', ''))
            if not ui.on_yes_no_input(
                    localize('content.remove'),
                    localize('content.remove.check') % query,
            ):
                return False, None

            search_history.del_item(query)
            ui.refresh_container()

            ui.show_notification(
                localize('removed') % query,
                time_ms=2500,
                audible=False,
            )
            return True, None

        if command == 'rename':
            query = to_unicode(params.get('q', ''))
            result, new_query = ui.on_keyboard_input(
                localize('search.rename'), query
            )
            if result:
                search_history.del_item(query)
                search_history.add_item(new_query)
                ui.refresh_container()
            return True, None

        if command == 'clear':
            if not ui.on_yes_no_input(
                    localize('search.clear'),
                    localize('content.clear.check') % localize('search.history')
            ):
                return False, None

            search_history.clear()
            ui.refresh_container()

            ui.show_notification(
                localize('completed'),
                time_ms=2500,
                audible=False,
            )
            return True, None

        if command == 'links':
            return provider.on_specials_x(
                provider,
                context,
                category='description_links',
            )

        if command.startswith('input'):
            query = None
            #  came from page 1 of search query by '..'/back
            #  user doesn't want to input on this path
            fallback = True
            old_path, old_params = context.parse_uri(
                context.get_infolabel('Container.FolderPath')
            )
            old_uri = context.create_uri(old_path, old_params)
            if (not context.refresh_requested()
                    and context.is_plugin_folder()
                    and context.is_plugin_path(old_uri,
                                               PATHS.SEARCH,
                                               partial=True)):

                query = old_params.get('q')
                if not query:
                    fallback = ui.pop_property(provider.FALLBACK)
                    if fallback:
                        history_blacklist = (
                            context.create_path(PATHS.SEARCH, 'input'),
                            context.create_path(PATHS.SEARCH, 'query'),
                            context.create_path(PATHS.SEARCH, 'list'),
                        )
                    else:
                        fallback = old_uri
                        history_blacklist = (
                            context.create_path(PATHS.SEARCH, 'input'),
                            context.create_path(PATHS.SEARCH, 'query'),
                        )
                    if old_path.startswith(history_blacklist):
                        query = False

            if query:
                query = to_unicode(query)
            elif query is None:
                result, input_query = ui.on_keyboard_input(
                    localize('search.title')
                )
                if result:
                    query = input_query

            if query:
                # Race conditions with other addons creating busy dialogs can
                # prevent opening a new window
                # fallback = old_uri
                # ui.set_property(provider.RESULT_FALLBACK, fallback)
                # return UriItem(context.create_uri(
                #     (PATHS.SEARCH, 'query'),
                #     dict(params, q=query),
                #     window={'replace': False, 'return': True},
                # )), {provider.RESULT_FALLBACK: False}

                # Alternate method is faster/smoother but means that history is
                # not properly modified to prevent navigating back to input
                # dialog
                context.set_params(q=query)
                context.set_path(PATHS.SEARCH, 'query')
                result, options = provider.on_search_run(context, query=query)
                if not options:
                    options = {provider.CACHE_TO_DISC: False}
                fallback = options.setdefault(
                    provider.FALLBACK,
                    context.get_uri() if result else old_uri,
                )
                if fallback:
                    ui.set_property(provider.FALLBACK, fallback)
            else:
                result = False
                options = {
                    provider.CACHE_TO_DISC: False,
                    provider.FALLBACK: fallback,
                }
            return result, options

        location = context.get_param('location', False)

        result = []
        options = {
            provider.CACHE_TO_DISC: False,
            provider.CONTENT_TYPE: {
                'content_type': CONTENT.LIST_CONTENT,
                'sub_type': None,
                'category_label': localize('search'),
            },
        }

        # 'New Search...'
        new_search_item = NewSearchItem(
            context, location=location
        )
        result.append(new_search_item)

        for search in search_history.get_items():
            # little fallback for old history entries
            if isinstance(search, DirectoryItem):
                search = search.get_name()

            # we create a new instance of the SearchItem
            search_history_item = SearchHistoryItem(
                context, search, location=location
            )
            result.append(search_history_item)

        return result, options

    @staticmethod
    def on_command(re_match, **_kwargs):
        command = re_match.group('command')
        return UriItem(''.join(('command://', command)))

    def handle_exception(self, context, exception_to_handle):
        return True

    def tear_down(self):
        pass
