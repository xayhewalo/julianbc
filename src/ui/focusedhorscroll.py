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


class HorScrollBehavior:
    """Infinite horizontal scrolling"""

    scroll_by = NumericProperty()
    drag_hor_scrolling = BooleanProperty(False)
    disable_drag_hor_scroll = BooleanProperty(False)
    shift_key = BooleanProperty(False)
    left_key = BooleanProperty(False)
    right_key = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scroll_by = sp(20)

    def on_touch_down(self, touch):
        """touchpad and mouse scroll scrolling"""

        # noinspection PyUnresolvedReferences
        if super().on_touch_down(touch):
            return True

        # noinspection PyUnresolvedReferences
        if self.collide_point(*touch.pos):
            # Touched widget but children didn't use touch, must be scrolling
            button = touch.button
            shift_key = self.shift_key
            if button == "scrollleft" or button == "scrolldown" and shift_key:
                # noinspection PyUnresolvedReferences
                self.gain_focus()
                self.scroll_by = -self._scroll_by
                self.cleanup_scroll()
                return True
            elif button == "scrollright" or button == "scrollup" and shift_key:
                # noinspection PyUnresolvedReferences
                self.gain_focus()
                self.scroll_by = self._scroll_by
                self.cleanup_scroll()
                return True
        return False

    def on_touch_move(self, touch):
        """touch/click and drag scrolling"""

        disable_drag_hor_scroll = self.disable_drag_hor_scroll
        # noinspection PyUnresolvedReferences
        if (
            self.collide_point(*touch.pos)
            and touch.dx != 0
            and not disable_drag_hor_scroll
        ):
            if touch.grab_current is not self:
                self.drag_hor_scrolling = True
                touch.grab(self)
                # noinspection PyUnresolvedReferences
                self.get_root_window().set_system_cursor("hand")
            self.scroll_by = touch.dx
            return True
        # noinspection PyUnresolvedReferences
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current == self and self.drag_hor_scrolling:
            touch.ungrab(self)
            # noinspection PyUnresolvedReferences
            self.get_root_window().set_system_cursor("arrow")
            self.cleanup_scroll()
        # noinspection PyUnresolvedReferences
        return super().on_touch_up(touch)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ("shift", "rshift"):
            self.shift_key = True
            return True
        elif self.is_left_key(keycode, modifiers):
            # noinspection PyUnresolvedReferences
            self.gain_focus()
            self.left_key = True
            self.scroll_by = -self._scroll_by
            self.cleanup_scroll()
            return True
        elif self.is_right_key(keycode, modifiers):
            # noinspection PyUnresolvedReferences
            self.gain_focus()
            self.right_key = True
            self.scroll_by = self._scroll_by
            self.cleanup_scroll()
            return True
        # noinspection PyUnresolvedReferences
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)

    def on_keyboard_up(self, keyboard, keycode):
        # i don't think we want to consume keys here?...
        if keycode[1] in ("shift", "rshift") and self.shift_key:
            self.shift_key = False
        if self.left_key and self.is_left_key(keycode):
            self.left_key = False
        if self.right_key and self.is_right_key(keycode):
            self.right_key = False
        # noinspection PyUnresolvedReferences
        return super().on_keyboard_up(keyboard, keycode)

    @staticmethod
    def is_left_key(keycode: list[int, str], modifiers: list = None) -> bool:
        k = keycode[1]
        if modifiers is not None:
            return k == "left" or (k == "numpad4" and "numlock" in modifiers)
        return k in ("left", "numpad4")

    @staticmethod
    def is_right_key(keycode: list[int, str], modifiers: list = None) -> bool:
        k = keycode[1]
        if modifiers is not None:
            return k == "right" or (k == "numpad6" and "numlock" in modifiers)
        return k in ("right", "numpad6")

    def cleanup_scroll(self):
        self.drag_hor_scrolling = False
        self.scroll_by = 0
