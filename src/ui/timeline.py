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
from typing import Union


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
    start_od = NumericProperty(__now_ordinal_decimal - 730.5)  # od @ x = 0
    end_od = NumericProperty(__now_ordinal_decimal + 730.5)  # od @ x = width

    def _get_time_span(self):
        return self.end_od - self.start_od

    time_span = AliasProperty(
        _get_time_span,
        None,
        bind=["start_od", "end_od"],
    )

    mark = ObjectProperty()
    mark_interval = ListProperty()
    event_view_mark = ObjectProperty()

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
            touches=self.set_drag_hor_scroll,
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

    def change_mark_interval(self, mark, *_):
        """
        Ensure label width doesn't overlap on zoom out.
        Ensure there are at least 2 visible marks when zooming in.
        """
        if self.mark.interval_width * 3 > self.width:
            # increase number of marks
            self.mark_interval = self.cdt.change_interval(
                self.mark_interval, self, mark
            )
        elif self.mark.max_label_width > self.mark.interval_width:
            # decrease number of marks
            self.mark_interval = self.cdt.change_interval(
                self.mark_interval, self, mark, increase=False
            )

    def draw_mark(self, _):
        secondary_mark_ods = self.mark.draw_marks()
        self.event_view_mark.draw_marks(mark_ods=secondary_mark_ods)

    def update_mark_interval(self, *_):
        self.mark.interval = self.mark_interval

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
