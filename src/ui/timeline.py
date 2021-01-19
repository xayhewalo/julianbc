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
import datetime

from .horizontalscroll import HorScrollBehavior
from .mark import Mark
# noinspection PyUnresolvedReferences
from .showhidebar import ShowHideBar  # so it's available for in kv lang
from .utils import ON_SURFACE_COLOR
from .zoom import ZoomBehavior
from src.customdatetime import DateUnits, TimeUnits
from src.eventcontroller import EventController
from src.setup_db import gregorian_datetime
from typing import Iterator, Union
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, InstructionGroup, Line
from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen

Builder.load_string("""
#:import utils src.ui.utils

<CollapsableTimeline>:
    ComboTimeline:
        id: combo_timeline
        size_hint: 1, 0.97
        y: show_hide_bar.y - self.height - sp(10)
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
            pos: self.parent.pos

    ShowHideBar:
        id: show_hide_bar
        size_hint: 1, 0.03
        pos_hint: {"top": 1}
        text: combo_timeline.cdt.date.calendar.name
        dependant: combo_timeline

<TimelineScreen>:
    name: "timeline_screen"

    CollapsableTimeline:
        id: ct1
        size_hint: 1, 0.5
        pos_hint: {"top": 1}

    CollapsableTimeline:
        id: ct2
        size_hint: 1, 0.5
        pos_hint: {"top": 0.5}
""")


class TimelineScreen(Screen):
    """Where Timelines are"""


# todo just do collapse with combo timeline
class CollapsableTimeline(FloatLayout):  # todo probs should be relative layout
    """Expands and collapses a ComboTimeline"""  # todo should this be called a timeline?
    # todo de-focus dependant when collapsed


