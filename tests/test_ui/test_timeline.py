import copy
import itertools
import pytest

from src.customdatetime import DateUnit, TimeUnit
from src.dbsetup import gregorian_cdt
from src.ui.mark import Mark
from src.ui.timeline import (
    Timeline,
    TimelineLayout,
    TimelineScrollView,
    TimelineScreen,
)
from tests.utils import FAKE
from unittest.mock import Mock, patch


def mocked_timeline():
    return Timeline(
        primary_mark=Mock(),
        secondary_mark=Mock(),
        event_view_mark=Mock(),
    )


def datetime_units():
    # fmt: off
    return [
        DateUnit.ERA, DateUnit.YEAR, DateUnit.MONTH, DateUnit.DAY,
        TimeUnit.HOUR, TimeUnit.MINUTE, TimeUnit.SECOND,
    ]
    # fmt: on


#
# Timeline
#
def test_timeline__get_time_span():
    tl = mocked_timeline()
    assert tl._get_time_span() == tl.end_od - tl.start_od


def test_timeline__get_extended_start_od():
    tl = mocked_timeline()
    cdt = Mock()
    tl.cdt = cdt
    assert tl._get_extended_start_od() == cdt.extend_od.return_value
    cdt.extend_od.assert_called_once_with(
        tl.start_od,
        tl.secondary_mark_interval,
        tl.extend_time_span_by,
        reverse=True,
    )


def test_timeline__get_extended_end_od():
    tl = mocked_timeline()
    cdt = Mock()
    tl.cdt = cdt
    assert tl._get_extended_end_od() == cdt.extend_od.return_value
    cdt.extend_od.assert_called_once_with(
        tl.end_od,
        tl.secondary_mark_interval,
        tl.extend_time_span_by,
    )


def test_timeline__get_extended_time_span():
    tl = mocked_timeline()
    extended_start_od, extended_end_od = FAKE.pyfloat(), FAKE.pyfloat()
    cdt = Mock()
    cdt.extend_od.side_effect = [extended_end_od, extended_start_od]
    tl.cdt = cdt
    expected_time_span = extended_end_od - extended_start_od
    assert tl._get_extended_time_span() == expected_time_span


@patch("kivy.clock.Clock.create_trigger")
@patch("src.ui.timeline.Timeline.bind")
def test_timeline_draw_mark_trigger(mock_bind, mock_create_trigger):
    tl = mocked_timeline()
    tl.size = 200, 200
    # extended_start_od/end_od cant' be set so test that they're bound
    assert tl.draw_marks_trigger == mock_create_trigger.return_value
    assert any(
        True
        for call in itertools.chain(mock_bind.call_args_list)
        if ("extended_start_od", tl.draw_marks_trigger) in call.kwargs.items()
    )
    assert any(
        True
        for call in itertools.chain(mock_bind.call_args_list)
        if ("extended_end_od", tl.draw_marks_trigger) in call.kwargs.items()
    )
    mock_create_trigger.assert_any_call(tl.draw_marks)
    tl.draw_marks_trigger.assert_called()


@patch("src.ui.timeline.Timeline.bind")
def test_timeline_give_focus(mock_bind):
    tl = mocked_timeline()
    tl.focus = FAKE.pybool()
    assert any(
        True
        for call in itertools.chain(mock_bind.call_args_list)
        if ("focus", tl.give_focus) in call.kwargs.items()
    )


def test_timeline_scroll_start_and_end():
    timeline = mocked_timeline()
    old_start_od, old_end_od = timeline.start_od, timeline.end_od
    cdt = Mock()
    cdt.extend_od.return_value = FAKE.pyfloat()
    timeline.cdt = cdt
    timeline.dx_to_dod = Mock()
    dod = FAKE.pyfloat()
    timeline.dx_to_dod.return_value = dod

    scroll_by = FAKE.pyfloat(min_value=1)
    timeline.scroll_by = scroll_by
    assert timeline.start_od == old_start_od - dod
    assert timeline.end_od == old_end_od - dod
    timeline.dx_to_dod.assert_called_once_with(scroll_by)
    timeline.dx_to_dod.reset_mock()

    old_start_od, old_end_od = timeline.start_od, timeline.end_od
    timeline.scroll_by = 0
    assert timeline.start_od == old_start_od
    assert timeline.end_od == old_end_od
    timeline.dx_to_dod.assert_not_called()


