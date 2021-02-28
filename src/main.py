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
import pathlib

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from os.path import join, split
from src.ui.collapse import CollapseBehavior
from src.ui.eventview import EventView
from src.ui.focus import AbstractFocus
from src.ui.imagebutton import HoverImageButton, HoverImageToggleButton
from src.ui.mark import Mark
from src.ui.markbar import MarkBar
from src.ui.timeline import TimelineScreen


class JulianBC(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = ModalView(size_hint=[0.4, 0.4])
        label = Label(
            text="This feature is not implemented yet"
            "\n\nClick outside this popup to dismiss it."
        )
        self.popup.add_widget(label)

    def build(self):
        Factory.register("AbstractFocus", AbstractFocus)
        Factory.register("CollapseBehavior", CollapseBehavior)
        Factory.register("EventView", EventView)
        Factory.register("HoverImageButton", HoverImageButton)
        Factory.register("HoverImageToggleButton", HoverImageToggleButton)
        Factory.register("Mark", Mark)
        Factory.register("MarkBar", MarkBar)
        Factory.register("TimelineScreen", TimelineScreen)  # todo test

        abs_src_path = split(__file__)[0]
        [  # load all *.kv files that not are the main kv file
            Builder.load_file(str(path))
            for path in pathlib.Path(abs_src_path).glob(join("**", "*.kv"))
            if "main.kv" not in str(path)
        ]
        return Builder.load_file(join(abs_src_path, "main.kv"))


def main():
    if __name__ == "__main__":
        JulianBC().run()


main()
