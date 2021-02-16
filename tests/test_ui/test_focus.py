from kivy.uix.widget import Widget
from src.ui.focus import AbstractFocus
from tests.test_ui.utils import reset_focus_instances
from tests.utils import FAKE
from unittest.mock import Mock, patch


class FocusWidget(AbstractFocus, Widget):
    pass


def test__init__():
    focus_widget = FocusWidget()
    assert focus_widget in AbstractFocus._instances
    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.lose_focus")
@patch("src.ui.focus.AbstractFocus._ensure_none_focused")
def test_set_focus_next(patch__ensure_none_focused, patch_lose_focus):
    focus_widget = FocusWidget()
    mock_focus_next = Mock()

    focus_widget.set_focus_next()
    patch_lose_focus.assert_called_once()
    patch__ensure_none_focused.assert_called_once()
    mock_focus_next.gain_focus.assert_not_called()
    patch_lose_focus.reset_mock()
    patch__ensure_none_focused.reset_mock()

    focus_widget.focus_next = mock_focus_next
    focus_widget.set_focus_next()
    patch_lose_focus.assert_called_once()
    mock_focus_next.gain_focus.assert_called_once()
    patch__ensure_none_focused.assert_not_called()
    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.lose_focus")
@patch("src.ui.focus.AbstractFocus._ensure_none_focused")
def test_set_focus_previous(patch__ensure_none_focused, patch_lose_focus):
    focus_widget = FocusWidget()
    mock_focus_previous = Mock()

    focus_widget.set_focus_previous()
    patch_lose_focus.assert_called_once()
    patch__ensure_none_focused.assert_called_once()
    mock_focus_previous.gain_focus.assert_not_called()
    patch_lose_focus.reset_mock()
    patch__ensure_none_focused.reset_mock()

    focus_widget.focus_previous = mock_focus_previous
    focus_widget.set_focus_previous()
    patch_lose_focus.assert_called_once()
    mock_focus_previous.gain_focus.assert_called_once()
    patch__ensure_none_focused.assert_not_called()
    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.lose_focus")
def test__ensure_none_focused(patch_lose_focus):
    focus_widget = FocusWidget()
    AbstractFocus._current_focused_widget = focus_widget
    focus_widget._ensure_none_focused()
    patch_lose_focus.assert_called_once()
    assert AbstractFocus._current_focused_widget is None

    focus_widget._ensure_none_focused()  # doesn't error with no focused widget
    assert AbstractFocus._current_focused_widget is None

    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.defocus_others")
@patch("src.ui.focus.AbstractFocus.change_focus_highlight_color")
def test_on_focus(patch_change_focus_highlight_color, patch_defocus_others):
    focus_widget = FocusWidget()
    focus_widget.focus = not focus_widget.focus
    patch_defocus_others.assert_called_once()
    patch_change_focus_highlight_color.assert_called_once()
    reset_focus_instances()


def test_defocus_others():
    def mock_lose_focus():
        mock_focus_widget.focus = False

    focused_widget1 = FocusWidget()  # not focused yet
    focused_widget1.defocus_others()
    assert AbstractFocus._current_focused_widget is None

    focused_widget1.focus = True
    mock_focus_widget = Mock()
    mock_focus_widget.focus = True
    mock_focus_widget.lose_focus = mock_lose_focus
    AbstractFocus._instances.append(mock_focus_widget)
    all_unfocused_widgets = AbstractFocus._instances
    all_unfocused_widgets.remove(focused_widget1)

    focused_widget1.defocus_others()
    assert AbstractFocus._current_focused_widget == focused_widget1
    assert mock_focus_widget.focus is False
    assert all([instance.focus is False for instance in all_unfocused_widgets])
    reset_focus_instances()


@patch("kivy.uix.widget.Widget.collide_point")
@patch("kivy.uix.widget.Widget.on_touch_down")
@patch("src.ui.focus.AbstractFocus.gain_focus")
def test_on_touch_down(*patches):
    patch_gain_focus = patches[0]
    patch_widget_on_touch_down = patches[1]
    patch_on_collide_point = patches[2]

    mock_scroll_touch = Mock()
    mock_scroll_touch.button = "_".join(["scroll", FAKE.word()])
    mock_non_scroll_touch = Mock()
    mock_non_scroll_touch.button = FAKE.word()
    while "scroll" in mock_non_scroll_touch.button:
        mock_non_scroll_touch.button = FAKE.word()
    mock_scroll_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()
    mock_non_scroll_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()

    patch_on_collide_point.return_value = False
    focus_widget = FocusWidget()
    focus_widget.on_touch_down(mock_scroll_touch)
    patch_gain_focus.assert_not_called()
    patch_widget_on_touch_down.assert_called_once_with(mock_scroll_touch)
    patch_widget_on_touch_down.reset_mock()

    focus_widget.on_touch_down(mock_non_scroll_touch)
    patch_gain_focus.assert_not_called()
    patch_widget_on_touch_down.assert_called_once_with(mock_non_scroll_touch)
    patch_widget_on_touch_down.reset_mock()

    patch_on_collide_point.return_value = True
    focus_widget.on_touch_down(mock_scroll_touch)
    patch_gain_focus.assert_not_called()
    patch_widget_on_touch_down.assert_called_once_with(mock_scroll_touch)
    patch_widget_on_touch_down.reset_mock()

    # touch should not be consumed
    assert focus_widget.on_touch_down(mock_non_scroll_touch) is not True
    patch_gain_focus.assert_called_once()
    patch_widget_on_touch_down.assert_called_once_with(mock_non_scroll_touch)
    patch_gain_focus.reset_mock()
    patch_widget_on_touch_down.reset_mock()

    focus_widget.focus_on_scroll = True
    # touch should not be consumed
    assert focus_widget.on_touch_down(mock_scroll_touch) is not True
    patch_gain_focus.assert_called_once()
    patch_widget_on_touch_down.assert_called_once_with(mock_scroll_touch)
    patch_gain_focus.reset_mock()
    patch_widget_on_touch_down.reset_mock()

    # touch should not be consumed
    assert focus_widget.on_touch_down(mock_non_scroll_touch) is not True
    patch_gain_focus.assert_called_once()
    patch_widget_on_touch_down.assert_called_once_with(mock_non_scroll_touch)

    reset_focus_instances()


def test_gain_focus():
    focus_widget = FocusWidget()
    focus_widget.gain_focus()
    assert focus_widget.focus is True
    reset_focus_instances()


def test_lose_focus():
    focus_widget = FocusWidget(focus=True)
    focus_widget.lose_focus()
    assert focus_widget.focus is False
    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.set_focus_next")
def test_give_focus(patch_set_focus_next):
    focus_widget = FocusWidget()
    focus_widget.give_focus()
    patch_set_focus_next.assert_not_called()

    focus_widget.focus = True
    focus_widget.give_focus()
    patch_set_focus_next.assert_called_once()

    reset_focus_instances()


def test_change_focus_highlight_color():
    fw = FocusWidget()
    fw.change_focus_highlight_color()
    assert fw.highlight_color == fw.unfocused_highlight_color

    fw.focus = True
    fw.change_focus_highlight_color()
    assert fw.highlight_color == fw.focused_highlight_color

    reset_focus_instances()


def test__currently_focused_widget():
    focus_widget1 = FocusWidget()
    focus_widget2 = FocusWidget()

    focus_widget1.focus = True
    assert AbstractFocus._current_focused_widget == focus_widget1

    focus_widget1.focus = False
    focus_widget2.focus = True
    assert AbstractFocus._current_focused_widget == focus_widget2

    reset_focus_instances()