def test_timeline_zoom_start_and_end():
    timeline = mocked_timeline()
    old_start_od, old_end_od = timeline.start_od, timeline.end_od
    cdt = Mock()
    cdt.extend_od.return_value = FAKE.pyfloat()
    timeline.cdt = cdt
    timeline.dx_to_dod = Mock()
    dod = FAKE.pyfloat()
    timeline.dx_to_dod.return_value = dod

    zoom_by = FAKE.pyfloat()
    timeline.zoom_by = zoom_by
    assert timeline.start_od == old_start_od + dod
    assert timeline.end_od == old_end_od - dod
    timeline.dx_to_dod.assert_called_once_with(zoom_by)
    timeline.dx_to_dod.reset_mock()

    old_start_od, old_end_od = timeline.start_od, timeline.end_od
    timeline.zoom_by = 0
    assert timeline.start_od == old_start_od
    assert timeline.end_od == old_end_od
    timeline.dx_to_dod.assert_not_called()


def test_timeline_check_mark_spacing():
    tl = mocked_timeline()
    tl.cdt = Mock()
    tl.cdt.extend_od.return_value = FAKE.pyfloat()
    tl.change_interval = Mock()
    tl.change_interval.return_value = FAKE.pylist()
    tl.change_interval_unit = Mock()
    tl.bad_mark_spacing = Mock()

    dateunit = FAKE.random_element(elements=DateUnit)
    old_mark_interval = [FAKE.random_int(min=1), dateunit]
    tl.secondary_mark_interval = copy.deepcopy(old_mark_interval)

    tl.on_kv_post(tl)
    assert any(  # check_mark_spacing bound to mark_interval property
        True
        for call in itertools.chain(tl.secondary_mark.bind.call_args_list)
        if ("interval_width", tl.check_mark_spacing) in call.kwargs.items()
    )

    tl.bad_mark_spacing.return_value = True
    tl.check_mark_spacing()
    assert tl.secondary_mark_interval == tl.change_interval.return_value
    tl.bad_mark_spacing.assert_called_with(
        tl.secondary_mark.interval_width, tl.width
    )
    tl.change_interval.assert_called_with(old_mark_interval, tl)
    tl.change_interval.reset_mock(), tl.bad_mark_spacing.reset_mock()

    tl.bad_mark_spacing.side_effect = [False, True]
    old_mark_interval = tl.secondary_mark_interval
    tl.check_mark_spacing()
    assert tl.secondary_mark_interval == tl.change_interval.return_value
    tl.bad_mark_spacing.assert_any_call(
        tl.secondary_mark.max_label_width,
        tl.secondary_mark.interval_width,
        spacing="too_many",
    )
    tl.change_interval.assert_called_with(old_mark_interval, increase=False)
    tl.change_interval.reset_mock(), tl.bad_mark_spacing.reset_mock()

    tl.bad_mark_spacing.side_effect = [False, False]
    tl.secondary_mark.max_label_width = tl.secondary_mark.interval_width
    tl.check_mark_spacing()
    tl.bad_mark_spacing.assert_any_call(
        tl.secondary_mark.max_label_width,
        tl.secondary_mark.interval_width,
        spacing="too_many",
    )
    tl.bad_mark_spacing.assert_any_call(
        tl.secondary_mark.interval_width, tl.width
    )
    tl.change_interval.assert_not_called()


def test_timeline_change_interval():
    timeline = Timeline(
        primary_mark=Mark(),
        secondary_mark=Mark(),
        event_view_mark=Mark(),
        cdt=gregorian_cdt,
    )
    old_frequency = 100_000
    interval = [old_frequency, DateUnit.YEAR]
    timeline.secondary_mark_interval = interval
    timeline.end_od = timeline.start_od + old_frequency * 365.25
    new_freq, new_unit = timeline.change_interval(interval)
    assert new_freq < old_frequency or new_unit != DateUnit.YEAR

    old_frequency = 1
    interval = [old_frequency, DateUnit.DAY]
    new_freq, new_unit = timeline.change_interval(interval)
    assert new_freq < old_frequency or new_unit not in DateUnit

    interval = [old_frequency, TimeUnit.SECOND]
    timeline.secondary_mark_interval = interval
    timeline.end_od = timeline.start_od + 365.25
    new_freq, new_unit = timeline.change_interval(interval, increase=False)
    assert new_freq < old_frequency or new_unit != DateUnit.YEAR


