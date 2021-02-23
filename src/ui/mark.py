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

from kivy.clock import Clock
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
    _label_alignments = [LABEL_LEFT, LABEL_CENTER, LABEL_MID_INTERVAL]
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
    interval_width = NumericProperty()
    calculate_interval_width = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.draw_marks_trigger = Clock.create_trigger(self.draw_marks)
        super().__init__(**kwargs)
        self.bind(pos=self.draw_marks_trigger, size=self.draw_marks_trigger)

    def draw_marks(self, *_, mark_ods: list = None) -> list:
        """:raises AssertionError: if less than two visible marks drawn"""

        def make_mark_x() -> tuple[float, list]:
            """:return: current mark x, all mark x's, all visible mark x's"""

            x = self.timeline.od_to_x(mark_od)
            mark_xs.append(x)
            return x, mark_xs

        self.canvas.clear()
        self.canvas.add(self.mark_color)

        mark_xs = []
        tl = self.timeline
        if mark_ods:  # skip expensive ordinal calculations if we can
            for mark_od in mark_ods:
                mark_x, mark_xs = make_mark_x()
        else:
            mark_od = tl.extended_start_od
            mark_ods = [mark_od]
            while mark_od <= tl.extended_end_od:
                mark_x, mark_xs = make_mark_x()

                mark_od = tl.cdt.next_od(mark_od, self.interval)
                mark_ods.append(mark_od)

        if self.calculate_interval_width:
            # don't use first and last mark for interval_width
            usable_mark_xs = mark_xs[1:-1]
            assert len(usable_mark_xs) >= 2, "must be at least 2 usable marks"
            self.interval_width = float(numpy.diff(usable_mark_xs).mean())

        for idx, mark_x in enumerate(mark_xs):
            unit = self.interval[1]
            mark_od = mark_ods[idx]

            pos = sp(mark_x), sp(self.mark_y)
            size = sp(self.mark_width), sp(self.mark_height)
            self.canvas.add(self.mark(pos=pos, size=size))

            if not self.has_label:
                continue
            hr_date = tl.cdt.od_to_hr_date(mark_od, unit)
            label = self.make_label(mark_x, hr_date, self.label_align)
            self.canvas.add(
                Rectangle(
                    pos=label.pos,
                    size=label.texture_size,
                    texture=label.texture,
                )
            )
        return mark_ods

    def make_label(self, x: int, text: str, alignment: str, force_visible=False) -> TextBoundLabel:
        """:raises: ValueError if alignment is isn't a valid option"""

        if alignment not in self._label_alignments:
            raise ValueError(f"{alignment} is not in a valid label alignment")

        label = TextBoundLabel(text=text, font_size=self.font_size)
        label.texture_update()
        if label.width > self.max_label_width:
            self.max_label_width = label.width + (2 * self.label_padding_x)

        if force_visible:
            self.set_visible_label_x(x, label)
        else:
            self.set_label_x(x, alignment, label)

        if self.label_y is None:
            label.top = self.top - self.label_padding_y
        else:
            label.y = self.label_y

        return label

    def set_label_x(self, x: float, alignment: str, label: TextBoundLabel):
        if alignment == self.LABEL_LEFT:
            label.x = sp(x + self.label_padding_x)
        elif alignment == self.LABEL_CENTER:
            label.center_x = sp(x)
        else:  # middle interval alignment
            label.center_x = sp(x + (self.interval_width / 2))

    def set_visible_label_x(self, x: float, label: TextBoundLabel):
        raise NotImplementedError
