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
from kivy.base import EventLoop
from kivy.factory import Factory


class MouseListenBehavior:
    """Listen to the Window's mouse position"""

    def __init__(self, **kwargs):
        EventLoop.window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__(**kwargs)

    # noinspection PyUnresolvedReferences
    def on_mouse_pos(self, window, mouse_pos):
        if self.disabled:
            return True
        for child in self.children:
            if child.dispatch("on_mouse_pos", window, mouse_pos):
                return True
