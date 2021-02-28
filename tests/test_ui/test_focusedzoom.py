from kivy.uix.widget import Widget
from src.ui.focusedzoom import ZoomBehavior
from src.ui.keylisten import KeyListenBehavior
from tests.utils import FAKE
from unittest.mock import Mock, patch


class ZoomWidget(ZoomBehavior, KeyListenBehavior, Widget):
    pass


def test__zoom_by():
    zoom = ZoomBehavior()
    assert zoom._zoom_by != 0


@patch("kivy.uix.widget.Widget.on_touch_down")
@patch("kivy.uix.widget.Widget.collide_point")
def test_on_touch_down(mock_collide_point, mock_widget_on_touch_down):
    zoom_widget = ZoomWidget()
    zoom_widget.gain_focus = Mock()
    mock_touch = Mock()
    mock_widget_on_touch_down.return_value = True
    assert zoom_widget.on_touch_down(mock_touch)
    assert mock_touch not in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_not_called()

    mock_widget_on_touch_down.return_value = False
    mock_collide_point.return_value = False
    mock_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()
    assert not zoom_widget.on_touch_down(mock_touch)
    assert mock_touch not in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_not_called()

    mock_collide_point.return_value = True
    mock_touch.button = "scrollup"
    assert zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == zoom_widget._zoom_by
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_called_once()
    zoom_widget.gain_focus.reset_mock()

    zoom_widget.disable_zoom_in = True
    assert not zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_not_called()

    mock_touch.button = "scrolldown"
    assert zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == -zoom_widget._zoom_by
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_called_once()
    zoom_widget.gain_focus.reset_mock()

    zoom_widget.disable_zoom_out = True
    assert not zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_not_called()

    zoom_widget.touches = [Mock()]  # doesn't zoom when scrolling
    assert not zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert len(zoom_widget.touches) == 2
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()
    zoom_widget.gain_focus.assert_not_called()

    mock_touch.button = Mock()
    mock_touch.button.startswith.return_value = False
    zoom_widget.touches = [Mock()]
    assert zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert len(zoom_widget.touches) == 2
    assert zoom_widget.pinch_zooming
    # don't test _zoom_by
    mock_touch.grab.assert_called_once_with(zoom_widget)
    mock_touch.grab.reset_mock()
    zoom_widget.pinch_zooming = False  # reset

    # doesn't pinch zoom with >2 touches
    assert not zoom_widget.on_touch_down(mock_touch)
    assert mock_touch in zoom_widget.touches
    assert not zoom_widget.pinch_zooming
    assert zoom_widget.zoom_by == 0
    mock_touch.grab.assert_not_called()


