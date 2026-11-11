"""Modal footer buttons as a django-menus menu.

The footer is a ``ModalButtons`` menu of named items, so a modal can add, insert,
relabel or remove buttons in ``setup_buttons(buttons, form=None)`` without
rebuilding the defaults::

    def setup_buttons(self, buttons, form=None):
        buttons['submit'].menu_display.text = 'Save'
        buttons.add_items(ModalButtonItem('export', css_classes='btn-info'), before='cancel')

``ModalButtonItem`` renders through ``helper.modal_button`` (a ``<button>`` that runs
its commands via ``django_modal.process_commands_lock``); any other django-menus item
(``MenuItem``, ``HtmlMenuItem``) can sit in the footer too.
"""
import json

from django.utils.safestring import mark_safe
from django_menus.menu import BaseMenuItem, HtmlMenu, HtmlMenuItem, MenuItem

from .helper import command_list, modal_button


class ModalButtonItem(MenuItem):
    """A modal button.  ``button_name`` identifies it in a ``ModalButtons`` menu.

    Clicking runs ``commands`` (a command name, dict or list); without commands it
    posts to the modal's ``button_<method>`` handler, ``method`` defaulting to
    ``button_name``.
    """

    def __init__(self, button_name, text=None, commands=None, method=None, method_kwargs=None,
                 css_classes='btn-primary', font_awesome=None, tooltip=None, attributes=None, **kwargs):
        if commands is None:
            commands = {'function': 'post_modal', 'button': dict(button=method or button_name, **(method_kwargs or {}))}
        self.button_name = button_name
        self.commands = commands
        if text is None:
            text = button_name.replace('_', ' ').capitalize()
        javascript = f"django_modal.process_commands_lock({json.dumps(command_list(commands))})".replace('"', "'")
        super().__init__(javascript, text, link_type=MenuItem.JAVASCRIPT, css_classes=css_classes,
                         font_awesome=font_awesome, attributes=attributes, **kwargs)
        # rendered by modal_button, so kept out of django-menus' own tooltip attributes
        self.tooltip = tooltip
        self.default_render = False

    def render(self):
        attributes = dict(self._attributes)
        if self.disabled:
            attributes['disabled'] = None
        return modal_button(self.menu_display.text, self.commands,
                            css_class=' '.join(self.menu_display.css_classes) or 'btn-primary',
                            font_awesome=self.menu_display.font_awesome, tooltip=self.tooltip, attributes=attributes)

    def __str__(self):
        return self.render()

    def __html__(self):
        return self.render()


class ModalButtons(HtmlMenu):
    """The buttons at the foot of a modal, rendered in ``.form-buttons > .btn-group``.

    ``buttons`` may be items, HTML strings (from ``modal_button``) or a single string.
    Items with a ``button_name`` can be looked up (``buttons['submit']``), removed,
    replaced or used as an insertion point.
    """

    def __init__(self, buttons=None, button_group_class='btn-group', button_container_class=None, request=None):
        super().__init__(request=request, template='django_modals/modal_buttons.html')
        self.button_group_class = button_group_class or 'btn-group'
        self.button_container_class = button_container_class
        if isinstance(buttons, str):
            buttons = [buttons]
        self.add_items(*(buttons or []))

    @staticmethod
    def as_item(button):
        if isinstance(button, (BaseMenuItem, tuple)):
            return button
        return HtmlMenuItem(html=str(button))

    def add_items(self, *items, before=None, after=None):
        """Append items, or insert them before/after the button with that ``button_name``."""
        if before is None and after is None:
            return super().add_items(*[self.as_item(i) for i in items if i is not None])
        return self.insert(self.index(before) if before is not None else self.index(after) + 1, *items)

    def insert(self, position, *items):
        count = len(self.menu_items)
        super().add_items(*[self.as_item(i) for i in items if i is not None])
        added = self.menu_items[count:]
        del self.menu_items[count:]
        self.menu_items[position:position] = added
        return self

    def index(self, button_name):
        for position, item in enumerate(self.menu_items):
            if getattr(item, 'button_name', None) == button_name:
                return position
        raise KeyError(button_name)

    def get(self, button_name, default=None):
        try:
            return self[button_name]
        except KeyError:
            return default

    def __getitem__(self, button_name):
        return self.menu_items[self.index(button_name)]

    def __contains__(self, button_name):
        return self.get(button_name) is not None

    def remove(self, *button_names):
        self.menu_items = [i for i in self.menu_items if getattr(i, 'button_name', None) not in button_names]
        return self

    def replace(self, button_name, *items):
        position = self.index(button_name)
        del self.menu_items[position]
        return self.insert(position, *items)

    def clear(self):
        self.menu_items = []
        return self

    def __str__(self):
        return self.render()

    def __html__(self):
        return mark_safe(self.render())
