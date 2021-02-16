from kivy.uix.widget import Widget
from src.ui.focusedhorscroll import HorScrollBehavior
from src.ui.keylisten import KeyListenBehavior
from tests.utils import FAKE
from unittest.mock import Mock, patch


class HorScrollWidget(HorScrollBehavior, KeyListenBehavior, Widget):
    pass


def test__scroll_by():
    scroll_widget = HorScrollWidget()
    assert scroll_widget._scroll_by != 0


@patch("kivy.uix.widget.Widget.on_touch_down")
@patch("kivy.uix.widget.Widget.collide_point")
def test_on_touch_down(mock_collide_point, mock_widget_on_touch_down):
    mock_touch = Mock()
    mock_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()

    scroll_widget = HorScrollWidget()
    scroll_widget.gain_focus = Mock()
    scroll_widget.cleanup_scroll = Mock()

    mock_widget_on_touch_down.return_value = True
    assert scroll_widget.on_touch_down(mock_touch) is True
    scroll_widget.gain_focus.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.assert_not_called()

    mock_widget_on_touch_down.return_value = False
    mock_collide_point.return_value = False
    assert scroll_widget.on_touch_down(mock_touch) is False
    assert scroll_widget.scroll_by == 0
    scroll_widget.gain_focus.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()

    mock_collide_point.return_value = True
    mock_touch.button = "scrollleft"
    assert scroll_widget.on_touch_down(mock_touch) is True
    assert scroll_widget.scroll_by == -scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    scroll_widget.scroll_by = 0  # reset
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()

    mock_touch.button = "scrollright"
    assert scroll_widget.on_touch_down(mock_touch) is True
    assert scroll_widget.scroll_by == scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    scroll_widget.scroll_by = 0  # reset
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()

    mock_touch.button = "scrolldown"
    assert scroll_widget.on_touch_down(mock_touch) is False
    assert scroll_widget.scroll_by == 0
    scroll_widget.gain_focus.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()

    scroll_widget.shift_key = True  # scroll down with shift
    assert scroll_widget.on_touch_down(mock_touch) is True
    assert scroll_widget.scroll_by == -scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    scroll_widget.scroll_by = 0  # reset
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()

    mock_touch.button = "scrollup"  # scroll up with shift
    assert scroll_widget.on_touch_down(mock_touch) is True
    assert scroll_widget.scroll_by == scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    scroll_widget.scroll_by = 0  # reset
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()

    scroll_widget.shift_key = False  # scroll up *without* shift
    assert scroll_widget.on_touch_down(mock_touch) is False
    assert scroll_widget.scroll_by == 0
    scroll_widget.gain_focus.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()


