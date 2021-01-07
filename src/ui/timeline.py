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
import datetime

from .hor_scroll import InfiniteHorScroll
from .mark import Mark
from src.customdate import DateUnits
from src.utils import gregorian_datetime
from kivy.clock import Clock
from kivy.graphics import Ellipse
from kivy.lang import Builder
from kivy.metrics import sp
from kivy.properties import (
    AliasProperty,
    BoundedNumericProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.floatlayout import FloatLayout


class BaseTimeline(FloatLayout, InfiniteHorScroll):
    """Abstract class for timelines"""

    dt = ObjectProperty(gregorian_datetime)  # ConvertibleDateTime

    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_as_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_ordinal_decimal = NumericProperty(__now_as_ordinal_decimal)
    end_ordinal_decimal = NumericProperty(__now_as_ordinal_decimal + 730)

    def _get_time_span(self):
        return self.end_ordinal_decimal - self.start_ordinal_decimal

    time_span = AliasProperty(  # days visible on the timeline
        _get_time_span,
        None,
        bind=["start_ordinal_decimal", "end_ordinal_decimal"]
    )

    primary_mark: Mark
    secondary_mark: Mark
    marks: list

    def __init__(self, **kwargs):
        super(BaseTimeline, self).__init__(**kwargs)
        for mark in self.marks:
            self.add_widget(mark)
        self.bind(pos=self.update_marks_bbox, size=self.update_marks_bbox)

    def on_scroll_by(self, *_) -> None:
        dod = self.dx_to_dod(self.scroll_by)
        self.start_ordinal_decimal -= dod
        self.end_ordinal_decimal -= dod

    def od_to_x(self, od: float) -> float:
        """convert ordinal decimal to x position"""
        dod = od - self.start_ordinal_decimal
        return self.x + self.dod_to_dx(dod)

    def dod_to_dx(self, dod: float) -> float:
        """convert change in ordinal decimal to change in pixels"""
        return self.width * (dod / self.time_span)

    def dx_to_dod(self, dx: float) -> float:
        """convert change in pixels to change in ordinal decimal"""
        return self.time_span * (dx / self.width)

    def update_marks_bbox(self, *_) -> None:
        """Update child Mark(s) bounding box"""
        for mark in self.marks:
            mark.pos = self.pos
            mark.size = self.size


kv = """
#:import utils src.ui.utils
<Timeline>:
    size_hint: 1, 0.8
    canvas:
        Color:
            rgb: utils.BACKGROUND_COLOR
        Rectangle:
            pos: self.pos
            size: self.size
"""

Builder.load_string(kv)


class Timeline(BaseTimeline):
    """Where the end-user adds events"""

    primary_mark_interval = ObjectProperty(DateUnits.YEAR)

    secondary_mark_width = BoundedNumericProperty(5, min=1)
    secondary_mark_height = BoundedNumericProperty(5, min=1)
    secondary_mark_y = BoundedNumericProperty(50, min=1)
    secondary_mark_interval = ObjectProperty(DateUnits.MONTH)

    def __init__(self, **kwargs):
        self.primary_mark = Mark(interval=self.primary_mark_interval)
        self.secondary_mark = Mark(
            label_align=Mark.LABEL_CENTER,
            mark=Ellipse,
            mark_width=sp(self.secondary_mark_width),
            mark_height=sp(self.secondary_mark_height),
            interval=self.secondary_mark_interval,
        )
        self.marks = [self.primary_mark, self.secondary_mark]
        super(Timeline, self).__init__(**kwargs)
        self.draw_marks_trigger = Clock.create_trigger(self.draw_all_marks)
        self.bind(
            height=self.update_secondary_mark,
            size=self.draw_marks_trigger,
            start_ordinal_decimal=self.draw_marks_trigger,
            end_ordinal_decimal=self.draw_marks_trigger,
        )

    def draw_all_marks(self, _) -> None:
        for mark in self.marks:
            mark.draw_marks()

    def update_secondary_mark(self, *_) -> None:
        self.secondary_mark.mark_y = self.height - sp(self.secondary_mark_y)
        self.secondary_mark.label_y = (
            self.height
            - sp(self.secondary_mark_y)
            + sp(self.secondary_mark_height)
        )
