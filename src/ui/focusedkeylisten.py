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
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from src.ui.focus import AbstractFocus
from src.ui.keylisten import KeyListenBehavior


class FocusKeyListenBehavior(AbstractFocus, KeyListenBehavior):
    """cycle through focusable widgets"""

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "tab":
            if "shift" in modifiers:
                self.set_focus_previous()
            else:
                self.set_focus_next()
            return True
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)

    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == "escape":
            self.focus = False
            return True
        return super().on_keyboard_up(keyboard, keycode)


class PassiveFocusBehavior(AbstractFocus):
    """Dictates what to focus next without actually requesting the keyboard"""

    keyboard_listener = ObjectProperty(rebind=True)  # instance of KeyListen

    def on_focus(self, *_):
        self.set_focus_next_and_previous()
        super().on_focus(*_)

    def set_focus_next_and_previous(self):
        if self.focus:
            self.keyboard_listener.focus_next = self.focus_next
            self.keyboard_listener.focus_previous = self.focus_previous


Factory.register("FocusKeyListenBehavior", FocusKeyListenBehavior)
