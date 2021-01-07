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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from src.ui.timeline import Timeline
from src.utils import gregorian_datetime


class MainApp(App):
    def build(self):
        root = FloatLayout()
        box = BoxLayout(orientation="vertical")
        timeline = Timeline(dt=gregorian_datetime)
        box.add_widget(timeline)
        root.add_widget(box)
        return root


if __name__ == "__main__":
    MainApp().run()
