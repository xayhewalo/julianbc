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
from kivy.animation import Animation
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.floatlayout import FloatLayout


class CollapseBar(FocusBehavior, FloatLayout):
    """collapses and expands it's children/dependant"""

    dependant = ObjectProperty()
    visible = BooleanProperty(True)

    transition = StringProperty("in_quint")
    duration = NumericProperty(0.2)

    font_size = NumericProperty("12sp")
    collapse_image = StringProperty("media/arrow-142-512.png")
    expand_image = StringProperty("media/arrow-204-512.png")

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.animate_dependant()
            return True
        return super().on_touch_up(touch)

    def animate_dependant(self):
        y = self.y if self.visible else self.y - self.dependant.height
        anim = Animation(y=y, t=self.transition, d=self.duration)
        anim.start(self.dependant)
        self.visible = not self.visible
