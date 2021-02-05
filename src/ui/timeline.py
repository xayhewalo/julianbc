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
from kivy.uix.floatlayout import FloatLayout
from src.ui.focusedkeylisten import FocusKeyListenBehavior
from src.ui.focusedhorscroll import HorScrollBehavior
from src.ui.focusedzoom import ZoomBehavior


class Timeline(
    HorScrollBehavior,
    ZoomBehavior,
    FocusKeyListenBehavior,
    FloatLayout,
):
    """Where the end-user adds events"""

    cdt = ObjectProperty()

    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_od = NumericProperty(__now_ordinal_decimal - 60)  # od @ x = 0
    end_od = NumericProperty(__now_ordinal_decimal + 60)  # od @ x = self.width

    def _get_time_span(self):
        return self.end_od - self.start_od

    time_span = AliasProperty(
        _get_time_span,
        None,
        bind=["start_od", "end_od"],
    )

    mark = ObjectProperty()
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
        bind=["start_od", "extend_time_span_by", "mark_interval"],
    )

    def _get_extended_end_od(self):
        return self.cdt.extend_od(
            self.end_od, self.mark_interval, self.extend_time_span_by
        )

    extended_end_od = AliasProperty(
        _get_extended_end_od,
        None,
        bind=["end_od", "extend_time_span_by", "mark_interval"],
    )

    def _get_extended_time_span(self):
        return self.extended_end_od - self.extended_start_od

    extended_time_span = AliasProperty(
        _get_extended_time_span,
        None,
        bind=["extended_start_od", "extended_end_od"],
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
            focus=self.give_focus,
        )

    def on_kv_post(self, base_widget):
        self.mark.bind(interval_width=self.change_mark_interval)
        return super().on_kv_post(base_widget)

    def scroll_start_and_end(self, *_):
        if self.scroll_by == 0:  # for performance
            return
        dod = self.dx_to_dod(self.scroll_by)
        self.start_od -= dod
        self.end_od -= dod

    def zoom_start_and_end(self, *_):
        if self.zoom_by == 0:  # for performance
            return
        dod = self.dx_to_dod(self.zoom_by)
        self.start_od += dod
        self.end_od -= dod

    def change_mark_interval(self, *_):
        """
        Ensure label width doesn't overlap on zoom out.
        Ensure there are at least 2 visible marks when zooming in.
        """
        if self.mark.interval_width * 3 > self.width:
            # increase number of marks
            mark_interval = self.cdt.change_interval(self.mark_interval, self)
            self.mark_interval = mark_interval
        elif self.mark.max_label_width > self.mark.interval_width:
            # decrease number of marks
            self.mark_interval = self.cdt.change_interval(
                self.mark_interval, self, False
            )

    def draw_mark(self, _):
        self.mark.draw_marks()

    def update_mark_interval(self, *_):
        self.mark.interval = self.mark_interval

    def disable_zoom(self, *_):
        self.disable_zoom_in = self.disable_zoom_out = self.shift_key

    def on_touches(self, *_):
        if len(self.touches) > 1:
            self.disable_drag_hor_scroll = True
        else:
            self.disable_drag_hor_scroll = False

    def give_focus(self, *_):
        if self.focus:
            self.set_focus_next()

    def on_touch_down(self, touch):
        if touch.button.startswith("scroll"):
            self.focus_next = self.ids["event_view"]
        return super().on_touch_down(touch)

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