class BaseTimeline(HorScrollBehavior, ZoomBehavior, FloatLayout):
    """Abstract class for timelines"""

    cdt = ObjectProperty(gregorian_datetime)
    __now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    __midnight_today = __now.replace(hour=0, minute=0, second=0, microsecond=0)
    __seconds_into_day = (__now - __midnight_today).seconds
    __now_ordinal_decimal = __now.toordinal() + (__seconds_into_day / 86400)
    start_ordinal_decimal = NumericProperty(__now_ordinal_decimal - 1)
    end_ordinal_decimal = NumericProperty(__now_ordinal_decimal + 1)

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
        app = App.get_running_app()
        if app.sync_timelines is True:
            for collapsable_timeline in app.timeline_screen.children:
                # fixme ugly
                if collapsable_timeline.children[1] is not self:
                    collapsable_timeline.children[1].scroll_by = self.scroll_by

    def scroll_siblings(self) -> None:
        for sibling in self.gen_timeline_siblings():
            sibling.scroll_by = self.scroll_by

    def on_zoom_by(self, *_) -> None:
        dod = self.dx_to_dod(self.zoom_by)
        self.start_ordinal_decimal += dod
        self.end_ordinal_decimal -= dod
        self.zoom_siblings()
        app = App.get_running_app()
        if app.sync_timelines is True:
            for collapsable_timeline in app.timeline_screen.children:
                # fixme ugly
                if collapsable_timeline.children[1] is not self:
                    # todo probs should change the ComboTimeline have it modifiy it's children, instead of siblings changing each other
                    collapsable_timeline.children[1].children[1].zoom_by = self.zoom_by  # mark timeline
                    collapsable_timeline.children[1].children[0].zoom_by = self.zoom_by
                    # collapsable_timeline.children[1].children[1].change_interval()  # mark timeline

    def zoom_siblings(self) -> None:
        for sibling in self.gen_timeline_siblings():
            sibling.zoom_by = self.zoom_by

    def gen_timeline_siblings(self) -> Iterator["BaseTimeline"]:
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

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.hor_scrolling:
            app = App.get_running_app()
            app.show_calendar_changer()
            return True
        return super(MarkedTimeline, self).on_touch_up(touch)

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

    min_event_height = NumericProperty("20sp")
    min_event_width = NumericProperty("100sp")
    event_y = NumericProperty(0)
    visible_event_params = ListProperty(defaultvalue=list())  # *pos, *size
    event_instr_group = ObjectProperty(InstructionGroup())
    event_instr = ObjectProperty(Line)  # event graphical instruction

    def __init__(self, **kwargs):
        self.draw_event_graphics_trigger = Clock.create_trigger(
            self.draw_event_graphics
        )
        super(BareTimeline, self).__init__(**kwargs)
        self.ec = EventController(cdt=self.cdt)
        self.event_instr_group.add(Color(*ON_SURFACE_COLOR))
        self.bind(
            time_span=self.draw_event_graphics_trigger,
            height=self.update_event_y,
            y=self.update_event_y,
            event_y=self.draw_event_graphics_trigger,
            cdt=self.update_ec,
        )

    def on_touch_down(self, touch):  # todo double click should open event manager
        if touch.is_double_tap and self.collide_point(*touch.pos):
            """pos = touch.x, self.event_y
            self.draw_event(pos)"""
            app = App.get_running_app()
            start = self.x_to_od(touch.x)
            app.show_event_editor(start_od=start)
            return True
        return super(BareTimeline, self).on_touch_down(touch)

    def draw_event_graphics(self, *_) -> None:  # todo make an EventContainer class like Mark?
        self.canvas.remove(self.event_instr_group)
        self.visible_event_params.clear()

        start_od, end_od = self.start_ordinal_decimal, self.end_ordinal_decimal
        visible_events = self.ec.get_events(start_od, end_od)
        prev_event = None
        prev_x = prev_right = float("inf")
        graphics = InstructionGroup()
        for event_idx, event in enumerate(visible_events):
            # fixme UI is interacting directly with the db here
            prev_idx = event_idx - 1
            if prev_event:
                prev_event = visible_events[prev_idx]
                prev_x = self.od_to_x(prev_event.start)
                prev_right = max(self.od_to_x(prev_event.end), prev_x + self.min_event_width)

            x = self.od_to_x(event.start)
            right = self.od_to_x(event.end)
            width = max(self.dod_to_dx(event.duration), self.min_event_width)

            if prev_x <= x <= prev_right:  # fixme if two events ago is really long, collisions occur
                y = self.visible_event_params[prev_idx]["pos"][1] - self.min_event_height
            else:
                y = self.event_y

            prev_event = copy.deepcopy(event)
            prev_x = x
            prev_right = right

            pos = x, y

            # todo change event height
            # event_params = [*pos, width, self.min_event_height]
            event_params = {"pos": pos, "size": [width, self.min_event_height]}
            graphics.add(
                self.event_instr(
                    rounded_rectangle=[*pos, width, self.min_event_height, 2]
                )
            )
            self.visible_event_params.append(event_params)
        self.event_instr_group = graphics
        self.canvas.add(self.event_instr_group)

    """def draw_event(
        self, pos: tuple[float, float], duration: float = None, *_
    ) -> None:
        x, _ = pos
        start_od = self.x_to_od(x)
        duration = duration or 1 / self.cdt.time.clock.seconds_in_day
        width = self.dod_to_dx(duration)
        self.event_instr_group.add(
            self.event_instr(
                rounded_rectangle=[*pos, width, self.min_event_height, 2]
            )
        )
        self.canvas.add(self.event_instr_group)

        self.ec.make({"start": start_od, "duration": duration})"""

    def x_to_od(self, x: float) -> float:
        """convert x position to ordinal decimal"""
        dx = x - self.x
        return self.start_ordinal_decimal + self.dx_to_dod(dx)

    def update_event_y(self, *_) -> None:
        self.event_y = self.y + self.height - self.min_event_height

    def update_ec(self, *_) -> None:
        self.ec = EventController(cdt=self.cdt)


class ComboTimeline(BaseTimeline):
    """Combination of a MarkedTimeline and BareTimeline"""

    def __init__(self, **kwargs):
        super(ComboTimeline, self).__init__(**kwargs)
        self.bind(
            start_ordinal_decimal=self.update_ordinal_decimals,
            end_ordinal_decimal=self.update_ordinal_decimals,
            cdt=self.update_convertible_datetimes,
            height=self.update_mark_height,
            y=self.update_mark_y,
        )

    def update_ordinal_decimals(self, *_) -> None:
        for child_tl in self.gen_child_timelines():
            child_tl.start_ordinal_decimal = self.start_ordinal_decimal
            child_tl.end_ordinal_decimal = self.end_ordinal_decimal

    def update_convertible_datetimes(self, *_) -> None:
        for child_tl in self.gen_child_timelines():
            child_tl.cdt = self.cdt

    def update_mark_height(self, *_) -> None:
        # noinspection PyTypeChecker
        for marked_tl in self.gen_child_timelines(child_cls=MarkedTimeline):
            marked_tl.mark.mark_height = self.height

    def update_mark_y(self, *_) -> None:
        # noinspection PyTypeChecker
        for marked_tl in self.gen_child_timelines(child_cls=MarkedTimeline):
            marked_tl.mark.mark_y = self.y

    def gen_child_timelines(
        self, child_cls: Union[BaseTimeline, MarkedTimeline] = BaseTimeline
    ) -> Iterator[Union[BaseTimeline, MarkedTimeline]]:
        for child in self.children:
            if isinstance(child, child_cls):
                yield child
