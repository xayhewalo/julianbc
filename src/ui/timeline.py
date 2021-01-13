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

from .hor_scroll import HorScrollBehavior
from .mark import Mark
from .utils import SURFACE_COLOR
from .zoom import ZoomBehavior
from src.customdatetime import DateUnits, TimeUnits
from src.setup_db import gregorian_datetime
from typing import Generator, Union
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.floatlayout import FloatLayout

Builder.load_string("""
#:import utils src.ui.utils
<ComboTimeline>:
    canvas:
        Color:
            rgba: utils.BACKGROUND_COLOR
        Rectangle:
            pos: self.pos
            size: self.size

    MarkedTimeline:
        size_hint: 1, 0.05
        pos_hint: {"top": 1}
        canvas.before:
            Color:
                rgba: 0.31, 0.31, 0.31, 0.95
            Rectangle:
                pos: self.pos
                size: self.size

    BareTimeline:
        size_hint: 1, 0.95
""")


class BaseTimeline(HorScrollBehavior, ZoomBehavior, FloatLayout):
    """Abstract class for timelines"""

    cdt = ObjectProperty(gregorian_datetime)  # ConvertibleDateTime

    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_ordinal_decimal = NumericProperty(__now_ordinal_decimal - 2.5)
    end_ordinal_decimal = NumericProperty(__now_ordinal_decimal + 2.5)

    def _get_time_span(self):
        return self.end_ordinal_decimal - self.start_ordinal_decimal

    time_span = AliasProperty(  # days visible on the timeline
        _get_time_span,
        None,
        bind=["start_ordinal_decimal", "end_ordinal_decimal"]
    )

    def on_scroll_by(self, *_) -> None:
        dod = self.dx_to_dod(self.scroll_by)
        self.start_ordinal_decimal -= dod
        self.end_ordinal_decimal -= dod
        self.scroll_siblings()

    def scroll_siblings(self) -> None:
        for sibling in self.gen_timeline_siblings():
            sibling.scroll_by = self.scroll_by

    def on_zoom_by(self, *_) -> None:
        dod = self.dx_to_dod(self.zoom_by)
        self.start_ordinal_decimal += dod
        self.end_ordinal_decimal -= dod
        self.zoom_siblings()

    def zoom_siblings(self) -> None:
        for sibling in self.gen_timeline_siblings():
            sibling.zoom_by = self.zoom_by

    def gen_timeline_siblings(
        self
    ) -> Generator["BaseTimeline", "BaseTimeline", None]:
        for child in self.parent.children:
            if isinstance(child, BaseTimeline) and child is not self:
                yield child

    #
    # Time Conversions
    #
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


class MarkedTimeline(BaseTimeline):
    """Contains date and time labels"""

    mark_interval = ListProperty([1, DateUnits.DAY])

    def __init__(self, **kwargs):
        super(BaseTimeline, self).__init__(**kwargs)
        self.mark = Mark(interval=self.mark_interval)
        self.add_widget(self.mark)
        self.draw_mark_trigger = Clock.create_trigger(self.draw_mark)
        self.bind(
            pos=self.update_mark_bbox,
            start_ordinal_decimal=self.draw_mark_trigger,
            end_ordinal_decimal=self.draw_mark_trigger,
            mark_interval=self.update_mark_interval,
        )

    def on_time_span(self, *_) -> None:
        unit = self.mark_interval[1]
        min_time_span = 5 / self.cdt.time.clock.seconds_in_day
        if unit == TimeUnits.SECOND and self.time_span <= min_time_span:
            self.disable_zoom_in = True
        else:
            self.disable_zoom_in = False

    def on_disable_zoom_in(self, *_) -> None:
        for sibling in self.gen_timeline_siblings():
            sibling.disable_zoom_in = self.disable_zoom_in

    def on_zoom_by(self, *_) -> None:
        """change mark intervals so all labels are visible"""
        super(MarkedTimeline, self).on_zoom_by(*_)
        mark = self.mark
        label_width = mark.max_label_width + (2 * mark.label_padding_x)
        increase_threshold = mark.interval_width * (2/3)
        decrease_threshold = mark.interval_width * (1/3)
        if label_width >= increase_threshold and self.zoom_by < 0:
            self.mark_interval = self.cdt.change_interval(self.mark_interval)
        elif label_width <= decrease_threshold and self.zoom_by > 0:
            self.mark_interval = self.cdt.change_interval(
                self.mark_interval, increase=False
            )

    def draw_mark(self, _) -> None:
        self.mark.draw_marks()

    def update_mark_bbox(self, *_) -> None:
        self.mark.pos = self.pos
        self.mark.size = self.size

    def update_mark_interval(self, *_) -> None:
        self.mark.interval = self.mark_interval

    def on_size(self, *_) -> None:
        self.draw_mark_trigger()
        self.update_mark_bbox()


class BareTimeline(BaseTimeline):
    """where the end-user adds events"""
    # todo don't add widgets, check db for visible events then make graphics for them

    def on_touch_down(self, touch):
        if touch.is_double_tap and self.collide_point(*touch.pos):
            with self.canvas:
                Color(SURFACE_COLOR)
                Line(rounded_rectangle=[*touch.pos, 100, 20, 2])
            return True
        return super(BareTimeline, self).on_touch_down(touch)


class ComboTimeline(BaseTimeline):
    """Combination of a MarkedTimeline and BareTimeline"""

    def __init__(self, **kwargs):
        super(ComboTimeline, self).__init__(**kwargs)
        self.bind(
            start_ordinal_decimal=self.update_ordinal_decimals,
            end_ordinal_decimal=self.update_ordinal_decimals,
            cdt=self.update_convertible_datetimes,
            height=self.update_mark_height,
        )

    def update_ordinal_decimals(self, *_) -> None:
        for child_tl in self.gen_child_timelines():
            child_tl.start_ordinal_decimal = self.start_ordinal_decimal
            child_tl.end_ordinal_decimal = self.end_ordinal_decimal

    def update_convertible_datetimes(self, *_) -> None:
        for child_tl in self.gen_child_timelines():
            child_tl.cdt = self.cdt

    def update_mark_height(self, *_) -> None:
        for marked_tl in self.gen_child_timelines():
            if isinstance(marked_tl, MarkedTimeline):
                marked_tl.mark.mark_height = self.height

    def gen_child_timelines(
        self
    ) -> Generator[BaseTimeline, BaseTimeline, None]:
        for child in self.children:
            if isinstance(child, BaseTimeline):
                yield child
