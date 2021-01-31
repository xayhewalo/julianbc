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
from kivy.properties import BooleanProperty, NumericProperty


# noinspection PyUnresolvedReferences
class HorScrollBehavior:
    """
    Infinite horizontal scrolling
    Should be inherited left of FocusBehavior
    """

    scroll_by = NumericProperty()  # this is what events should bind to
    drag_hor_scrolling = BooleanProperty(False)
    disable_drag_hor_scroll = BooleanProperty(False)
    shift_key = BooleanProperty(False)
    left_key = BooleanProperty(False)
    right_key = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collision = None
        self._scroll_by = sp(20)

    def on_touch_down(self, touch):
        """touchpad and mouse scroll scrolling"""

        if super().on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            # Touched widget but children didn't use touch, must be scrolling
            self._collision = True
            button = touch.button
            shift_scrollleft = (button == "scrolldown" and self.shift_key)
            shift_scrollright = (button == "scrollup" and self.shift_key)
            if touch.button == "scrollleft" or shift_scrollleft:
                self.focus = True
                self.scroll_by = - self._scroll_by
                self.cleanup_scroll()
                return True
            elif touch.button == "scrollright" or shift_scrollright:
                # noinspection PyAttributeOutsideInit
                self.focus = True
                self.scroll_by = self._scroll_by
                self.cleanup_scroll()
                return True
        return False

    def on_touch_move(self, touch):
        """touch/click and drag scrolling"""

        disable_drag_hor_scroll = self.disable_drag_hor_scroll
        if self._collision and touch.dx != 0 and not disable_drag_hor_scroll:
            # Should have already gained focus through FocusBehavior
            if touch.grab_current is not self:
                self.drag_hor_scrolling = True
                touch.grab(self)
                self.get_root_window().set_system_cursor("hand")
            self.scroll_by = touch.dx
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and self.drag_hor_scrolling:
            touch.ungrab(self)
            self.get_root_window().set_system_cursor("arrow")
            self.cleanup_scroll()
        return super().on_touch_up(touch)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] in ("shift", "rshift"):
            self.shift_key = True
            return True
        elif self.left_key_down(keycode, modifiers):
            self.left_key = True
            self.scroll_by = -self._scroll_by
            self.cleanup_scroll()
        elif self.right_key_down(keycode, modifiers):
            self.right_key = True
            self.scroll_by = self._scroll_by
            self.cleanup_scroll()
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_key_up(self, window, keycode):
        # i don't think we want to consume keys here?...
        if keycode[1] in ("shift", "rshift"):
            self.shift_key = False
        if self.left_key and self.left_key_down(keycode):
            self.left_key = False
        elif self.right_key and self.right_key_down(keycode):
            self.right_key = False
        return super().keyboard_on_key_up(window, keycode)

    @staticmethod
    def left_key_down(keycode: list[int, str], modifiers: list = None) -> bool:
        key = keycode[1]
        if modifiers:
            return key == "left" or key == "numpad4" and "numlock" in modifiers
        return key == "left" or key == "numpad4"

    @staticmethod
    def right_key_down(keycode: list[int, str], modifiers: list = None) -> bool:
        k = keycode[1]
        if modifiers:
            return k == "right" or k == "numpad6" and "numlock" in modifiers
        return k == "right" or k == "numpad6"

    def cleanup_scroll(self):
        self.drag_hor_scrolling = False
        self.scroll_by = 0
        self._collision = False
