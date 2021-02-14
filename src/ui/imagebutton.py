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
from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    StringProperty,
)
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from src.ui.focusedkeylisten import FocusKeyListenBehavior
from src.ui.mouselisten import MouseListenBehavior


class ChangeButtonBgColor:
    normal_color = ListProperty([0, 0, 0, 0])
    down_color = ListProperty([1, 1, 1, 0.5])
    current_color = ListProperty(normal_color.defaultvalue)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection PyUnresolvedReferences
        self.bind(state=self.change_color)

    def change_color(self, *_):
        # noinspection PyUnresolvedReferences
        if self.state == "normal":
            self.current_color = self.normal_color
        else:
            self.current_color = self.down_color


class HoverChangeBgColor(FocusKeyListenBehavior, MouseListenBehavior):
    """change color when mouse hovers over the button"""

    hover_color = ListProperty([1, 1, 1, 0.2])
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection PyUnresolvedReferences
        self.bind(hovered=self.change_color, focus=self.change_color)

    # noinspection PyUnresolvedReferences
    def change_color(self, *_):
        super().change_color(*_)
        if (self.hovered or self.focus) and self.state == "normal":
            # noinspection PyAttributeOutsideInit
            self.current_color = self.hover_color

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ("enter", "numpadenter"):
            # noinspection PyUnresolvedReferences
            self.on_press()
            return True
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)

    def on_mouse_pos(self, window, mouse_pos):
        # noinspection PyUnresolvedReferences
        if self.collide_point(*mouse_pos):
            self.hovered = True
            return True
        self.hovered = False
        return False


class ImageLayout(FloatLayout):
    """Size and position an image"""

    image_size_hint = ListProperty([1, 1])
    image_pos_hint = DictProperty({"center_x": 0.5, "center_y": 0.5})
    image_source = StringProperty("")


class HoverImageButton(
    HoverChangeBgColor,
    ChangeButtonBgColor,
    ButtonBehavior,
    ImageLayout,
):
    def on_press(self):
        App.get_running_app().popup.open()


class HoverImageToggleButton(
    HoverChangeBgColor,
    ChangeButtonBgColor,
    ToggleButtonBehavior,
    ImageLayout,
):
    def on_press(self):
        if self.state == "normal":
            App.get_running_app().popup.open()
