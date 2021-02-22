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
from kivy.metrics import sp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.vector import Vector


class ZoomBehavior:
    """A hacky class to zoom without storing a potentially infinite number"""

    disable_zoom_in = BooleanProperty(False)
    disable_zoom_out = BooleanProperty(False)
    zoom_by = NumericProperty()
    pinch_zooming = BooleanProperty(False)
    touches = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._zoom_by = sp(20)

    def on_touch_down(self, touch):
        self.zoom_by = 0

        # noinspection PyUnresolvedReferences
        if super().on_touch_down(touch):
            return True

        consumed_touch = False
        # noinspection PyUnresolvedReferences
        if self.collide_point(*touch.pos):
            button = touch.button
            self.touches.append(touch)
            if button == "scrollup" and not self.disable_zoom_in:
                # noinspection PyUnresolvedReferences
                self.gain_focus()
                self.zoom_by = self._zoom_by
                consumed_touch = True
            elif button == "scrolldown" and not self.disable_zoom_out:
                # noinspection PyUnresolvedReferences
                self.gain_focus()
                self.zoom_by = -self._zoom_by
                consumed_touch = True
            elif len(self.touches) == 2 and not button.startswith("scroll"):
                # AbstractFocus should handle focusing in this case
                touch.grab(self)
                self.pinch_zooming = True
                consumed_touch = True
        return consumed_touch

    def on_touch_move(self, touch):
        """based on kivy.uix.scatter"""

        if touch.grab_current and self.pinch_zooming:
            self.zoom_by = 0

            anchor = Vector(self.touches[0].pos)
            old_distance = anchor.distance(touch.ppos)
            new_distance = anchor.distance(touch.pos)
            if old_distance > new_distance:
                self.zoom_by = self._zoom_by
                return True
            elif new_distance > old_distance:
                self.zoom_by = -self._zoom_by
                return True
        # noinspection PyUnresolvedReferences
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch in self.touches:
            self.touches.remove(touch)
            if touch.grab_current == self and self.pinch_zooming:
                touch.ungrab(self)
        # noinspection PyUnresolvedReferences
        return super().on_touch_up(touch)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """zoom with ctrl + '+' or ctrl + '-'"""
        self.zoom_by = 0

        key = keycode[1]
        ctrl = "ctrl" in modifiers
        ctrl_numpadadd_add = key == "numpadadd" and ctrl
        ctrl_shift_add = key == "=" and {"shift", "ctrl"}.issubset(modifiers)
        if ctrl_numpadadd_add or ctrl_shift_add:
            self.zoom_by = self._zoom_by
            return True

        ctrl_numpadsubtract = key == "numpadsubstract" and ctrl
        ctrl_shift_subtract = key == "-" and ctrl and "shift" not in modifiers
        if ctrl_numpadsubtract or ctrl_shift_subtract:
            self.zoom_by = -self._zoom_by
            return True
        # noinspection PyUnresolvedReferences
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)
