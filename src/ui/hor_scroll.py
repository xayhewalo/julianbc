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
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.widget import Widget


class InfiniteHorScroll(Widget):
    """Infinite horizontal scrolling."""

    scroll_by = NumericProperty(0)
    hor_scrolling = BooleanProperty(False)

    def on_touch_down(self, touch):
        if super(InfiniteHorScroll, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            # Touched widget but children didn't use touch, must be scrolling
            self.hor_scrolling = True
            touch.grab(self)
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.hor_scrolling:
            self.scroll_by = touch.dx
            return True
        return super(InfiniteHorScroll, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and self.hor_scrolling:
            touch.ungrab(self)
            self.hor_scrolling = False
        return super(InfiniteHorScroll, self).on_touch_up(touch)
