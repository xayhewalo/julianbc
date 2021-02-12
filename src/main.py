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
import os

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from src.ui.collapse import CollapseBehavior
from src.ui.eventview import EventView
from src.ui.focus import AbstractFocus
from src.ui.imagebutton import HoverImageButton, HoverImageToggleButton
from src.ui.mark import Mark
from src.ui.markbar import MarkBar

ui_directory = "ui"
Builder.load_file(os.path.join(ui_directory, "collapse.kv"))
Builder.load_file(os.path.join(ui_directory, "eventview.kv"))
Builder.load_file(os.path.join(ui_directory, "headerbar.kv"))
Builder.load_file(os.path.join(ui_directory, "imagebutton.kv"))
Builder.load_file(os.path.join(ui_directory, "markbar.kv"))
Builder.load_file(os.path.join(ui_directory, "textboundlabel.kv"))
Builder.load_file(os.path.join(ui_directory, "timeline.kv"))


class JulianBC(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = ModalView(size_hint=[0.4, 0.4])
        label = Label(
            text="This feature is not implemented yet"
            "\n\nClick outside this popup to dismiss it."
        )
        self.popup.add_widget(label)

    # def on_start(self):
    #     import cProfile
    #     self.profile = cProfile.Profile()
    #     self.profile.enable()

    # def on_stop(self):
    #     import pstats
    #     self.profile.disable()
    #     self.profile.dump_stats("myapp.profile")
    #     s = pstats.Stats("myapp.profile")
    #     s.strip_dirs().sort_stats("time").print_stats()

    def build(self):
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    Factory.register("AbstractFocus", AbstractFocus)
    Factory.register("CollapseBehavior", CollapseBehavior)
    Factory.register("EventView", EventView)
    Factory.register("Mark", Mark)
    Factory.register("MarkBar", MarkBar)
    Factory.register("HoverImageButton", HoverImageButton)
    Factory.register("HoverImageToggleButton", HoverImageToggleButton)

    JulianBC().run()
