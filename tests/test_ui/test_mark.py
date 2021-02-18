import pytest

from kivy.graphics import Rectangle
from kivy.metrics import sp
from kivy.uix.label import Label
from src.ui.mark import Mark
from src.ui.textboundlabel import TextBoundLabel
from tests.utils import FAKE
from unittest.mock import Mock, patch


@patch("kivy.clock.Clock.create_trigger")
@patch("src.ui.mark.Mark.bind")
def test_draw_marks_trigger(mock_bind, mock_create_trigger):
    draw_marks_trigger = mock_create_trigger.return_value
    mark = Mark()
    mock_create_trigger.assert_called_with(mark.draw_marks)
    mock_bind.assert_called_with(
        pos=draw_marks_trigger,
        size=draw_marks_trigger,
    )


@patch("src.ui.mark.Mark.canvas")
@patch("src.ui.mark.Mark.make_label")
def test_draw_marks_without_mark_ods(mock_make_label, mock_canvas):
    timeline = Mock()
    extended_time_span = FAKE.pyfloat(min_value=5000, max_value=9999)
    timeline.extended_start_od = FAKE.pyfloat(min_value=-2000)
    timeline.extended_end_od = timeline.extended_start_od + extended_time_span
    timeline.width = timeline.extended_end_od + abs(FAKE.pyfloat())
    timeline.od_to_x = lambda od: od
    timeline.cdt.next_od = lambda od, _: od + extended_time_span / 10
    timeline.mark_interval = FAKE.pylist(
        nb_elements=2, variable_nb_elements=False
    )

    mock_mark_graphic = Mock()
    mock_make_label.return_value = Label(text=FAKE.word())

    mark = Mark()
    mark.timeline = timeline
    mark.mark = mock_mark_graphic

    assert all([isinstance(mark_od, float) for mark_od in mark.draw_marks()])
    assert any(  # label graphic is somewhere in the canvas
        [
            True
            for call in mark.canvas.add.call_args_list
            if isinstance(call.args[0], Rectangle)
        ]
    )
    assert any(  # mark graphic is somewhere in the canvas
        [
            True
            for call in mark.canvas.add.call_args_list
            if mock_mark_graphic.return_value in call.args
        ]
    )
    assert mark.interval_width > 0
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    mock_make_label.assert_called()


@patch("src.ui.mark.Mark.canvas")
@patch("src.ui.mark.Mark.make_label")
def test_draw_marks_with_mark_ods(mock_make_label, mock_canvas):
    mock_mark_graphic = Mock()
    mock_make_label.return_value = Label(text=FAKE.word())
    expected_interval_width = FAKE.pyfloat(min_value=1)
    mark_ods = [n * expected_interval_width for n in range(10)]

    timeline = Mock()
    timeline.od_to_x = lambda x: x
    timeline.width = max(mark_ods)
    timeline.mark_interval = FAKE.pylist(
        nb_elements=2, variable_nb_elements=False
    )

    mark = Mark()
    mark.timeline = timeline
    mark.mark = mock_mark_graphic

    assert mark.draw_marks(mark_ods=mark_ods) == mark_ods
    assert any(  # label graphic is somewhere in the canvas
        [
            True
            for call in mark.canvas.add.call_args_list
            if isinstance(call.args[0], Rectangle)
        ]
    )
    assert any(  # mark graphic is somewhere in the canvas
        [
            True
            for call in mark.canvas.add.call_args_list
            if mock_mark_graphic.return_value in call.args
        ]
    )
    assert mark.interval_width == expected_interval_width
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    mark.timeline.cdt.next_od.assert_not_called()
    mock_make_label.assert_called()


def test_make_label():
    x = FAKE.pyfloat()
    text = FAKE.word()
    mark = Mark()
    made_label = mark.make_label(x, text, mark.LABEL_LEFT)
    assert isinstance(made_label, TextBoundLabel)
    assert mark.max_label_width > 0
    assert made_label.x == sp(x + mark.label_padding_x)
    assert made_label.top == mark.top - mark.label_padding_y
    assert made_label.text == text
    assert made_label.font_size == mark.font_size

    made_label = mark.make_label(x, text, mark.LABEL_CENTER)
    assert isinstance(made_label, TextBoundLabel)
    assert mark.max_label_width > 0
    assert made_label.center_x == sp(x)
    assert made_label.top == mark.top - mark.label_padding_y
    assert made_label.text == text
    assert made_label.font_size == mark.font_size

    mark.interval_width = FAKE.pyfloat(min_value=1)
    made_label = mark.make_label(x, text, mark.LABEL_MID_INTERVAL)
    assert isinstance(made_label, TextBoundLabel)
    assert mark.max_label_width > 0
    assert made_label.center_x == sp(x + mark.interval_width / 2)
    assert made_label.text == text
    assert made_label.font_size == mark.font_size

    mark.label_y = FAKE.pyfloat()
    alignment = FAKE.random_element(elements=mark._label_alignments)
    made_label = mark.make_label(x, text, alignment)
    assert isinstance(made_label, TextBoundLabel)
    assert mark.max_label_width > 0
    assert made_label.y == mark.label_y
    assert made_label.text == text
    assert made_label.font_size == mark.font_size

    with pytest.raises(ValueError):
        mark.make_label(x, text, Mock())
