#  Copyright (c) 2021 author(s) of JulianBC.
#
#  This file is part of JulianBC.
#
#  JulianBC is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  JulianBC is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with JulianBC.  If not, see <https://www.gnu.org/licenses/>.
from kivy.properties import ObjectProperty
from src.ui.focus import AbstractFocus
from src.ui.keylisten import KeyListenBehavior


class FocusKeyListenBehavior(AbstractFocus, KeyListenBehavior):
    """cycle through focusable widgets"""

    passive_listener = ObjectProperty(allownone=True, rebind=True)

    # useful when passive_listener changes focus_next and focus_previous
    default_focus_previous = ObjectProperty(allownone=True, rebind=True)
    default_focus_next = ObjectProperty(allownone=True, rebind=True)
    next_active_listener = ObjectProperty(alllownone=True, rebind=True)
    previous_active_listener = ObjectProperty(allownone=True, rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection PyUnresolvedReferences
        self.bind(focus=self.request_keyboard)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "tab":
            if "shift" in modifiers:
                self.set_focus_previous()
            else:
                self.set_focus_next()
            return True

        if self.passive_listener:
            if self.passive_listener.on_keyboard_down(
                keyboard, keycode, text, modifiers
            ):
                return True
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)

    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == "escape":
            self.focus = False
            return True

        if self.passive_listener:
            if self.passive_listener.on_keyboard_up(keyboard, keycode):
                return True
        return super().on_keyboard_up(keyboard, keycode)


class PassiveFocusBehavior(AbstractFocus):
    """
    Dictates what to focus next without actually requesting the keyboard
    Keyboard listener should call on_keyboard_* on behalf of these instances
    """

    keyboard_listener = ObjectProperty(rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection PyUnresolvedReferences
        self.bind(
            focus_next=self.set_focus_next_and_previous,
            focus_previous=self.set_focus_next_and_previous,
        )

    def on_kv_post(self, base_widget):
        # noinspection PyUnresolvedReferences
        super().on_kv_post(base_widget)
        self.keyboard_listener.bind(keyboard=self.reset_listener)

    def reset_listener(self, *_):
        kb_listener = self.keyboard_listener
        if kb_listener.keyboard is None:
            kb_listener.focus_next = kb_listener.default_focus_next
            kb_listener.focus_previous = kb_listener.default_focus_previous

    def set_passive_listener(self):
        if self.keyboard_listener and self.focus:
            self.keyboard_listener.passive_listener = self

    def on_focus(self, *_):
        self.set_focus_next_and_previous()
        self.set_passive_listener()
        super().on_focus(*_)

    def set_focus_next_and_previous(self, *_):
        if self.focus:
            self.keyboard_listener.request_keyboard()
            self.keyboard_listener.focus_next = self.focus_next
            self.keyboard_listener.focus_previous = self.focus_previous

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        pass

    def on_keyboard_up(self, keyboard, keycode):
        pass
