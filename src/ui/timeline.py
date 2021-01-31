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

from kivy.clock import Clock
from kivy.properties import (
    AliasProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from src.ui.focusedhorscroll import HorScrollBehavior
from src.ui.focusedzoom import ZoomBehavior


class Timeline(HorScrollBehavior, ZoomBehavior, FocusBehavior, FloatLayout):
    """Where the end-user adds events"""

    cdt = ObjectProperty()

    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_od = NumericProperty(__now_ordinal_decimal - 1)  # od @ x = 0
    end_od = NumericProperty(__now_ordinal_decimal + 1)  # od @ x = self.width

    def _get_time_span(self):
        return self.end_od - self.start_od

    time_span = AliasProperty(
        _get_time_span,
        None,
        bind=["start_od", "end_od"],
    )

    mark_interval = ListProperty()
    extend_time_span_by = NumericProperty(1)

    def _get_extended_start_od(self):
        factor = self.extend_time_span_by
        return self.cdt.extend_od(
            self.start_od, self.mark_interval, factor, reverse=True
        )

    extended_start_od = AliasProperty(
        _get_extended_start_od,
        None,
        bind=["start_od", "extend_time_span_by"],
        cache=True,  # fixme uncommenting makes 1-2 second interval scroll/zoom work...sort off
    )

    def _get_extended_end_od(self):
        return self.cdt.extend_od(
            self.end_od, self.mark_interval, self.extend_time_span_by
        )

    extended_end_od = AliasProperty(
        _get_extended_end_od,
        None,
        bind=["end_od", "extend_time_span_by"],
        cache=True,  # fixme uncommenting makes 1-2 second interval scroll/zoom work...sort off
    )

    def _get_extended_time_span(self):
        return self.extended_end_od - self.extended_start_od

    extended_time_span = AliasProperty(
        _get_extended_time_span,
        None,
        bind=["extended_start_od", "extended_end_od"],
    )

    def _get_interval_width(self):
        end_x = self.od_to_x(self.end_od)
        extended_end_x = self.od_to_x(self.extended_end_od)
        return (extended_end_x - end_x) / self.extend_time_span_by

    interval_width = AliasProperty(
        _get_interval_width,
        None,
        bind=["extended_end_od", "end_od", "extend_time_span_by"],
        cache=True,
    )

    def __init__(self, **kwargs):
        self.draw_mark_trigger = Clock.create_trigger(self.draw_mark)
        super().__init__(**kwargs)
        self.bind(
            size=self.draw_mark_trigger,
            extended_start_od=self.draw_mark_trigger,
            extended_end_od=self.draw_mark_trigger,
            mark_interval=self.update_mark_interval,
            scroll_by=self.scroll_start_and_end,
            zoom_by=self.zoom_start_and_end,
            shift_key=self.disable_zoom,
        )

    def scroll_start_and_end(self, *_):
        dod = self.dx_to_dod(self.scroll_by)
        self.start_od -= dod
        self.end_od -= dod

    def zoom_start_and_end(self, *_):
        dod = self.dx_to_dod(self.zoom_by)
        self.start_od += dod
        self.end_od -= dod

    def on_interval_width(self, *_):
        # fixme label's don't realign until scroll/another zoom
        mark = self.ids["mark"]
        label_width = mark.max_label_width + (2 * mark.label_padding_x)
        increase_threshold = 0.5
        decrease_threshold = 0.2
        if label_width / self.interval_width >= increase_threshold:
            mark_interval = self.cdt.change_interval(self.mark_interval, self)
            self.mark_interval = mark_interval
        elif label_width / self.interval_width <= decrease_threshold:
            self.mark_interval = self.cdt.change_interval(
                self.mark_interval, self, False
            )

    def draw_mark(self, _):
        self.ids["mark"].draw_marks()

    def update_mark_interval(self, *_):
        self.ids["mark"].interval = self.mark_interval

    def on_shift_key(self, *_):
        self.disable_zoom(self.shift_key)

    def on_touches(self, *_):
        if len(self.touches) > 1:
            self.disable_drag_hor_scroll = True
        else:
            self.disable_drag_hor_scroll = False

    def disable_zoom(self, *_):
        self.disable_zoom_in = self.disable_zoom_out = self.shift_key

    #
    # Time Conversions
    #
    def od_to_x(self, od: float) -> float:
        """convert ordinal decimal to x position"""
        dod = od - self.start_od
        return self.x + self.dod_to_dx(dod)

    def dod_to_dx(self, dod: float) -> float:
        """convert change in ordinal decimal to change in pixels"""
        return self.width * (dod / self.time_span)

    def dx_to_dod(self, dx: float) -> float:
        """convert change in pixels to change in ordinal decimal"""
        return self.time_span * (dx / self.width)