def test_timeline_change_interval_recursively_changing_unit():
    timeline = mocked_timeline()
    timeline.cdt = gregorian_cdt
    timeline.cdt.get_frequencies = Mock()
    frequencies = [FAKE.random_int(min=1) for _ in range(10)]
    timeline.cdt.get_frequencies.return_value = frequencies
    timeline.change_interval_unit = Mock()
    timeline.od_to_x = Mock()  # mock too few marks on screen
    timeline.od_to_x.side_effect = [0, timeline.width + FAKE.random_int(min=1)]
    timeline.bad_mark_spacing = Mock()
    timeline.bad_mark_spacing.return_value = True

    frequency = FAKE.random_element(elements=frequencies)
    unit = FAKE.random_element(elements=datetime_units())
    expected_interval = [frequency, unit]
    timeline.change_interval_unit.side_effect = [None, expected_interval]

    old_frequency = FAKE.random_int(min=1)
    frequency = FAKE.random_element(elements=frequencies)
    unit = FAKE.random_element(elements=datetime_units())
    interval = [frequency, unit]
    timeline.secondary_mark_interval = interval
    timeline.end_od = timeline.start_od + old_frequency * 365.25
    assert timeline.change_interval(interval, timeline) == expected_interval


@patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
def test_timeline_change_interval_unit_when_increasing_unit(mock):
    mock_get_frequencies = mock

    non_year_or_era_units = [DateUnit.MONTH, DateUnit.DAY]
    non_year_or_era_units.extend(TimeUnit)
    non_year_or_era_unit = FAKE.random_element(elements=non_year_or_era_units)
    frequencies = [FAKE.random_int(min=1) for _ in range(5)]
    mock_get_frequencies.return_value = frequencies

    timeline = mocked_timeline()
    timeline.cdt = Mock()
    timeline.cdt.get_frequencies = mock_get_frequencies
    timeline.cdt.datetime_units = datetime_units()
    timeline.cdt.is_datetime_unit.return_value = False
    timeline.change_interval = Mock()

    non_year_interval = [max(frequencies), non_year_or_era_unit]
    assert (
        timeline.change_interval_unit(non_year_interval, increase=False)
        == timeline.change_interval.return_value
    )

    timeline.cdt.is_datetime_unit.return_value = True
    year_interval = [max(frequencies), DateUnit.YEAR]
    with pytest.raises(ValueError):
        timeline.change_interval_unit(year_interval, increase=False)


@patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
def test_timeline_change_interval_unit_when_decreasing_unit(mock):
    mock_get_frequencies = mock

    non_sec_units = [*DateUnit]
    non_sec_units.extend([TimeUnit.HOUR, TimeUnit.MINUTE])
    non_sec_unit = FAKE.random_element(elements=non_sec_units)
    frequencies = [FAKE.random_int(min=1) for _ in range(5)]
    mock_get_frequencies.return_value = frequencies

    timeline = mocked_timeline()
    timeline.cdt = Mock()
    timeline.cdt.get_frequencies = mock_get_frequencies
    timeline.cdt.datetime_units = datetime_units()
    timeline.cdt.is_datetime_unit.return_value = False
    timeline.change_interval = Mock()

    non_sec_interval = [min(frequencies), non_sec_unit]
    assert (
        timeline.change_interval_unit(non_sec_interval, increase=True)
        == timeline.change_interval.return_value
    )

    timeline.cdt.is_datetime_unit.return_value = True
    second_interval = [min(frequencies), TimeUnit.SECOND]
    with pytest.raises(ValueError):
        timeline.change_interval_unit(second_interval, increase=True)


def test_timeline_change_unit_can_do_nothing():
    timeline = mocked_timeline()
    timeline.cdt = Mock()
    timeline.change_interval = Mock()

    frequencies = [FAKE.random_int(min=1) for _ in range(5)]
    frequencies.sort()
    timeline.cdt.get_frequencies.return_value = frequencies
    frequency = FAKE.random_element(elements=frequencies[1:-1])
    interval = [frequency, Mock()]
    assert timeline.change_interval_unit(interval, FAKE.pybool()) is None
    timeline.change_interval.assert_not_called()


