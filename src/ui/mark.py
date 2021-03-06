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
import numpy

from kivy.graphics import Color, Rectangle
from kivy.metrics import sp
from kivy.properties import (
    BooleanProperty,
    BoundedNumericProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.widget import Widget
from src.ui.textboundlabel import TextBoundLabel


class Mark(Widget):
    """Marks specific point in time. Should be a child of a BaseTimeline"""

    timeline = ObjectProperty()

    LABEL_LEFT = "left"
    LABEL_CENTER = "center"
    LABEL_MID_INTERVAL = "mid_interval"
    LABEL_RIGHT = "right"
    # fmt: off
    _label_alignments = [
        LABEL_LEFT, LABEL_CENTER, LABEL_MID_INTERVAL, LABEL_RIGHT
    ]
    # fmt: on
    label_align = OptionProperty(LABEL_LEFT, options=_label_alignments)
    label_padding_x = NumericProperty("2sp")
    label_padding_y = NumericProperty("2sp")
    label_y = NumericProperty(None, allownone=True)
    font_size = BoundedNumericProperty(sp(12), min=sp(12))
    has_label = BooleanProperty(True)
    max_label_width = NumericProperty()

    mark = ObjectProperty(Rectangle)
    mark_y = NumericProperty()
    mark_width = NumericProperty("2sp")
    mark_height = NumericProperty("100sp")
    mark_color = ObjectProperty(Color([250 / 255] * 3))

    interval = ListProperty()
    interval_width = NumericProperty(allownone=True)
    force_visible = BooleanProperty(False)

    def draw_marks(self, *_, mark_ods: list = None) -> list:
        """:raises AssertionError: when 2 marks should be visible but aren't"""

        def make_mark_x() -> tuple[float, list, list]:
            """:return: current mark x, all mark x's, all visible mark x's"""

            x = self.timeline.od_to_x(mark_od)
            mark_xs.append(x)
            if self.timeline.x <= x <= self.timeline.right:
                visible_mark_xs.append(x)
            return x, mark_xs, visible_mark_xs

        def add_mark_to_canvas():
            pos = sp(mark_x), sp(self.mark_y)
            size = sp(self.mark_width), sp(self.mark_height)
            self.canvas.add(self.mark(pos=pos, size=size))

        def add_label_to_canvas(alignment=None, location: str = None):
            alignment = alignment or self.label_align
            hr_date = tl.cdt.od_to_hr_date(mark_od, unit)
            label = self.make_label(mark_x, hr_date, alignment)

            if (
                location == "left"
                and label.right >= mid_mark_x - self.label_padding_x
            ):
                label.right = mid_mark_x - self.label_padding_x
            elif (
                location == "right"
                and label.x
                <= mid_mark_x + self.mark_width + self.label_padding_x
            ):
                label.x = mid_mark_x + self.mark_width + self.label_padding_x

            self.canvas.add(
                Rectangle(
                    pos=label.pos,
                    size=label.texture_size,
                    texture=label.texture,
                )
            )

        self.canvas.clear()
        self.canvas.add(self.mark_color)

        mark_xs = []
        visible_mark_xs = []
        tl = self.timeline

        unit = self.interval[1]
        if mark_ods:  # skip expensive ordinal calculations if we can
            for mark_od in mark_ods:
                mark_x, mark_xs, visible_mark_xs = make_mark_x()
        elif tl.cdt.is_datetime_unit(unit, "era"):
            mark_ods = tl.cdt.era_start_ordinals
        else:
            # extend_od() widens time span without considering the interval
            # so the first mark_od needs to be set with next_od()
            mark_od = tl.cdt.next_od(
                tl.extended_start_od, self.interval, forward=False
            )
            mark_ods = [mark_od]
            while mark_od <= tl.extended_end_od:
                mark_x, mark_xs, visible_mark_xs = make_mark_x()

                mark_od = tl.cdt.next_od(mark_od, self.interval)
                mark_ods.append(mark_od)

        # interval_width is only valid if there are at least two visible marks
        force_visible = self.force_visible
        interval_width = float(numpy.diff(visible_mark_xs).mean())
        if numpy.isnan(interval_width):
            if not force_visible:
                raise RuntimeError("Must be at least 2 visible marks")
            self.interval_width = None
        else:
            self.interval_width = interval_width

        if force_visible and self.interval_width is None and self.has_label:
            # force labels to be visible if there are less than 2 visible marks
            off_screen_mark_od = tl.cdt.next_od(
                tl.start_od, self.interval, forward=False
            )
            off_screen_mark_x = tl.od_to_x(off_screen_mark_od)
            mid_mark_od = tl.cdt.next_od(tl.start_od, self.interval)
            mid_mark_x = tl.od_to_x(mid_mark_od)  # may still be off screen

            mark_ods = [off_screen_mark_od, mid_mark_od]
            mark_xs = [off_screen_mark_x, mid_mark_x]

            for idx, mark_x in enumerate(mark_xs):  # the marks without labels
                mark_od = mark_ods[idx]
                add_mark_to_canvas()

            marks_drawn = True
            mark_ods = [tl.start_od, tl.end_od]
            mark_xs = [tl.x, tl.right]  # really should be called label pos
            alignments = [self.LABEL_LEFT, self.LABEL_RIGHT]
            pin_locations = "left", "right"
        else:
            marks_drawn = False
            alignments = None
            pin_locations = None

        for idx, mark_x in enumerate(mark_xs):
            mark_od = mark_ods[idx]

            if not marks_drawn:
                add_mark_to_canvas()

            if not self.has_label:
                continue

            try:
                label_align = alignments[idx]
                pin_location = pin_locations[idx]
            except TypeError:
                add_label_to_canvas()
            else:
                add_label_to_canvas(label_align, pin_location)
        return mark_ods

    def make_label(self, x: int, text: str, alignment: str) -> TextBoundLabel:
        """:raises: ValueError if alignment is isn't a valid option"""

        if alignment not in self._label_alignments:
            raise ValueError(f"{alignment} is not in a valid label alignment")

        label = TextBoundLabel(text=text, font_size=self.font_size)
        label.texture_update()
        if label.width > self.max_label_width:
            self.max_label_width = label.width + (2 * self.label_padding_x)

        if alignment == self.LABEL_LEFT:
            label.x = sp(x + self.label_padding_x)
        elif alignment == self.LABEL_CENTER:
            label.center_x = sp(x)
        elif alignment == self.LABEL_MID_INTERVAL:
            label.center_x = sp(x + (self.interval_width / 2))
        else:  # right alignment
            label.right = x - self.label_padding_x

        if self.label_y is None:
            label.top = self.top - self.label_padding_y
        else:
            label.y = self.label_y

        return label