@patch("kivy.uix.widget.Widget.collide_point")
@patch("kivy.uix.widget.Widget.get_root_window")
@patch("kivy.uix.widget.Widget.on_touch_move")
def test_on_touch_move(*mocks):
    mock_widget_on_touch_move = mocks[0]
    mock_get_root_window = mocks[1]
    mock_window = Mock()
    mock_get_root_window.return_value = mock_window
    mock_collide_point = mocks[2]
    mock_touch = Mock()
    mock_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()

    scroll_widget = HorScrollWidget()
    mock_collide_point.return_value = False
    scroll_widget.disable_drag_hor_scroll = True
    mock_touch.dx = 0
    assert (
        scroll_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_touch.grab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    mock_widget_on_touch_move.reset_mock()

    mock_collide_point.return_value = True
    assert (
        scroll_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_touch.grab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    mock_widget_on_touch_move.reset_mock()

    mock_collide_point.return_value = False
    mock_touch.dx = FAKE.pyfloat(min_value=0)
    assert (
        scroll_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_touch.grab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    mock_widget_on_touch_move.reset_mock()

    scroll_widget.disable_drag_hor_scroll = True
    assert (
        scroll_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_touch.grab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    mock_widget_on_touch_move.reset_mock()

    mock_collide_point.return_value = True
    mock_touch.dx = FAKE.pyfloat(min_value=1)
    mock_touch.grab_current = scroll_widget
    scroll_widget.disable_drag_hor_scroll = False
    assert scroll_widget.on_touch_move(mock_touch) is True
    assert scroll_widget.scroll_by == mock_touch.dx
    assert scroll_widget.drag_hor_scrolling is False
    mock_touch.grab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    mock_widget_on_touch_move.assert_not_called()
    scroll_widget.scroll_by = 0  # reset

    mock_touch.grab_current = None
    assert scroll_widget.on_touch_move(mock_touch) is True
    assert scroll_widget.scroll_by == mock_touch.dx
    assert scroll_widget.drag_hor_scrolling is True
    mock_touch.grab.assert_called_once_with(scroll_widget)
    mock_window.set_system_cursor.assert_called_once_with("hand")
    mock_widget_on_touch_move.assert_not_called()


@patch("kivy.uix.widget.Widget.get_root_window")
@patch("kivy.uix.widget.Widget.on_touch_up")
def test_on_touch_up(mock_widget_on_touch_up, mock_get_root_window):
    mock_window = Mock()
    mock_get_root_window.return_value = mock_window
    mock_touch = Mock()

    scroll_widget = HorScrollWidget()
    scroll_widget.cleanup_scroll = Mock()
    assert (
        scroll_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    mock_touch.grab_current = scroll_widget
    assert (
        scroll_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    mock_touch.grab_current = None
    scroll_widget.drag_hor_scrolling = True
    assert (
        scroll_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_window.set_system_cursor.assert_not_called()
    scroll_widget.cleanup_scroll.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    mock_touch.grab_current = scroll_widget
    assert (
        scroll_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_called_once_with(scroll_widget)
    mock_window.set_system_cursor.assert_called_once_with("arrow")
    scroll_widget.cleanup_scroll.assert_called_once()


@patch("src.ui.focusedhorscroll.HorScrollBehavior.is_left_key")
@patch("src.ui.focusedhorscroll.HorScrollBehavior.is_right_key")
@patch("src.ui.keylisten.KeyListenBehavior.on_keyboard_down")
def test_on_keyboard_down(*mocks):
    mock_keylisten_on_keyboard_down = mocks[0]
    mock_is_right_key = mocks[1]
    mock_is_right_key.return_value = False
    mock_is_left_key = mocks[2]
    mock_is_left_key.return_value = False

    mock_kb = Mock()
    fake_keycode = FAKE.random_int(), FAKE.sentence()
    text = FAKE.word()
    mods = FAKE.pylist()

    scroll_widget = HorScrollWidget()
    assert scroll_widget.on_keyboard_down(mock_kb, (304, "shift"), text, mods)
    assert scroll_widget.shift_key is True
    mock_keylisten_on_keyboard_down.assert_not_called()
    scroll_widget.shift_key = False  # reset

    assert scroll_widget.on_keyboard_down(mock_kb, (303, "rshift"), text, mods)
    assert scroll_widget.shift_key is True
    mock_keylisten_on_keyboard_down.assert_not_called()

    scroll_widget.cleanup_scroll = Mock()
    scroll_widget.gain_focus = Mock()
    mock_is_left_key.return_value = True
    assert scroll_widget.on_keyboard_down(mock_kb, fake_keycode, text, mods)
    assert scroll_widget.left_key is True
    assert scroll_widget.scroll_by == -scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    mock_keylisten_on_keyboard_down.assert_not_called()
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()
    scroll_widget.scroll_by = 0  # reset

    mock_is_left_key.return_value = False
    mock_is_right_key.return_value = True
    assert scroll_widget.on_keyboard_down(mock_kb, fake_keycode, text, mods)
    assert scroll_widget.right_key is True
    assert scroll_widget.scroll_by == scroll_widget._scroll_by
    scroll_widget.gain_focus.assert_called_once()
    scroll_widget.cleanup_scroll.assert_called_once()
    mock_keylisten_on_keyboard_down.assert_not_called()
    scroll_widget.gain_focus.reset_mock()
    scroll_widget.cleanup_scroll.reset_mock()
    scroll_widget.scroll_by = 0  # reset

    mock_is_right_key.return_value = False
    assert (
        scroll_widget.on_keyboard_down(mock_kb, fake_keycode, text, mods)
        == mock_keylisten_on_keyboard_down.return_value
    )
    assert scroll_widget.scroll_by == 0
    scroll_widget.gain_focus.assert_not_called()


@patch("src.ui.focusedhorscroll.HorScrollBehavior.is_left_key")
@patch("src.ui.focusedhorscroll.HorScrollBehavior.is_right_key")
@patch("src.ui.keylisten.KeyListenBehavior.on_keyboard_up")
def test_on_keyboard_up(*mocks):
    mock_keylisten_on_keyboard_down = mocks[0]
    mock_is_right_key = mocks[1]
    mock_is_right_key.return_value = False
    mock_is_left_key = mocks[2]
    mock_is_left_key.return_value = False
    mock_kb = Mock()

    scroll_widget = HorScrollWidget()
    scroll_widget.shift_key = True
    keycode = (304, "shift")
    assert (
        scroll_widget.on_keyboard_up(mock_kb, keycode)
        == mock_keylisten_on_keyboard_down.return_value
    )
    assert not scroll_widget.shift_key
    mock_keylisten_on_keyboard_down.assert_called_with(mock_kb, keycode)

    scroll_widget.shift_key = True
    keycode = (303, "rshift")
    assert (
        scroll_widget.on_keyboard_up(mock_kb, keycode)
        == mock_keylisten_on_keyboard_down.return_value
    )
    assert not scroll_widget.shift_key
    mock_keylisten_on_keyboard_down.assert_called_with(mock_kb, keycode)

    fake_keycode = FAKE.pyfloat(), FAKE.sentence()
    scroll_widget.left_key = True
    mock_is_left_key.return_value = True
    assert (
        scroll_widget.on_keyboard_up(mock_kb, fake_keycode)
        == mock_keylisten_on_keyboard_down.return_value
    )
    assert not scroll_widget.left_key
    mock_keylisten_on_keyboard_down.assert_called_with(mock_kb, fake_keycode)

    scroll_widget.left_key = mock_is_left_key.return_value = False
    scroll_widget.right_key = True
    mock_is_right_key.return_value = True
    assert (
        scroll_widget.on_keyboard_up(mock_kb, fake_keycode)
        == mock_keylisten_on_keyboard_down.return_value
    )
    assert not scroll_widget.right_key
    mock_keylisten_on_keyboard_down.assert_called_with(mock_kb, fake_keycode)


def test_is_left_key():
    hor_scroll = HorScrollBehavior()
    numpad_modifier = FAKE.pylist()
    numpad_modifier.append("numlock")
    fake_key = FAKE.word()
    while fake_key in ("left", "numpad4"):
        fake_key = FAKE.word()

    assert hor_scroll.is_left_key([276, "left"], FAKE.pylist())
    assert hor_scroll.is_left_key([260, "numpad4"], numpad_modifier)
    assert hor_scroll.is_left_key([276, "left"])
    assert hor_scroll.is_left_key([260, "numpad4"])
    assert not hor_scroll.is_left_key([FAKE.random_int(), fake_key])
    assert not hor_scroll.is_left_key([260, "numpad4"], [])


def test_is_right_key():
    hor_scroll = HorScrollBehavior()
    numpad_modifier = FAKE.pylist()
    numpad_modifier.append("numlock")
    fake_key = FAKE.word()
    while fake_key in ("right", "numpad6"):
        fake_key = FAKE.word()

    assert hor_scroll.is_right_key([275, "right"], FAKE.pylist())
    assert hor_scroll.is_right_key([262, "numpad6"], numpad_modifier)
    assert hor_scroll.is_right_key([275, "right"])
    assert hor_scroll.is_right_key([262, "numpad6"])
    assert not hor_scroll.is_right_key([FAKE.random_int(), fake_key])
    assert not hor_scroll.is_right_key([262, "numpad6"], [])


def test_cleanup_scroll():
    scroll_widget = HorScrollWidget()
    scroll_widget.drag_hor_scrolling = True
    scroll_widget.scroll_by = FAKE.random_int(min=1)

    scroll_widget.cleanup_scroll()
    assert not scroll_widget.drag_hor_scrolling
    assert scroll_widget.scroll_by == 0
