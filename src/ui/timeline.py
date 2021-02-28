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
    ReferenceListProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from src.ui.collapse import CollapseBehavior
from src.ui.focus import AbstractFocus
from src.ui.focusedkeylisten import FocusKeyListenBehavior
from src.ui.focusedhorscroll import HorScrollBehavior
from src.ui.focusedzoom import ZoomBehavior
from typing import Literal, Union


class Timeline(
    HorScrollBehavior,
    ZoomBehavior,
    FocusKeyListenBehavior,
    CollapseBehavior,
    FloatLayout,
):
    """Determines what datetimes are visible on screen"""

    mark_bar = ObjectProperty()
    collapse_bar = ObjectProperty()
    event_view = ObjectProperty()
    focusable_descendants = ReferenceListProperty(
        mark_bar, collapse_bar, event_view, rebind=True
    )

    cdt = ObjectProperty()  # ConvertibleDateTime

    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_od = NumericProperty(__now_ordinal_decimal - 365.25)  # od @ x = 0
    end_od = NumericProperty(__now_ordinal_decimal + 365.25)  # od @ x = width

    def _get_time_span(self):
        return self.end_od - self.start_od

    time_span = AliasProperty(
        _get_time_span,
        None,
        bind=["start_od", "end_od"],
    )

    primary_mark = ObjectProperty()
    secondary_mark = ObjectProperty()
    event_view_mark = ObjectProperty()
    secondary_mark_interval = ListProperty()
    too_few_marks_factor = NumericProperty(3)
    too_many_marks_factor = NumericProperty(1)

    extend_time_span_by = NumericProperty(1)

    def _get_extended_start_od(self):
        factor = self.extend_time_span_by
        return self.cdt.extend_od(
            self.start_od, self.secondary_mark_interval, factor, reverse=True
        )

    extended_start_od = AliasProperty(
        _get_extended_start_od,
        None,
        bind=["start_od", "extend_time_span_by", "secondary_mark_interval"],
    )

    def _get_extended_end_od(self):
        return self.cdt.extend_od(
            self.end_od, self.secondary_mark_interval, self.extend_time_span_by
        )

    extended_end_od = AliasProperty(
        _get_extended_end_od,
        None,
        bind=["end_od", "extend_time_span_by", "secondary_mark_interval"],
    )

    def _get_extended_time_span(self):
        return self.extended_end_od - self.extended_start_od

    extended_time_span = AliasProperty(
        _get_extended_time_span,
        None,
        bind=["extended_start_od", "extended_end_od"],
    )

    def __init__(self, **kwargs):
        self.draw_marks_trigger = Clock.create_trigger(self.draw_marks)
        super().__init__(**kwargs)
        self.bind(
            size=self.draw_marks_trigger,
            extended_start_od=self.draw_marks_trigger,
            extended_end_od=self.draw_marks_trigger,
            secondary_mark_interval=self.update_mark_interval,
            scroll_by=self.scroll_start_and_end,
            zoom_by=self.zoom_start_and_end,
            shift_key=self.disable_zoom,
            touches=self.set_drag_hor_scroll,
            focus=self.give_focus,
        )

    def on_kv_post(self, base_widget):
        self.secondary_mark.bind(interval_width=self.check_mark_spacing)
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

    def check_mark_spacing(self, *_):  # todo test bind
        interval_width = self.secondary_mark.interval_width
        max_label_width = self.secondary_mark.max_label_width
        if self.bad_mark_spacing(interval_width, self.width):
            # increase number of marks
            self.secondary_mark_interval = self.change_interval(
                self.secondary_mark_interval, self
            )
        elif self.bad_mark_spacing(
            max_label_width, interval_width, spacing="too_many",
        ):
            # decrease number of marks
            self.secondary_mark_interval = self.change_interval(
                self.secondary_mark_interval, increase=False
            )

    def change_interval(
        self, interval: list, increase=True, recursive=False,
    ) -> list:
        """change mark_interval so labels don't overlap and/or are visible"""
        frequency, unit = interval
        changed_interval = self.change_unit(interval, increase)
        if changed_interval is not None:
            return changed_interval

        # increasing the number of marks means decreasing the frequency
        sign = -1 if increase else 1
        new_frequency = frequency
        frequencies = self.cdt.get_frequencies(unit)
        if not recursive:  # change_unit() has already changed the frequency
            idx = frequencies.index(frequency)
            new_idx = idx + sign
            new_frequency = frequencies[new_idx]

        start_od = self.start_od
        start_x = self.od_to_x(start_od)
        assert start_x == 0, f"start_od should be at x = 0, it's {start_x}"

        new_od = self.cdt.extend_od(start_od, [new_frequency, unit])
        new_interval_width = self.od_to_x(new_od)  # an approximation

        max_label_width = self.secondary_mark.max_label_width
        while (
            self.bad_mark_spacing(
                max_label_width, new_interval_width, spacing="too_many"
            )
            or self.bad_mark_spacing(new_interval_width, self.width)
        ):
            interval = [new_frequency, unit]
            interval = self.change_unit(interval, increase)
            if interval is not None:
                return interval

            idx = frequencies.index(new_frequency)
            new_idx = idx + sign
            new_frequency = frequencies[new_idx]
            new_od = self.cdt.extend_od(start_od, [new_frequency, unit])
            new_interval_width = self.od_to_x(new_od)

            increase = self.bad_mark_spacing(new_interval_width, self.width)
        return [new_frequency, unit]

    def change_unit(self, interval: list, increase=True) -> Union[list, None]:
        """
        Change the unit of an interval. Assumes self.cdt.datetime_units is
        sorted largest to smallest

        :raises ValueError: when increasing a Year unit or decreasing a second
            unit.
        """
        frequency, unit = interval
        frequencies = self.cdt.get_frequencies(unit)
        decrease_unit = increase and frequency == min(frequencies)
        increase_unit = not increase and frequency == max(frequencies)

        if increase_unit:
            if self.cdt.is_datetime_unit(unit, "era"):
                raise ValueError("Interval unit can't be more than a year")

            unit_idx = self.cdt.datetime_units.index(unit)
            bigger_unit = self.cdt.datetime_units[unit_idx - 1]
            frequency = min(self.cdt.get_frequencies(bigger_unit))
            interval = [frequency, bigger_unit]
            return self.change_interval(interval, increase, recursive=True)
        elif decrease_unit:
            if self.cdt.is_datetime_unit(unit, "second"):
                raise ValueError("Interval unit can't be less than a second")

            unit_idx = self.cdt.datetime_units.index(unit)
            smaller_unit = self.cdt.datetime_units[unit_idx + 1]
            frequency = max(self.cdt.get_frequencies(smaller_unit))
            interval = [frequency, smaller_unit]
            return self.change_interval(interval, increase, recursive=True)

    def bad_mark_spacing(
        self,
        max_width: float,
        current_width: float,
        spacing: Literal["too_few", "too_many"] = "too_few",
    ) -> bool:
        factor = self.too_few_marks_factor
        if spacing == "too_many":
            factor = self.too_many_marks_factor
        return max_width * factor > current_width

    def draw_marks(self, _):
        self.primary_mark.draw_marks()
        secondary_mark_ods = self.secondary_mark.draw_marks()
        self.event_view_mark.draw_marks(mark_ods=secondary_mark_ods)

    def update_mark_interval(self, *_):
        self.secondary_mark.interval = self.secondary_mark_interval
        self.event_view_mark.interval = self.secondary_mark_interval

        unit = self.secondary_mark_interval[1]
        self.primary_mark.interval = self.cdt.get_primary_interval(unit)

    def disable_zoom(self, *_):
        self.disable_zoom_in = self.disable_zoom_out = self.shift_key

    def set_drag_hor_scroll(self, *_):
        if len(self.touches) > 1:
            self.disable_drag_hor_scroll = True
        else:
            self.disable_drag_hor_scroll = False

    def gain_focus(self, *_):
        """don't gain focus if any focusable descendants have focus"""
        if not self.descendant_focused():
            super().gain_focus()

    def descendant_focused(self) -> bool:
        for focusable_widget in self.focusable_descendants:
            if focusable_widget and focusable_widget.focus:
                return True
        return False

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


