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
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp
from kivy.properties import (
    BoundedNumericProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.widget import Widget
from src.ui.textboundlabel import TextBoundLabel


class Mark(Widget):
    """Marks specific point in time. Should be a child of a BaseTimeline"""

    LABEL_LEFT = "left"
    LABEL_CENTER = "center"
    LABEL_MID_INTERVAL = "mid_interval"
    _label_alignments = [LABEL_LEFT, LABEL_CENTER, LABEL_MID_INTERVAL]
    label_align = OptionProperty(LABEL_LEFT, options=_label_alignments)
    label_padding_x = NumericProperty("2sp")
    label_padding_y = NumericProperty("2sp")
    label_y = NumericProperty()
    font_size = BoundedNumericProperty(sp(12), min=sp(12))
    max_label_width = NumericProperty()

    mark = ObjectProperty(Rectangle)
    mark_y = NumericProperty()
    mark_width = NumericProperty("2sp")
    mark_height = NumericProperty("100sp")
    mark_color = ObjectProperty(Color([250 / 255] * 3))

    def __init__(self, **kwargs):
        self.draw_marks_trigger = Clock.create_trigger(self.draw_marks)
        super().__init__(**kwargs)
        self.bind(pos=self.draw_marks_trigger, size=self.draw_marks_trigger)

    def draw_marks(self, *_, mark_ods=None) -> list:
        def draw_and_increment(mark_od_: float) -> float:
            parent = self.parent
            x = parent.od_to_x(mark_od_)
            unit = parent.mark_interval[1]
            hr_date = parent.cdt.od_to_hr_date(mark_od_, unit)
            label = self.make_label(x, hr_date, self.label_align)
            pos = sp(x), sp(self.mark_y)
            size = sp(self.mark_width), sp(self.mark_height)
            self.canvas.add(self.mark(pos=pos, size=size))
            self.canvas.add(
                Rectangle(
                    pos=label.pos,
                    size=label.texture_size,
                    texture=label.texture,
                )
            )

            mark_od_ = parent.cdt.next_od(mark_od_, parent.mark_interval)
            return mark_od_

        self.canvas.clear()
        self.canvas.add(self.mark_color)

        if mark_ods:
            for mark_od in mark_ods:
                draw_and_increment(mark_od)
        else:
            mark_od = self.parent.extended_start_od
            mark_ods = [mark_od]
            while mark_od <= self.parent.extended_end_od:
                mark_od = draw_and_increment(mark_od)
                mark_ods.append(mark_od)
        return mark_ods

    def make_label(self, x: int, text: str, alignment: str) -> TextBoundLabel:
        """:raises: ValueError if alignment is isn't a valid option"""

        if alignment not in self._label_alignments:
            raise ValueError(f"{alignment} is not in a valid label alignment")

        label = TextBoundLabel(text=text, font_size=self.font_size)
        label.texture_update()
        if label.width > self.max_label_width:
            self.max_label_width = label.width

        if alignment == self.LABEL_LEFT:
            label_x = sp(x + self.label_padding_x)
        elif alignment == self.LABEL_CENTER:
            label_x = sp(x - int(label.width / 2) + self.label_padding_x)
        else:  # middle interval alignment
            # todo just set center x?
            half_interval_width = self.parent.interval_width / 2
            half_label_width = label.width / 2
            padding = self.label_padding_x
            label_x = sp(x + half_interval_width - half_label_width + padding)

        label_y = self.label_y or sp(
            self.top - self.font_size - self.label_padding_y
        )
        label.pos = label_x, label_y
        return label