def test_timeline_bad_mark_spacing():
    timeline = mocked_timeline()
    width = timeline.width
    interval_width = width
    assert timeline.bad_mark_spacing(width, interval_width)

    interval_width = (width * timeline.too_few_marks_factor) + 1
    assert not timeline.bad_mark_spacing(width, interval_width)

    interval_width = (width * timeline.too_many_marks_factor) - 1
    assert timeline.bad_mark_spacing(width, interval_width, spacing="too_many")

    interval_width = (width * timeline.too_many_marks_factor) + 1
    assert not timeline.bad_mark_spacing(
        width, interval_width, spacing="too_many"
    )


def test_timeline_draw_marks():
    timeline = mocked_timeline()
    timeline.draw_marks(Mock())
    timeline.secondary_mark.draw_marks.assert_called_once()
    timeline.event_view_mark.draw_marks.assert_called_once_with(
        mark_ods=timeline.secondary_mark.draw_marks.return_value
    )


def test_timeline_update_mark_interval():
    tl = mocked_timeline()
    tl.cdt = Mock()
    tl.cdt.extend_od.return_value = FAKE.pyfloat()
    tl.secondary_mark_interval = FAKE.pylist()
    assert tl.secondary_mark.interval == tl.secondary_mark_interval
    assert tl.event_view_mark.interval == tl.secondary_mark.interval
    assert tl.primary_mark.interval == tl.cdt.get_primary_interval.return_value


def test_timeline_disable_zoom():
    timeline = mocked_timeline()
    timeline.shift_key = True
    assert timeline.disable_zoom_in is timeline.shift_key
    assert timeline.disable_zoom_out is timeline.shift_key

    timeline.shift_key = False
    assert timeline.disable_zoom_in is timeline.shift_key
    assert timeline.disable_zoom_out is timeline.shift_key


def test_timeline_set_drag_hor_scroll():
    timeline = mocked_timeline()
    timeline.touches = FAKE.pylist(nb_elements=2, variable_nb_elements=False)
    assert timeline.disable_drag_hor_scroll

    timeline.touches = FAKE.pylist(nb_elements=1)
    assert not timeline.disable_drag_hor_scroll


@patch("src.ui.focusedkeylisten.FocusKeyListenBehavior.gain_focus")
def test_timeline_gain_focus(mock_fkl_gain_focus):
    timeline = mocked_timeline()
    timeline.descendant_focused = Mock()
    timeline.descendant_focused.return_value = True
    timeline.gain_focus()
    mock_fkl_gain_focus.assert_not_called()

    timeline.descendant_focused.return_value = False
    timeline.gain_focus()
    mock_fkl_gain_focus.assert_called_once()


def test_timeline_descendant_focused():
    timeline = mocked_timeline()
    assert not timeline.descendant_focused()

    collapse_bar = Mock()
    collapse_bar.focus = True
    timeline.collapse_bar = collapse_bar
    assert timeline.descendant_focused()
    timeline.collapse_bar.focus = False

    event_view = Mock()
    event_view.focus = True
    timeline.event_view = event_view
    assert timeline.descendant_focused()
    timeline.event_view.focus = False

    collapse_bar = Mock()
    collapse_bar.focus = True
    timeline.collapse_bar = collapse_bar
    assert timeline.descendant_focused()
    timeline.collapse_bar.focus = False

    mark_bar = Mock()
    mark_bar.focus = True
    timeline.mark_bar = mark_bar
    assert timeline.descendant_focused()


def test_timeline_od_to_x():
    timeline = mocked_timeline()
    timeline.dod_to_dx = Mock()
    dx = FAKE.pyfloat()
    timeline.dod_to_dx.return_value = dx
    ordinal_decimal = FAKE.pyfloat()
    dod = ordinal_decimal - timeline.start_od
    assert timeline.od_to_x(ordinal_decimal) == timeline.x + dx
    timeline.dod_to_dx.assert_called_once_with(dod)


