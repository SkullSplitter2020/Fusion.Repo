# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from __future__ import absolute_import, division, unicode_literals

from weakref import proxy

from .view_manager import ViewManager
from ..abstract_context_ui import AbstractContextUI
from ...compatibility import string_type, xbmc, xbmcgui
from ...constants import ADDON_ID, REFRESH_CONTAINER
from ...utils import to_unicode


class XbmcContextUI(AbstractContextUI):
    def __init__(self, context):
        super(XbmcContextUI, self).__init__()
        self._context = context
        self._view_manager = None

    def create_progress_dialog(self,
                               heading,
                               message='',
                               total=None,
                               background=False,
                               message_template=None,
                               template_params=None):
        if not message_template and background:
            message_template = '{_message} {_current}/{_total}'

        return XbmcProgressDialog(
            ui=proxy(self),
            dialog=(xbmcgui.DialogProgressBG
                    if background else
                    xbmcgui.DialogProgress),
            background=background,
            heading=heading,
            message=message or self._context.localize('please_wait'),
            total=int(total) if total is not None else 0,
            message_template=message_template,
            template_params=template_params,
            hide=self._context.get_param('hide_progress'),
        )

    def get_view_manager(self):
        if self._view_manager is None:
            self._view_manager = ViewManager(self._context)

        return self._view_manager

    def on_keyboard_input(self, title, default='', hidden=False):
        # Starting with Gotham (13.X > ...)
        dialog = xbmcgui.Dialog()
        result = dialog.input(title,
                              to_unicode(default),
                              type=xbmcgui.INPUT_ALPHANUM)
        if result:
            text = to_unicode(result)
            return True, text

        return False, ''

    def on_numeric_input(self, title, default=''):
        dialog = xbmcgui.Dialog()
        result = dialog.input(title, str(default), type=xbmcgui.INPUT_NUMERIC)
        if result:
            return True, int(result)

        return False, None

    def on_yes_no_input(self, title, text, nolabel='', yeslabel=''):
        dialog = xbmcgui.Dialog()
        return dialog.yesno(title, text, nolabel=nolabel, yeslabel=yeslabel)

    def on_ok(self, title, text):
        dialog = xbmcgui.Dialog()
        return dialog.ok(title, text)

    def on_remove_content(self, name):
        return self.on_yes_no_input(
            self._context.localize('content.remove'),
            self._context.localize('content.remove.check') % to_unicode(name),
        )

    def on_delete_content(self, name):
        return self.on_yes_no_input(
            self._context.localize('content.delete'),
            self._context.localize('content.delete.check') % to_unicode(name),
        )

    def on_clear_content(self, name):
        return self.on_yes_no_input(
            self._context.localize('content.clear'),
            self._context.localize('content.clear.check') % to_unicode(name),
        )

    def on_select(self, title, items=None, preselect=-1, use_details=False):
        if isinstance(items, (list, tuple)):
            items = enumerate(items)
        elif isinstance(items, dict):
            items = items.items()
        else:
            return -1

        result_map = {}
        dialog_items = []

        for idx, item in items:
            if isinstance(item, (list, tuple)):
                num_details = len(item)
                if num_details > 2:
                    list_item = xbmcgui.ListItem(label=item[0],
                                                 label2=item[1],
                                                 offscreen=True)
                    if num_details > 3:
                        use_details = True
                        icon = item[3]
                        list_item.setArt({'icon': icon, 'thumb': icon})
                        if num_details > 4 and item[4]:
                            preselect = idx
                    result_map[idx] = item[2]
                    dialog_items.append(list_item)
                else:
                    result_map[idx] = item[1]
                    dialog_items.append(item[0])
            else:
                result_map[idx] = idx
                dialog_items.append(item)

        dialog = xbmcgui.Dialog()
        result = dialog.select(title,
                               dialog_items,
                               preselect=preselect,
                               useDetails=use_details)
        return result_map.get(result, -1)

    def show_notification(self,
                          message,
                          header='',
                          image_uri='',
                          time_ms=5000,
                          audible=True):
        _header = header
        if not _header:
            _header = self._context.get_name()

        _image = image_uri
        if not _image:
            _image = self._context.get_icon()

        _message = message.replace(',', ' ').replace('\n', ' ')

        xbmcgui.Dialog().notification(_header,
                                      _message,
                                      _image,
                                      time_ms,
                                      audible)

    def on_busy(self):
        return XbmcBusyDialog()

    def refresh_container(self):
        self._context.send_notification(REFRESH_CONTAINER)

    def set_property(self, property_id, value='true'):
        self._context.log_debug('Set property |{id}|: {value!r}'
                                .format(id=property_id, value=value))
        _property_id = '-'.join((ADDON_ID, property_id))
        xbmcgui.Window(10000).setProperty(_property_id, value)
        return value

    def get_property(self, property_id):
        _property_id = '-'.join((ADDON_ID, property_id))
        value = xbmcgui.Window(10000).getProperty(_property_id)
        self._context.log_debug('Get property |{id}|: {value!r}'
                                .format(id=property_id, value=value))
        return value

    def pop_property(self, property_id):
        _property_id = '-'.join((ADDON_ID, property_id))
        window = xbmcgui.Window(10000)
        value = window.getProperty(_property_id)
        if value:
            window.clearProperty(_property_id)
        self._context.log_debug('Pop property |{id}|: {value!r}'
                                .format(id=property_id, value=value))
        return value

    def clear_property(self, property_id):
        self._context.log_debug('Clear property |{id}|'.format(id=property_id))
        _property_id = '-'.join((ADDON_ID, property_id))
        xbmcgui.Window(10000).clearProperty(_property_id)
        return None

    @staticmethod
    def bold(value, cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[B]', value, '[/B]',
            '[CR]' * cr_after,
        ))

    @staticmethod
    def uppercase(value, cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[UPPERCASE]', value, '[/UPPERCASE]',
            '[CR]' * cr_after,
        ))

    @staticmethod
    def color(color, value, cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[COLOR=', color.lower(), ']', value, '[/COLOR]',
            '[CR]' * cr_after,
        ))

    @staticmethod
    def light(value, cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[LIGHT]', value, '[/LIGHT]',
            '[CR]' * cr_after,
        ))

    @staticmethod
    def italic(value, cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[I]', value, '[/I]',
            '[CR]' * cr_after,
        ))

    @staticmethod
    def indent(number=1, value='', cr_before=0, cr_after=0):
        return ''.join((
            '[CR]' * cr_before,
            '[TABS]', str(number), '[/TABS]', value,
            '[CR]' * cr_after,
        ))

    @staticmethod
    def new_line(value=1, cr_before=0, cr_after=0):
        if isinstance(value, int):
            return '[CR]' * value
        return ''.join((
            '[CR]' * cr_before,
            value,
            '[CR]' * cr_after,
        ))

    @staticmethod
    def set_focus_next_item():
        container = xbmc.getInfoLabel('System.CurrentControlId')
        position = xbmc.getInfoLabel('Container.CurrentItem')
        try:
            position = int(position) + 1
        except ValueError:
            return
        xbmc.executebuiltin(
            'SetFocus({container},{position},absolute)'.format(
                container=container,
                position=position
            )
        )

    @staticmethod
    def busy_dialog_active(all_modals=False, dialog_ids=frozenset((
            10100,  # WINDOW_DIALOG_YES_NO
            10101,  # WINDOW_DIALOG_PROGRESS
            10103,  # WINDOW_DIALOG_KEYBOARD
            10109,  # WINDOW_DIALOG_NUMERIC
            10138,  # WINDOW_DIALOG_BUSY
            10151,  # WINDOW_DIALOG_EXT_PROGRESS
            10160,  # WINDOW_DIALOG_BUSY_NOCANCEL
            12000,  # WINDOW_DIALOG_SELECT
            12002,  # WINDOW_DIALOG_OK
    ))):
        if all_modals and xbmc.getCondVisibility('System.HasActiveModalDialog'):
            return True
        dialog_id = xbmcgui.getCurrentWindowDialogId()
        if dialog_id in dialog_ids:
            return dialog_id
        return False


