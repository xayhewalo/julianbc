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
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from src.ui.headerbar import HeaderBar
from src.ui.timeline import ComboTimeline
from src.setup_db import gregorian_datetime


class MainApp(App):
    def build(self):
        root = FloatLayout()
        box = BoxLayout(orientation="vertical")
        timeline = ComboTimeline(cdt=gregorian_datetime)
        box.add_widget(HeaderBar())
        box.add_widget(timeline)
        root.add_widget(box)
        return root

    @staticmethod
    def show_not_implemented_popup() -> None:
        modal = ModalView(size_hint=[0.4, 0.4])
        label = Label(
            text="This feature is not implemented yet."
                 "\n\nClick outside this popup to dismiss it."
        )
        modal.add_widget(label)
        modal.open()


if __name__ == "__main__":
    MainApp().run()