class TimelineScrollView(ScrollView):
    """Viewport for all the timelines"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(children=self.bind_child)

    def bind_child(self, *_):
        child = self.children[0]
        child.bind(height=self.set_do_scroll_y, timelines=self.set_do_scroll_y)
        child.bind(timelines=self.bind_child_timelines)

    def bind_child_timelines(self, *_):
        """listen to the focus of all Timelines and their focusable children"""

        child = self.children[0]
        for timeline in child.timelines:
            timeline.bind(focus=self.set_do_scroll_y)
            timeline.bind(focus=self.scroll_to_focused_widget)

            for focusable_widget in timeline.focusable_descendants:
                try:
                    focusable_widget.bind(focus=self.set_do_scroll_y)
                    focusable_widget.bind(focus=self.scroll_to_focused_widget)
                except AttributeError:
                    pass

    def set_do_scroll_y(self, *_):
        """disable scroll when a Timeline or its child has focus"""

        child = self.children[0]
        timeline_has_focus = False
        for timeline in child.timelines:
            if timeline.focus:
                timeline_has_focus = True
                break

            if timeline.descendant_focused():
                timeline_has_focus = True
                break

        if child.height <= self.height or timeline_has_focus:
            self.do_scroll_y = False
        else:
            self.do_scroll_y = True

    def scroll_to_focused_widget(self, widget, value):
        if value:
            self.scroll_to(widget)


class TimelineLayout(FloatLayout):
    """Manages Timeline sizes. Should be the child of TimelineScrollView"""

    timelines = ListProperty([])

    def add_widget(self, widget, index=0, canvas=None):
        super().add_widget(widget, index=index, canvas=canvas)
        if isinstance(widget, Timeline):
            self.timelines.insert(index, widget)
            widget.bind(height=self.resize_timelines)

    def remove_widget(self, widget):
        super().remove_widget(widget)
        if widget in self.timelines:
            self.timelines.remove(widget)

    def on_kv_post(self, base_widget):
        self.parent.bind(height=self.resize_timelines)

    def on_timelines(self, *_):
        Clock.schedule_once(self.resize_timelines, -1)

    def resize_timelines(self, *_):
        self.set_collapsable_timelines()

        top_tl = self.top_timeline
        if len(self.timelines) == 1:
            # only one timeline, set it to full available height
            self.set_height()
            top_tl.expanded_height = self.parent.height
            top_tl.expanded_y = self.parent.y
            return

        self.set_height()
        self.set_timeline_listeners()

        top_tl.expanded_height = self.default_timeline_height
        top_tl.expanded_y = self.top - top_tl.expanded_height
        top_tl_index = self.timelines.index(top_tl)
        for idx, timeline in reversed(list(enumerate(self.timelines))):
            if idx == top_tl_index:
                continue

            above_tl = self.above_timeline(timeline)
            timeline.expanded_height = self.default_timeline_height
            timeline.expanded_y = above_tl.y - timeline.expanded_height

    def set_height(self, *_):
        height = 0.0
        for timeline in self.timelines:
            if timeline.collapsed:
                height += timeline.collapsed_height
            else:
                height += self.default_timeline_height
        self.height = max(height, self.parent.height)

    def set_collapsable_timelines(self):
        num_expanded = len([tl for tl in self.timelines if not tl.collapsed])
        allow_collapse = num_expanded > 2
        for tl in self.timelines:
            if not tl.collapsed:
                tl.collapsable = allow_collapse

    def set_timeline_listeners(self):
        for tl in self.timelines:
            if tl != self.top_timeline:
                # let kv file set previous active listener for top timeline
                tl.previous_active_listener = self.above_timeline(tl)
            tl.next_active_listener = self.below_timeline(tl)

    def below_timeline(self, timeline: Timeline) -> Union[Timeline, None]:
        below_idx = self.timelines.index(timeline) - 1
        if below_idx < 0:
            return None
        return self.timelines[below_idx]

    def above_timeline(self, timeline: Timeline) -> Union[Timeline, None]:
        above_idx = self.timelines.index(timeline) + 1
        try:
            return self.timelines[above_idx]
        except IndexError:
            return None

    @property
    def top_timeline(self) -> Timeline:
        return self.timelines[-1]

    @property
    def default_timeline_height(self) -> float:
        """the default height when there is more than 1 timeline"""
        return self.parent.height / 2


class TimelineScreen(AbstractFocus, Screen):
    """Where one or more timelines are displayed"""

    timeline_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(focus=self.give_focus)