class XbmcProgressDialog(object):
    def __init__(self,
                 ui,
                 dialog,
                 background,
                 heading,
                 message='',
                 total=0,
                 message_template=None,
                 template_params=None,
                 hide=False):
        if hide:
            self._dialog = None
            self._created = False
            return

        self._ui = ui
        if ui.busy_dialog_active(all_modals=True):
            self._dialog = dialog()
            self._dialog.create(heading, message)
            self._created = True
        else:
            self._dialog = dialog()
            self._created = False

        self._background = background

        self._position = None
        self._total = total

        self._heading = heading
        self._message = message
        if message_template:
            self._message_template = message_template
            self._template_params = {
                '_message': message,
                '_progress': (0, self._total),
                '_current': 0,
                '_total': self._total,
            }
            if template_params:
                self._template_params.update(template_params)
        else:
            self._message_template = None
            self._template_params = None

        # simple reset because KODI won't do it :(
        self.update(position=0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.close()

    def get_total(self):
        if not self._dialog:
            return None
        return self._total

    def get_position(self):
        if not self._dialog:
            return None
        return self._position

    def close(self):
        if self._dialog and self._created:
            self._dialog.close()
            self._dialog = None
            self._created = False

    def is_aborted(self):
        if self._dialog and self._created:
            return getattr(self._dialog, 'iscanceled', bool)()
        return False

    def set_total(self, total):
        if not self._dialog:
            return
        self._total = int(total)

    def reset_total(self, new_total, **kwargs):
        if not self._dialog:
            return
        self._total = int(new_total)
        self.update(position=0, **kwargs)

    def update_total(self, new_total, **kwargs):
        if not self._dialog:
            return
        self._total = int(new_total)
        self.update(steps=0, **kwargs)

    def grow_total(self, new_total=None, delta=None):
        if not self._dialog:
            return None
        if delta:
            delta = int(delta)
            self._total += delta
        elif new_total:
            total = int(new_total)
            if total > self._total:
                self._total = total
        return self._total

    def update(self, steps=1, position=None, message=None, **template_params):
        if not self._dialog:
            return

        if position is None:
            self._position += steps
        else:
            self._position = position

        if not self._total:
            percent = 0
        elif self._position >= self._total:
            percent = 100
            self._total = self._position
        else:
            percent = int(100 * self._position / self._total)

        if isinstance(message, string_type):
            self._message = message
        elif self._message_template:
            if template_params:
                self._template_params.update(template_params)
            template_params = self._template_params
            progress = (self._position, self._total)
            template_params['_progress'] = progress
            template_params['_current'], template_params['_total'] = progress
            message = self._message_template.format(
                *template_params['_progress'],
                **template_params
            )
            self._message = message

        if not self._created:
            if self._ui.busy_dialog_active(all_modals=True):
                return
            self._dialog.create(self._heading, self._message)
            self._created = True

        # Kodi 18 renamed XbmcProgressDialog.update argument line1 to message.
        # Only use positional arguments to maintain compatibility
        if self._background:
            self._dialog.update(percent, self._heading, self._message)
        else:
            self._dialog.update(percent, self._message)


class XbmcBusyDialog(object):
    def __enter__(self):
        xbmc.executebuiltin('ActivateWindow(BusyDialogNoCancel)')
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.close()

    @staticmethod
    def close():
        xbmc.executebuiltin('Dialog.Close(BusyDialogNoCancel)')
