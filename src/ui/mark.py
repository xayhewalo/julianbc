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
from .textboundlabel import TextBoundLabel
from .utils import ON_BACKGROUND_COLOR
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp
from kivy.properties import (
    BoundedNumericProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.widget import Widget


class Mark(Widget):
    """Marks specific point in time. Should be a child of a BaseTimeline"""

    LABEL_LEFT = "left"
    LABEL_CENTER = "center"
    _label_alignments = [LABEL_LEFT, LABEL_CENTER]
    label_align = OptionProperty(LABEL_LEFT, options=_label_alignments)
    label_padding_x = NumericProperty("2sp")
    label_padding_y = NumericProperty("2sp")
    label_y = NumericProperty(0)
    font_size = BoundedNumericProperty(sp(10), min=sp(10))
    max_label_width = NumericProperty(0)

    mark = ObjectProperty(Rectangle)
    mark_y = NumericProperty(0)
    mark_width = NumericProperty("2sp")
    mark_height = NumericProperty("800sp")
    mark_color = ObjectProperty(defaultvalue=Color(*ON_BACKGROUND_COLOR))

    interval = ListProperty(list())
    interval_width = NumericProperty(0)

    def __init__(self, **kwargs):
        self.draw_marks_trigger = Clock.create_trigger(self.draw_marks)
        super(Mark, self).__init__(**kwargs)
        self.bind(interval=self.draw_marks_trigger)

    def draw_marks(self, *_) -> None:
        self.canvas.clear()
        self.canvas.add(self.mark_color)

        parent = self.parent
        dt = parent.cdt  # ConvertibleDateTime
        frequency, dateunit = self.interval
        backwards_interval = -frequency * 2, dateunit

        start_ordinal = int(parent.start_ordinal_decimal)
        old_start_ordinal = start_ordinal
        start_ymd = dt.od_to_ast_ymd(start_ordinal)
        start_ymd = dt.date.shift_ast_ymd(start_ymd, [backwards_interval])
        start_ordinal = int(dt.ast_ymd_to_od(start_ymd))
        end_ordinal = int(parent.end_ordinal_decimal)
        end_ymd = dt.od_to_ast_ymd(end_ordinal)
        end_ymd = dt.date.shift_ast_ymd(end_ymd, [self.interval])
        end_ordinal = int(dt.ast_ymd_to_od(end_ymd))

        self.interval_width = (
            (
                parent.od_to_x(old_start_ordinal)
                - parent.od_to_x(start_ordinal)
            ) / 3
        )

        mark_od = start_ordinal
        while mark_od <= end_ordinal:
            x = parent.od_to_x(mark_od)
            hr_date = parent.cdt.od_to_hr_date(mark_od, dateunit)
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

            ast_ymd = dt.od_to_ast_ymd(mark_od)
            ast_ymd = dt.date.next_ast_ymd(ast_ymd, self.interval)
            mark_od = dt.ast_ymd_to_od(ast_ymd)

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
        else:  # center alignment
            label_x = sp(x - int(label.width / 2) + self.label_padding_x)

        label_y = self.label_y or sp(
            self.top - self.font_size - self.label_padding_y
        )
        label.pos = label_x, label_y
        return label

    #
    # Disable Touch
    #
    def on_touch_down(self, touch):
        return False

    def on_touch_move(self, touch):
        return False

    def on_touch_up(self, touch):
        return False