def test_timeline_dod_to_dx():
    timeline = mocked_timeline()
    width = timeline.width
    percent = FAKE.random.uniform(0, 1)
    dod = percent * timeline.time_span
    assert round(timeline.dod_to_dx(dod), 5) == round(width * percent, 5)


def test_timeline_dx_to_dod():
    timeline = mocked_timeline()
    percent = FAKE.random.uniform(0, 1)
    dx = percent * timeline.width
    expected_dx = round(timeline.time_span * percent, 5)
    assert round(timeline.dx_to_dod(dx), 5) == expected_dx


#
# TimelineScrollView
#
def test_timelinescrollview_bind_child():
    tl_scroll_view = TimelineScrollView()
    child = Mock()
    tl_scroll_view.children = [child]
    child.bind.assert_any_call(
        height=tl_scroll_view.set_do_scroll_y,
        timelines=tl_scroll_view.set_do_scroll_y,
    )
    child.bind.assert_any_call(timelines=tl_scroll_view.bind_child_timelines)


def test_timelinescrollview_bind_child_timelines():
    collapse_bar1 = Mock()
    event_view1, event_view2 = Mock(), Mock()
    mark_bar2 = Mock()
    timeline1 = Mock()
    timeline1.focusable_descendants = [collapse_bar1, event_view1, None]
    timeline2 = Mock()
    timeline2.focusable_descendants = [None, event_view2, mark_bar2]
    child = Mock()
    child.timelines = [timeline1, timeline2]
    tl_scroll_view = TimelineScrollView()
    tl_scroll_view.children = [child]

    tl_scroll_view.bind_child_timelines()
    for timeline in child.timelines:
        timeline.bind.assert_any_call(focus=tl_scroll_view.set_do_scroll_y)
        timeline.bind.assert_any_call(
            focus=tl_scroll_view.scroll_to_focused_widget
        )
    collapse_bar1.bind.assert_any_call(focus=tl_scroll_view.set_do_scroll_y)
    event_view1.bind.assert_any_call(focus=tl_scroll_view.set_do_scroll_y)
    event_view2.bind.assert_any_call(
        focus=tl_scroll_view.scroll_to_focused_widget
    )
    mark_bar2.bind.assert_any_call(
        focus=tl_scroll_view.scroll_to_focused_widget
    )


def test_timelinescrollview_set_do_scroll_y():
    timeline1 = Mock()
    timeline1.focus = True
    timeline1.descendant_focused.return_value = False
    timeline2 = Mock()
    timeline2.focus = False
    timeline2.descendant_focused.return_value = False
    tl_scroll_view = TimelineScrollView()
    child = Mock()
    child.timelines = [timeline1, timeline2]
    child.height = tl_scroll_view.height + FAKE.pyfloat(min_value=1)
    tl_scroll_view.children = [child]
    tl_scroll_view.set_do_scroll_y()
    assert not tl_scroll_view.do_scroll_y
    timeline1.focus = False

    timeline2.descendant_focused.return_value = True
    tl_scroll_view.set_do_scroll_y()
    assert not tl_scroll_view.set_do_scroll_y()
    timeline2.descendant_focused.return_value = False

    child.height = tl_scroll_view.height + FAKE.pyfloat(min_value=1)
    tl_scroll_view.set_do_scroll_y()
    assert tl_scroll_view.do_scroll_y

    child.height = tl_scroll_view.height - FAKE.pyfloat(min_value=1)
    tl_scroll_view.set_do_scroll_y()
    assert not tl_scroll_view.do_scroll_y


def test_timelinescrollview_scroll_to_focused_widget():
    tl_scroll_view = TimelineScrollView()
    tl_scroll_view.scroll_to = Mock()
    mock_widget = Mock()

    tl_scroll_view.scroll_to_focused_widget(mock_widget, False)
    tl_scroll_view.scroll_to.assert_not_called()

    tl_scroll_view.scroll_to_focused_widget(mock_widget, True)
    tl_scroll_view.scroll_to.assert_called_with(mock_widget)


