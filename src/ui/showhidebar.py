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
    BooleanProperty, NumericProperty, ObjectProperty, StringProperty
)
from kivy.uix.button import Button


class ShowHideBar(Button):
    dependant = ObjectProperty(None)  # the content to show and hide
    visible = BooleanProperty(True)

    # animation properties
    transition = StringProperty("in_quint")
    duration = NumericProperty(0.2)

    def __init__(self, **kwargs):
        super(ShowHideBar, self).__init__(**kwargs)
        self.bind(on_release=self.animate_dependant)

    def animate_dependant(self, _):
        y = self.y if self.visible else self.y - self.dependant.height
        anim = Animation(y=y, t=self.transition, d=self.duration)
        anim.start(self.dependant)
        self.visible = not self.visible
