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
#  along with JulianBC.  If not, see <https://www.gnu.org/licenses/>
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
    """Marks specific moment in time. Should be a child of a BaseTimeline"""

    LABEL_LEFT = "left"
    LABEL_CENTER = "center"
    _label_alignments = [LABEL_LEFT, LABEL_CENTER]
    label_align = OptionProperty(LABEL_LEFT, options=_label_alignments)
    label_padding_x = NumericProperty("2sp")
    label_padding_y = NumericProperty("2sp")
    label_y = NumericProperty(0)

    mark = ObjectProperty(Rectangle)
    mark_y = NumericProperty(0)
    mark_width = NumericProperty("2sp")
    mark_height = NumericProperty("800sp")
    mark_color = ObjectProperty(defaultvalue=Color(*ON_BACKGROUND_COLOR))
    font_size = BoundedNumericProperty(sp(10), min=sp(10))
    # moments = ListProperty(list())
    # spacing = BoundedNumericProperty(sp(50), min=sp(1))  # in pixels
    """YEAR_INTERVAL = "year"
    MONTH_INTERVAL = "month"
    time_interval = OptionProperty()"""
    interval = ListProperty([])

    def __init__(self, **kwargs):
        self.draw_marks_trigger = Clock.create_trigger(self.draw_marks)
        super(Mark, self).__init__(**kwargs)
        self.bind(interval=self.draw_marks_trigger)

    """def __init__(self, **kwargs):
        self.draw_mark_trigger = Clock.create_trigger(self.draw_marks)
        super(Mark, self).__init__(**kwargs)
        self.bind(scroll_by=self.draw_mark_trigger, size=self.draw_mark_trigger)"""
        # todo translate canvas unless draw is necessary

    """def draw_marks(self, _) -> None:
        self.canvas.clear()

        self.canvas.add(self.mark_color)
        next_band_x = -self.spacing + (self.x % self.spacing)
        while next_band_x <= self.width:
            x = next_band_x + (self.scroll_by % self.spacing)

            label = self.make_label(x, self.label_align)
            rect_pos = sp(x), sp(self.mark_y)
            size = sp(self.mark_width), sp(self.mark_height)
            self.canvas.add(self.mark(pos=rect_pos, size=size))

            self.canvas.add(
                Rectangle(
                    pos=label.pos,
                    size=label.texture_size,
                    texture=label.texture,
                )
            )
            next_band_x += self.spacing"""

    """def draw_marks(self, *_) -> None:
        self.canvas.clear()

        self.canvas.add(self.mark_color)
        for moment in self.moments:
            x = self.parent.moment_to_x(moment)
            hr_date = self.parent.datetime.moment_to_hr_date(moment)
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
            )"""

    def draw_marks(self, *_) -> None:
        self.canvas.clear()
        self.canvas.add(self.mark_color)

        start_ast_ymd = self.parent.datetime.moment_to_ast_ymd(
            self.parent.start_moment
        )
        next_band_ast_ymd = self.parent.datetime.date.increment_ast_ymd(
            start_ast_ymd, [self.interval]
        )
        hr_date = self.parent.datetime.date.format_hr_date(
            next_band_ast_ymd
        )
        next_band_moment = self.parent.datetime.ast_ymd_to_moment(
            next_band_ast_ymd
        )
        next_band_x = self.parent.moment_to_x(next_band_moment)
        next_band_ordinal_decimal = self.parent.datetime.moment_to_ordinal_decimal(next_band_moment)
        end_ordinal_decimal = self.parent.datetime.moment_to_ordinal_decimal(
            self.parent.end_moment
        )
        while next_band_ordinal_decimal <= end_ordinal_decimal:
            label = self.make_label(
                next_band_x, hr_date, self.label_align
            )
            rect_pos = sp(next_band_x), sp(self.mark_y)
            size = sp(self.mark_width), sp(self.mark_height)
            self.canvas.add(self.mark(pos=rect_pos, size=size))
            self.canvas.add(
                Rectangle(
                    pos=label.pos,
                    size=label.texture_size,
                    texture=label.texture,
                )
            )

            next_band_ast_ymd = self.parent.datetime.date.increment_ast_ymd(
                next_band_ast_ymd, [self.interval]
            )

            hr_date = self.parent.datetime.date.format_hr_date(
                next_band_ast_ymd
            )
            next_band_moment = self.parent.datetime.ast_ymd_to_moment(
                next_band_ast_ymd
            )
            next_band_x = self.parent.moment_to_x(next_band_moment)
            next_band_ordinal_decimal = self.parent.datetime.moment_to_ordinal_decimal(next_band_moment)

    def make_label(self, x: int, text: str, alignment: str) -> TextBoundLabel:
        """
        :param x: x position of the mark related to this label
        :param text: text of the label
        :param alignment: horizontal alignment of the label
        :returns: the label
        :raises: ValueError if alignment is isn't a valid option
        """
        if alignment not in self._label_alignments:
            raise ValueError(f"{alignment} is not in a valid label alignment")

        label = TextBoundLabel(text=text, font_size=self.font_size)
        label.texture_update()
        if alignment == self.LABEL_LEFT:
            label_x = sp(x + self.label_padding_x)
        else:  # center alignment
            label_x = sp(x - int(label.width / 2) + self.label_padding_x)

        label_y = self.label_y or sp(
            self.top - self.font_size - self.label_padding_y
        )
        label.pos = label_x, label_y
        return label

    '''def make_label(self, x: int, alignment: str) -> TextBoundLabel:
        """
        :param x: x position of the mark related to this label
        :param alignment: horizontal alignment of the label
        :returns: the label
        :raises: ValueError if alignment is isn't a valid option
        """
        if alignment not in self._label_alignments:
            raise ValueError(f"{alignment} is not in a valid label alignment")

        label = TextBoundLabel(text=self.label_text, font_size=self.font_size)
        label.texture_update()
        if alignment == self.LABEL_LEFT:
            label_x = sp(x + self.label_padding_x)
        else:  # center alignment
            label_x = sp(x - int(label.width / 2) + self.label_padding_x)

        label_y = self.label_y or sp(
            self.top - self.font_size - self.label_padding_y
        )
        label.pos = label_x, label_y
        return label'''

    #
    # Disable Touch
    #
    def on_touch_down(self, touch):
        return False

    def on_touch_move(self, touch):
        return False

    def on_touch_up(self, touch):
        return False