#
# TimelineLayout
#
@patch("kivy.uix.floatlayout.FloatLayout.add_widget")
def test_timelinlayout_add_widget(mock_fl_add_widget):
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines.insert = Mock()
    timeline = mocked_timeline()
    timeline.bind = Mock()
    canvas = Mock()
    index = FAKE.random_int()
    widget = Mock()
    mock_fl_add_widget.reset_mock()  # to remove any descendants calls
    tl_layout.add_widget(widget, index, canvas)
    mock_fl_add_widget.assert_called_once_with(
        widget, index=index, canvas=canvas
    )
    tl_layout.timelines.insert.assert_not_called()
    widget.bind.assert_not_called()
    mock_fl_add_widget.reset_mock()

    tl_layout.add_widget(timeline, index=index, canvas=canvas)
    mock_fl_add_widget.assert_called_once_with(
        timeline, index=index, canvas=canvas
    )
    tl_layout.timelines.insert.assert_called_once_with(index, timeline)
    timeline.bind.assert_called_with(height=tl_layout.resize_timelines)


@patch("kivy.uix.floatlayout.FloatLayout.remove_widget")
def test_timelinelayout_remove_widget(mock_fl_remove_widget):
    tl_layout = TimelineLayout(parent=Mock())
    mock_widget = Mock()
    tl_layout.remove_widget(mock_widget)
    mock_fl_remove_widget.assert_called_once_with(mock_widget)
    mock_fl_remove_widget.reset_mock()

    mock_timeline = Mock()
    tl_layout.timelines.append(mock_timeline)
    tl_layout.remove_widget(mock_timeline)
    assert mock_timeline not in tl_layout.timelines
    mock_fl_remove_widget.assert_called_once_with(mock_timeline)


def test_timelinelayout_on_kv_post():
    parent = Mock()
    tl_layout = TimelineLayout(parent=parent)
    parent.bind.assert_called_with(height=tl_layout.resize_timelines)


@patch("kivy.clock.Clock.schedule_once")
def test_timelinelayout_on_timelines(mock_schedule_once):
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines = [Mock()]
    mock_schedule_once.assert_called_with(tl_layout.resize_timelines, -1)


@patch("src.ui.timeline.TimelineLayout.default_timeline_height")
def test_timelinelayout_resize_timelines(mock_default_timeline_height):
    mock_default_timeline_height.return_value = FAKE.pyfloat()

    parent = Mock()
    parent.height = FAKE.pyfloat(min_value=1)
    tl_layout = TimelineLayout(parent=parent)
    tl_layout.set_collapsable_timelines = Mock()
    tl_layout.set_height = Mock()
    tl_layout.set_timeline_listeners = Mock()
    mock_top_tl = Mock()
    tl_layout.timelines = [mock_top_tl]

    tl_layout.resize_timelines()
    assert mock_top_tl.expanded_height == tl_layout.parent.height
    assert mock_top_tl.expanded_y == tl_layout.parent.y
    tl_layout.set_height.assert_called_once()
    tl_layout.set_height.reset_mock()

    mock_bottom_tl = Mock()
    mock_bottom_tl.y = 0
    tl_layout.timelines = [mock_bottom_tl, mock_top_tl]
    tl_layout.resize_timelines()
    assert mock_top_tl.expanded_height == tl_layout.default_timeline_height
    assert (
        mock_top_tl.expanded_y == tl_layout.top - mock_top_tl.expanded_height
    )
    assert mock_bottom_tl.expanded_height == tl_layout.default_timeline_height
    assert (
        mock_bottom_tl.expanded_y
        == mock_top_tl.y - mock_bottom_tl.expanded_height
    )
    tl_layout.set_height.assert_called_once()
    tl_layout.set_timeline_listeners.assert_called_once()
    tl_layout.set_height.reset_mock()
    tl_layout.set_timeline_listeners.reset_mock()

    mock_mid_tl = Mock()
    mock_mid_tl.y = 0
    tl_layout.timelines = [mock_bottom_tl, mock_mid_tl, mock_top_tl]
    tl_layout.resize_timelines()
    assert mock_top_tl.expanded_height == tl_layout.default_timeline_height
    assert (
        mock_top_tl.expanded_y == tl_layout.top - mock_top_tl.expanded_height
    )
    assert mock_mid_tl.expanded_height == tl_layout.default_timeline_height
    assert (
        mock_mid_tl.expanded_y
        == mock_top_tl.y - mock_bottom_tl.expanded_height
    )
    assert mock_bottom_tl.expanded_height == tl_layout.default_timeline_height
    assert (
        mock_bottom_tl.expanded_y
        == mock_mid_tl.y - mock_bottom_tl.expanded_height
    )


