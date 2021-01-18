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
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from src.customdatetime import ConvertibleDateTime
from src.customdate import ConvertibleDate


Builder.load_string("""
#:import utils src.ui.utils
<CalendarChanger>:
    canvas:
        Color:
            rgba: utils.SURFACE_COLOR
        Rectangle:
            pos: self.pos
            size: self.size
""")


class CalendarChanger(FloatLayout):
    """Change a timeline's calendar based on user input"""

    def draw(self):
        app = App.get_running_app()
        timeline = app.timeline_screen.children[0].children[1]  # fixme disgusting
        calendar = timeline.cdt.date.calendar
        all_calendars = list()
        all_calendars.extend([calendar, *calendar.calendars()])
        num_cals = len(all_calendars)
        for idx, cal in enumerate(all_calendars):
            button = Button(text=cal.name, size_hint=[0.1, 0.1], pos_hint={"center_x": 0.5, "y": idx / num_cals})
            time = timeline.cdt.time
            date = ConvertibleDate(calendar=cal)
            button.cdt = ConvertibleDateTime(date=date, time=time)
            button.bind(on_release=self.change_calendar)
            self.add_widget(button)
            # [self.add_widget(Button(text=cal.name)) for cal in all_calendars]

    def change_calendar(self, *args):
        obj = None
        for arg in args:
            if isinstance(arg, Button):
                obj = arg

        app = App.get_running_app()  # todo DRY
        timeline = app.timeline_screen.children[0].children[1]  # fixme disgusting
        timeline.cdt = obj.cdt
        collapse_button = app.timeline_screen.children[0].children[0]
        collapse_button.text = timeline.cdt.date.calendar.name  # fixme disgusting
        self.parent.remove_widget(self)

    def on_parent(self, *_):
        self.draw()