@patch("kivy.uix.widget.Widget.on_touch_move")
def test_on_touch_move(mock_widget_on_touch_move):
    mock_touch = Mock()
    zoom_widget = ZoomWidget()

    assert (
        zoom_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_widget_on_touch_move.reset_mock()

    mock_touch.grab_current = zoom_widget
    assert (
        zoom_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_widget_on_touch_move.reset_mock()

    mock_touch.grab_current = None
    zoom_widget.pinch_zooming = True
    assert (
        zoom_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_widget_on_touch_move.reset_mock()

    mock_touch.grab_current = zoom_widget
    mock_touch.ppos = FAKE.pyfloat(min_value=0), FAKE.pyfloat(min_value=0)
    mock_touch.pos = mock_touch.ppos
    mock_anchor = Mock()
    mock_anchor.pos = 0, 0
    zoom_widget.touches = [mock_anchor, mock_touch]
    assert (
        zoom_widget.on_touch_move(mock_touch)
        == mock_widget_on_touch_move.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_widget_on_touch_move.assert_called_once_with(mock_touch)
    mock_widget_on_touch_move.reset_mock()

    mock_touch.ppos = FAKE.pyfloat(min_value=1), FAKE.pyfloat(min_value=1)
    dpixels = FAKE.pyfloat(min_value=1, max_value=int(max(*mock_touch.ppos)))
    mock_touch.pos = mock_touch.ppos[0] + dpixels, mock_touch.ppos[1] + dpixels
    assert zoom_widget.on_touch_move(mock_touch) is True
    assert zoom_widget.zoom_by == -zoom_widget._zoom_by
    mock_widget_on_touch_move.assert_not_called()

    mock_touch.pos = mock_touch.ppos[0] - dpixels, mock_touch.ppos[1] - dpixels
    assert zoom_widget.on_touch_move(mock_touch) is True
    assert zoom_widget.zoom_by == zoom_widget._zoom_by
    mock_widget_on_touch_move.assert_not_called()


@patch("kivy.uix.widget.Widget.on_touch_up")
def test_on_touch_up(mock_widget_on_touch_up):
    zoom_widget = ZoomWidget()
    mock_touch = Mock()
    assert (
        zoom_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    zoom_widget.touches.append(mock_touch)
    assert (
        zoom_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    assert mock_touch not in zoom_widget.touches
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    zoom_widget.touches.append(mock_touch)
    mock_touch.grab_current = zoom_widget
    assert (
        zoom_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    assert mock_touch not in zoom_widget.touches
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    zoom_widget.touches.append(mock_touch)
    mock_touch.grab_current = None
    zoom_widget.pinch_zooming = True
    assert (
        zoom_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    assert mock_touch not in zoom_widget.touches
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_not_called()
    mock_widget_on_touch_up.reset_mock()

    zoom_widget.touches.append(mock_touch)
    mock_touch.grab_current = zoom_widget
    assert (
        zoom_widget.on_touch_up(mock_touch)
        == mock_widget_on_touch_up.return_value
    )
    assert mock_touch not in zoom_widget.touches
    mock_widget_on_touch_up.assert_called_once_with(mock_touch)
    mock_touch.ungrab.assert_called_with(zoom_widget)


@patch("src.ui.keylisten.KeyListenBehavior.on_keyboard_down")
def test_on_keyboard_down(mock_kl_on_keyboard_down):
    zoom_widget = ZoomWidget()
    mock_kb = Mock()
    fake_keycode = FAKE.random_int(), FAKE.word()
    text = FAKE.sentence()
    mods = FAKE.pylist()
    assert (
        zoom_widget.on_keyboard_down(mock_kb, fake_keycode, text, mods)
        == mock_kl_on_keyboard_down.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_kl_on_keyboard_down.assert_called_once_with(
        mock_kb, fake_keycode, text, mods
    )
    mock_kl_on_keyboard_down.reset_mock()

    mods.append("ctrl")
    assert (
        zoom_widget.on_keyboard_down(mock_kb, (270, "numpadadd"), text, mods)
        is True
    )
    assert zoom_widget.zoom_by == zoom_widget._zoom_by
    mock_kl_on_keyboard_down.assert_not_called()

    mods.append("shift")
    assert zoom_widget.on_keyboard_down(mock_kb, (61, "="), text, mods) is True
    assert zoom_widget.zoom_by == zoom_widget._zoom_by
    mock_kl_on_keyboard_down.assert_not_called()

    assert (
        zoom_widget.on_keyboard_down(
            mock_kb, (269, "numpadsubstract"), text, mods
        )
        is True
    )
    assert zoom_widget.zoom_by == -zoom_widget._zoom_by
    mock_kl_on_keyboard_down.assert_not_called()

    assert (  # ctrl + shift  + - should not zoom
        zoom_widget.on_keyboard_down(mock_kb, (45, "-"), text, mods)
        == mock_kl_on_keyboard_down.return_value
    )
    assert zoom_widget.zoom_by == 0
    mock_kl_on_keyboard_down.assert_called_once_with(
        mock_kb, (45, "-"), text, mods
    )
    mock_kl_on_keyboard_down.reset_mock()

    mods.remove("shift")
    assert zoom_widget.on_keyboard_down(mock_kb, (45, "-"), text, mods) is True
    assert zoom_widget.zoom_by == -zoom_widget._zoom_by
    mock_kl_on_keyboard_down.assert_not_called()
