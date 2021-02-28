import copy
import numpy
import pytest

from kivy.graphics import Rectangle
from kivy.metrics import sp
from kivy.uix.label import Label
from src.ui.mark import Mark
from src.ui.textboundlabel import TextBoundLabel
from tests.utils import FAKE
from unittest.mock import Mock, patch


@patch("src.ui.mark.Mark.canvas")
@patch("src.ui.mark.Mark.make_label")
def test_draw_marks_without_mark_ods(mock_make_label, mock_canvas):
    timeline = Mock()
    extended_time_span = FAKE.pyfloat(min_value=5000, max_value=9999)
    timeline.extended_start_od = FAKE.pyfloat(min_value=-2000)
    timeline.extended_end_od = timeline.extended_start_od + extended_time_span
    timeline.width = timeline.extended_end_od + abs(FAKE.pyfloat())
    timeline.x, timeline.right = 0, timeline.width
    timeline.od_to_x = lambda od: od
    timeline.cdt.next_od.side_effect = (
        lambda od, _, **kwargs: od + extended_time_span / 10
    )
    timeline.mark_interval = FAKE.pylist(
        nb_elements=2, variable_nb_elements=False
    )
    timeline.cdt.date.is_era_unit.return_value = False

    mock_mark_graphic = Mock()
    mock_make_label.return_value = Label(text=FAKE.word())

    mark = Mark()
    mark.timeline = timeline
    mark.mark = mock_mark_graphic
    mark.interval = timeline.mark_interval

    assert all([isinstance(mark_od, float) for mark_od in mark.draw_marks()])
    assert any(  # label graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if isinstance(call.args[0], Rectangle)
    )
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert mark.interval_width > 0
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    timeline.cdt.next_od.assert_any_call(  # what the first mark_od should be
        timeline.extended_start_od, mark.interval, forward=False
    )
    mock_make_label.assert_called()

    mock_canvas.reset_mock(), mock_make_label.reset_mock()

    mark.has_label = False
    assert all([isinstance(mark_od, float) for mark_od in mark.draw_marks()])
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert mark.interval_width > 0
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    timeline.cdt.next_od.assert_any_call(  # what the first mark_od should be
        timeline.extended_start_od, mark.interval, forward=False
    )
    mock_make_label.assert_not_called()


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
    timeline.x, timeline.right = 0, timeline.width
    timeline.mark_interval = FAKE.pylist(
        nb_elements=2, variable_nb_elements=False
    )

    mark = Mark()
    mark.timeline = timeline
    mark.mark = mock_mark_graphic
    mark.interval = timeline.mark_interval

    assert mark.draw_marks(mark_ods=mark_ods) == mark_ods
    assert any(  # label graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if isinstance(call.args[0], Rectangle)
    )
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert round(mark.interval_width, 1) == round(expected_interval_width, 1)
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    mark.timeline.cdt.next_od.assert_not_called()
    mock_make_label.assert_called()

    mock_canvas.reset_mock(), mock_make_label.reset_mock()

    mark.has_label = False
    assert mark.draw_marks(mark_ods=mark_ods) == mark_ods
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert round(mark.interval_width, 1) == round(expected_interval_width, 1)
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    mark.timeline.cdt.next_od.assert_not_called()
    mock_make_label.assert_not_called()


@patch("src.ui.mark.Mark.canvas")
@patch("src.ui.mark.Mark.make_label")
def test_draw_marks_with_era_interval(mock_make_label, mock_canvas):
    mock_mark_graphic = Mock()
    mock_make_label.return_value = Label(text=FAKE.word())

    timeline = Mock()
    timeline.cdt.date.is_era_unit.return_value = True
    era_start_ordinals = [FAKE.random_int() for _ in range(5)]
    era_start_ordinals.insert(0, 0)
    timeline.cdt.era_start_ordinals = era_start_ordinals
    timeline.od_to_x = lambda x: x
    timeline.width = max(timeline.cdt.era_start_ordinals)
    timeline.x, timeline.right = 0, timeline.width
    timeline.mark_interval = FAKE.pylist(
        nb_elements=2, variable_nb_elements=False
    )

    mark = Mark()
    mark.timeline = timeline
    mark.mark = mock_mark_graphic
    mark.interval = timeline.mark_interval

    assert mark.draw_marks(mark_ods=era_start_ordinals) == era_start_ordinals
    assert any(  # label graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if isinstance(call.args[0], Rectangle)
    )
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert mark.interval_width > 0
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    mark.timeline.cdt.next_od.assert_not_called()
    mock_make_label.assert_called()


@patch.object(numpy, "isnan", return_value=True)
def test_draw_marks_raises(*_):

    mark = Mark(timeline=Mock())
    mark.interval = FAKE.pylist(nb_elements=2, variable_nb_elements=0)
    with pytest.raises(RuntimeError):
        mark.draw_marks()


@patch("src.ui.mark.Mark.canvas")
@patch("src.ui.mark.Mark.make_label")
def test_draw_marks_with_force_visible(mock_make_label, mock_canvas):
    mock_mark_graphic = Mock()
    mock_make_label.return_value = Label(text=FAKE.word())

    tl = Mock()
    visible_mark_x = 50
    mark_ods = [-100, visible_mark_x]
    returned_ods = copy.deepcopy(mark_ods)
    returned_ods.extend([FAKE.random_int(), visible_mark_x])
    tl.od_to_x.side_effect = returned_ods
    tl.width = 100
    tl.x, tl.right = 0, tl.width
    tl.mark_interval = FAKE.pylist(nb_elements=2, variable_nb_elements=0)
    mock_hr_date = tl.cdt.od_to_hr_date.return_value

    mark = Mark(force_visible=True)
    mark.timeline = tl
    mark.mark = mock_mark_graphic
    mark.interval = tl.mark_interval

    assert mark.draw_marks(mark_ods=mark_ods) == [tl.start_od, tl.end_od]
    assert any(  # label graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if isinstance(call.args[0], Rectangle)
    )
    assert any(  # mark graphic is somewhere in the canvas
        True
        for call in mark.canvas.add.call_args_list
        if mock_mark_graphic.return_value in call.args
    )
    assert mark.interval_width is None
    mock_canvas.clear.assert_called_once()
    mock_canvas.add.assert_any_call(mark.mark_color)
    tl.cdt.next_od.assert_any_call(tl.start_od, mark.interval, forward=False)
    tl.cdt.next_od.assert_any_call(tl.start_od, mark.interval)
    mock_mark_graphic.assert_any_call(
        pos=(visible_mark_x, mark.mark_y),
        size=(mark.mark_width, mark.mark_height),
    )
    mock_make_label.assert_any_call(tl.x, mock_hr_date, mark.LABEL_LEFT)
    mock_make_label.assert_any_call(tl.right, mock_hr_date, mark.LABEL_RIGHT)

    # don't test has_label=False and force_visible=True; inconsequential case


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

    made_label = mark.make_label(x, text, mark.LABEL_RIGHT)
    assert isinstance(made_label, TextBoundLabel)
    assert mark.max_label_width > 0
    assert made_label.right == x - mark.label_padding_x
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