def test_timelinelayout_set_height():
    parent = Mock()
    parent.height = FAKE.pyfloat(min_value=1)
    tl_layout = TimelineLayout(parent=parent)
    tl_layout.set_height()
    assert tl_layout.height == tl_layout.parent.height

    timeline1, timeline2, timeline3 = Mock(), Mock(), Mock()
    timeline1.collapsed = True
    timeline1.collapsed_height = FAKE.pyfloat(min_value=1)
    timeline2.collapsed, timeline3.collapsed = False, False
    tl_layout.timelines = [timeline1, timeline2, timeline3]
    tl_layout.set_height()
    assert round(tl_layout.height, 5) == round(
        sum(
            [timeline1.collapsed_height, 2 * tl_layout.default_timeline_height]
        ),
        5,
    )


def test_timelinelayout_set_collapsable_timelines():
    timeline1, timeline2, timeline3 = Mock(), Mock(), Mock()
    timeline1.collapsed = timeline2.collapsed = timeline3.collapsed = False
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines = [timeline1, timeline2, timeline3]
    tl_layout.set_collapsable_timelines()
    assert timeline1.collapsable
    assert timeline2.collapsable
    assert timeline3.collapsable

    timeline2.collapsed = True
    tl_layout.set_collapsable_timelines()
    assert not timeline1.collapsable
    assert timeline2.collapsable
    assert not timeline3.collapsable


def test_timelinelayout_set_timeline_listeners():
    bottom_timeline, mid_timeline, top_timeline = Mock(), Mock(), Mock()
    top_timeline.previous_active_listener = None
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines = [bottom_timeline, mid_timeline, top_timeline]
    tl_layout.above_timeline = Mock()
    tl_layout.below_timeline = Mock()
    tl_layout.set_timeline_listeners()

    assert top_timeline.previous_active_listener is None  # set by kv file
    assert (
        top_timeline.next_active_listener
        == tl_layout.below_timeline.return_value
    )
    assert (
        mid_timeline.previous_active_listener
        == tl_layout.above_timeline.return_value
    )
    assert (
        mid_timeline.next_active_listener
        == tl_layout.below_timeline.return_value
    )
    assert (
        bottom_timeline.previous_active_listener
        == tl_layout.above_timeline.return_value
    )
    assert (
        bottom_timeline.next_active_listener
        == tl_layout.below_timeline.return_value
    )


def test_timelinelayout_below_timeline():
    bottom_timeline, mid_timeline, top_timeline = Mock(), Mock(), Mock()
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines = [bottom_timeline, mid_timeline, top_timeline]

    assert tl_layout.below_timeline(top_timeline) == mid_timeline
    assert tl_layout.below_timeline(mid_timeline) == bottom_timeline
    assert tl_layout.below_timeline(bottom_timeline) is None


def test_timelinelayout_above_timeline():
    bottom_timeline, mid_timeline, top_timeline = Mock(), Mock(), Mock()
    tl_layout = TimelineLayout(parent=Mock())
    tl_layout.timelines = [bottom_timeline, mid_timeline, top_timeline]

    assert tl_layout.above_timeline(top_timeline) is None
    assert tl_layout.above_timeline(mid_timeline) == top_timeline
    assert tl_layout.above_timeline(bottom_timeline) == mid_timeline


def test_timelinelayout_top_timeline():
    tl_layout = TimelineLayout(parent=Mock())
    top_timeline = Mock()
    tl_layout.timelines = FAKE.pylist()
    tl_layout.timelines.extend([top_timeline])
    assert tl_layout.top_timeline == top_timeline


def test_timelinelayout_default_timeline_height():
    parent = Mock()
    parent.height = FAKE.pyfloat(min_value=1)
    tl_layout = TimelineLayout(parent=parent)
    assert 0 < tl_layout.default_timeline_height < parent.height


#
# TimelineScreen
#
@patch("src.ui.timeline.TimelineScreen.bind")
def test_binding(mock_bind):
    timeline_screen = TimelineScreen()
    mock_bind.assert_called_with(focus=timeline_screen.give_focus)
