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
import copy

from .hor_scroll import InfiniteHorScroll
from .mark import Mark
from datetime import datetime as py_datetime, timezone
from kivy.clock import Clock
from kivy.graphics import Ellipse
from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    BoundedNumericProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.metrics import sp
from kivy.uix.floatlayout import FloatLayout
from src.customdate import DateUnits
from src.utils import gregorian_datetime
from typing import Union


class BaseTimeline(FloatLayout, InfiniteHorScroll):
    """Abstract class for timelines"""

    datetime = ObjectProperty(gregorian_datetime)

    start_moment = ListProperty(  # todo make ordinal decimal
        [py_datetime.now(timezone.utc).astimezone().toordinal(), 0]
    )
    time_span = ListProperty([730, 43200])  # (delta days, seconds into day)  # todo should be day decimal

    def _get_end_moment(self) -> tuple[int, int]:
        end_ordinal = self.start_moment[0] + self.time_span[0]
        end_seconds_into_day = self.start_moment[1] + self.time_span[1]
        return end_ordinal, end_seconds_into_day

    def _set_end_moment(self, value: tuple[int, int]) -> None:
        start_ordinal = value[0] - self.time_span[0]
        start_seconds_into_day = value[1] - self.time_span[1]
        self.start_moment = [start_ordinal, start_seconds_into_day]

    end_moment = AliasProperty(
        _get_end_moment, _set_end_moment, bind=["start_moment", "time_span"]
    )

    primary_mark: Mark
    secondary_mark: Mark
    marks: list

    def __init__(self, **kwargs):
        super(BaseTimeline, self).__init__(**kwargs)
        for mark in self.marks:
            self.add_widget(mark)
        self.bind(pos=self.update_marks_bbox, size=self.update_marks_bbox)

    def moment_to_x(self, moment: tuple[int, int]) -> float:
        dt = self.datetime  # obsolete by self.dod_to_x
        start_moment, end_moment = self.start_moment, self.end_moment
        total_seconds = dt.elapsed_seconds(end_moment, start_moment)
        seconds_since_start = dt.elapsed_seconds(moment, start_moment)
        delta_x = self.width * (seconds_since_start / total_seconds)
        return self.x + delta_x

    def on_scroll_by(self, *_) -> None:
        """Scroll all marks when BaseTimeline scrolls"""
        """for mark in self.marks:
            mark.scroll_by = self.scroll_by"""
        print(self.scroll_by)
        ordinal_decimal_shift = self.dx_to_dod(self.scroll_by * 30)
        ord_n_secs = self.datetime.split_ordinal_decimal(ordinal_decimal_shift)
        ordinal, seconds = ord_n_secs
        self.start_moment = self.start_moment[0] - ordinal, self.start_moment[1] - seconds
        self.end_moment = self.end_moment[0] - ordinal, self.end_moment[1] - seconds

    def update_marks_bbox(self, *_):
        """Update child Mark(s) bounding box"""
        for mark in self.marks:
            mark.pos = self.pos
            mark.size = self.size

    #
    # Time Conversions
    #
    def dx_to_dod(self, dx: float) -> float:
        """change in pixels to change in ordinal decimal"""
        span = self.datetime.moment_to_ordinal_decimal(self.time_span)
        return span * (dx / self.width)

    def dod_to_dx(self, dod: float) -> float:
        """change in ordinal decimal to change in pixels"""
        span = self.datetime.moment_to_ordinal_decimal(self.time_span)
        return self.width * (dod / span)

    def od_to_x(self, ordinal_decimal: float) -> float:
        """convert ordinal decimal to x position"""
        dod = ordinal_decimal - self.datetime.moment_to_ordinal_decimal(
            self.start_moment
        )
        return self.x + self.dod_to_dx(dod)

    def x_to_od(self, x: float) -> float:
        """convert x position to ordinal decimal"""
        dx = x - self.x
        start_ordinal_decimal = self.datetime.moment_to_ordinal_decimal(
            self.start_moment
        )
        return start_ordinal_decimal + self.dx_to_dod(dx)


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

    # todo add increment_hms
    primary_mark_interval = ListProperty([1, DateUnits.YEAR])
    primary_moments = ListProperty(list())

    secondary_mark_width = BoundedNumericProperty(5, min=1)
    secondary_mark_height = BoundedNumericProperty(5, min=1)
    secondary_mark_y = BoundedNumericProperty(50, min=1)
    secondary_mark_interval = ListProperty([3, DateUnits.MONTH])

    scroll_interval = ListProperty([10, DateUnits.DAY])
    # todo remake moments if scroll hits threshold

    def __init__(self, **kwargs):
        # primary_moments = self.make_moments(self.primary_mark_interval)
        self.primary_mark = Mark(interval=self.primary_mark_interval)
        self.secondary_mark = Mark(
            label_align=Mark.LABEL_CENTER,
            mark=Ellipse,
            mark_width=sp(self.secondary_mark_width),
            mark_height=sp(self.secondary_mark_height),
            # todo add moments,
        )
        self.marks = [self.primary_mark]  # todo add secondary mark
        self.bind(height=self.update_secondary_mark)
        super(Timeline, self).__init__(**kwargs)
        self.draw_marks_trigger = Clock.create_trigger(self.draw_all_marks)
        self.set_primary_moments_trigger = Clock.create_trigger(self.set_primary_moments)
        self.bind(size=self.draw_marks_trigger)

    def on_start_moment(self, *_) -> None:
        self.draw_marks_trigger()
        # self.set_primary_moments()

    def set_primary_moments(self, *_) -> None:
        self.primary_mark.moments = self.make_moments(
            self.primary_mark_interval
        )
        # todo secondary_moments/ordinal decimal

    def make_moments(self, interval: tuple[int, int], *_) -> list:
        def append_next_moment(
            _moments: list, _ast_ymd: tuple[int, int, int]
        ) -> tuple[tuple[int, int], tuple[int, Union[int, None], int]]:
            _ast_ymd = self.datetime.date.increment_ast_ymd(
                _ast_ymd, [interval]
            )
            _moment = self.datetime.ast_ymd_to_moment(_ast_ymd)
            _moments.append(_moment)
            _ordinal_decimal = self.datetime.moment_to_ordinal_decimal(_moment)
            return _ordinal_decimal, _ast_ymd

        start_ast_ymd = self.datetime.moment_to_ast_ymd(self.start_moment)
        offscreen_ast_ymd = self.datetime.date.increment_ast_ymd(
            start_ast_ymd, [[-interval[0], interval[1]]]  # fixme ugly
        )
        offscreen_moment = self.datetime.ast_ymd_to_moment(offscreen_ast_ymd)
        offscreen_ordinal_decimal = self.datetime.moment_to_ordinal_decimal(
            offscreen_moment
        )
        moment = copy.deepcopy(offscreen_moment)
        ordinal_decimal = self.datetime.moment_to_ordinal_decimal(moment)
        ast_ymd = copy.deepcopy(offscreen_ast_ymd)

        moments = list()
        moments.append(moment)
        span = self.datetime.moment_to_ordinal_decimal(self.time_span)
        # ^ not a real ordinal decimal but the math works ^

        end_ordinal_decimal = self.datetime.moment_to_ordinal_decimal(self.end_moment)
        while ordinal_decimal < end_ordinal_decimal:
            ordinal_decimal, ast_ymd = append_next_moment(moments, ast_ymd)
        _ = append_next_moment(moments, ast_ymd)  # add moment offscreen
        return moments

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
