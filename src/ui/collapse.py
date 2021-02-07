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
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout
from src.ui.focusedkeylisten import PassiveFocusBehavior


class CollapseBehavior:
    """animates a widget's collapsing and expanding"""

    collapsed = BooleanProperty(False)
    collapsable = BooleanProperty(True)
    expanded_height = NumericProperty()
    expanded_y = NumericProperty()
    collapsed_height = NumericProperty()

    transition = StringProperty("in_quint")
    duration = NumericProperty(0.2)

    def _get_collapsed_y(self):
        expanded_top = self.expanded_y + self.expanded_height
        collapsed_y = expanded_top - self.collapsed_height
        return collapsed_y

    collapsed_y = AliasProperty(
        _get_collapsed_y,
        None,
        rebind=True,
        bind=["expanded_y", "expanded_height"],
    )


class CollapseBar(PassiveFocusBehavior, FloatLayout):
    """collapses and expands it's dependant"""

    dependant = ObjectProperty()
    dependant_collapsed = BooleanProperty(False)
    collapsable = BooleanProperty(True)

    font_size = NumericProperty("12sp")
    # todo won't work on windows, use os join
    collapse_image = StringProperty("media/arrow-142-512.png")
    expand_image = StringProperty("media/arrow-204-512.png")

    def on_touch_up(self, touch):
        button = touch.button  # todo DRY with Abstract Focus
        if (
            self.collide_point(*touch.pos)
            and not button.startswith("scroll")
            and self.collapsable
        ):
            self.modify_dependant()
            return True
        return super().on_touch_up(touch)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ("enter", "numpadenter") and self.collapsable:
            self.modify_dependant()
            return True
        return super().on_keyboard_down(keyboard, keycode, text, modifiers)

    def modify_dependant(self):
        """collapse or expand dependant"""
        if self.dependant_collapsed:
            self.add_widget(self.dependant)
        else:
            self.remove_widget(self.dependant)
        self.dependant_collapsed = not self.dependant_collapsed

    def on_dependant_collapsed(self, *_):
        self.dependant.collapsed = self.dependant_collapsed


Factory.register("CollapseBehavior", CollapseBehavior)
