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
from kivy.core.window import Window


class KeyListenBehavior:
    """listen to the Window's keyboard events"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard = None
        self.request_keyboard()

    def request_keyboard(self, *_):
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(
            on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up
        )

    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        pass

    def on_keyboard_up(self, keyboard, keycode):
        pass
