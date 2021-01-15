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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, NoTransition
from src.ui.headerbar import HeaderBar
from src.ui.timeline import TimelineScreen


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.sm = ScreenManager(transition=NoTransition())

    def build(self):
        root = FloatLayout()
        timeline_screen = TimelineScreen(size_hint=[1, 0.9])
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(timeline_screen)
        root.add_widget(self.sm)
        root.add_widget(HeaderBar(size_hint=[1, 0.1], pos_hint={"top": 1}))
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
