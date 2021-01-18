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
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, NoTransition
from src.ui.calendarchanger import CalendarChanger
from src.ui.eventeditor import EventEditor
from src.ui.headerbar import HeaderBar
from src.ui.timeline import TimelineScreen


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.root = FloatLayout()
        self.screen_manager = ScreenManager(transition=NoTransition())
        self.event_editor = EventEditor(size_hint_y=0.9, x=800)
        self.timeline_screen = TimelineScreen(size_hint=[1, 0.9])

    def build(self):
        self.screen_manager = ScreenManager(transition=NoTransition())
        self.screen_manager.add_widget(self.timeline_screen)
        self.root.add_widget(self.screen_manager)
        self.root.add_widget(HeaderBar(size_hint=[1, 0.1], pos_hint={"top": 1}))
        self.root.add_widget(self.event_editor)
        return self.root

    def show_event_editor(self, start_od: float = None, end_od: float = None):
        if start_od is not None:
            self.event_editor.start = start_od
        if end_od is not None:
            self.event_editor.end = end_od

        anim = Animation(right=self.root.right, t="in_sine", d=0.2)  # todo bind
        anim.start(self.event_editor)

    def hide_event_editor(self) -> None:
        anim = Animation(x=self.root.right, t="out_sine", d=0.2)  # todo bind
        anim.start(self.event_editor)

    def show_calendar_changer(self):
        cc = CalendarChanger(
            pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=[0.5, 0.5]
        )
        self.root.add_widget(cc)

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
