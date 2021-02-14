from kivy.lang import Builder
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.widget import Widget
from os.path import join
from src.ui.imagebutton import (
    ChangeButtonBgColor,
    HoverChangeBgColor,
    HoverImageButton,
    HoverImageToggleButton,
)
from tests.test_ui.utils import reset_focus_instances
from tests.utils import FAKE
from unittest.mock import Mock, patch


try:
    Builder.load_file(join("src", "ui", "imagebutton.kv"))
except FileNotFoundError:
    Builder.load_file(join("..", "..", "src", "ui", "imagebutton.kv"))


#
# ChangeButtonBgColor
#
class ChangeBgColorWidget(ChangeButtonBgColor, ButtonBehavior, Widget):
    pass


@patch("src.ui.imagebutton.ChangeButtonBgColor.change_color")
def test_changebgcolor_on_state(mock_change_color):
    widget = ChangeBgColorWidget()
    widget.state = "down"
    mock_change_color.assert_called_once()


def test_changebgcolor_change_color():
    widget = ChangeBgColorWidget()
    widget.state = "normal"
    widget.change_color()
    assert widget.current_color == widget.normal_color

    widget.state = "down"
    widget.change_color()
    assert widget.current_color == widget.down_color


#
# HoverChangeBgColor
#
class HoverChangeWidget(
    HoverChangeBgColor,
    ChangeButtonBgColor,
    ButtonBehavior,
    Widget,
):
    pass


@patch("src.ui.imagebutton.HoverChangeBgColor.change_color")
def test_hoverchange_change_color_binding(mock_change_color):
    widget = HoverChangeWidget()
    widget.hovered = True
    widget.focus = True
    assert mock_change_color.call_count == 2
    reset_focus_instances()


@patch("src.ui.imagebutton.ChangeButtonBgColor.change_color")
def test_hoverchange_change_color(mock_super_change_color):
    widget = HoverChangeWidget()

    mock_super_change_color.reset_mock()
    widget.change_color()
    assert widget.current_color != widget.hover_color
    mock_super_change_color.assert_called_once()
    mock_super_change_color.reset_mock()

    widget.hovered = True
    widget.change_color()
    assert widget.current_color == widget.hover_color
    mock_super_change_color.assert_called()
    mock_super_change_color.reset_mock()
    widget.hovered = False
    widget.current_color = widget.normal_color

    widget.focus = True
    widget.change_color()
    assert widget.current_color == widget.hover_color
    mock_super_change_color.assert_called()
    mock_super_change_color.reset_mock()
    widget.current_color = widget.normal_color

    widget.state = "down"
    widget.change_color()
    assert widget.current_color != widget.hover_color
    mock_super_change_color.assert_called()
    mock_super_change_color.reset_mock()

    widget.focus = False
    widget.hovered = True
    widget.change_color()
    assert widget.current_color != widget.hover_color
    mock_super_change_color.assert_called()
    mock_super_change_color.reset_mock()

    reset_focus_instances()


@patch("kivy.uix.behaviors.button.ButtonBehavior.on_press")
@patch("src.ui.focusedkeylisten.FocusKeyListenBehavior.on_keyboard_down")
def test_hoverchange_on_keyboard_down(mock_on_keyboard_down, mock_on_press):
    kb = Mock()
    fake_keycode = FAKE.pylist(nb_elements=2)
    text = Mock()
    mods = Mock()

    hcw = HoverChangeWidget()
    hcw.on_keyboard_down(kb, fake_keycode, text, mods)
    mock_on_press.assert_not_called()
    mock_on_keyboard_down.assert_called_with(kb, fake_keycode, text, mods)
    mock_on_keyboard_down.reset_mock()

    assert hcw.on_keyboard_down(kb, (13, "enter"), text, mods) is True
    mock_on_press.assert_called_once()
    mock_on_keyboard_down.assert_not_called()
    mock_on_press.reset_mock()
    mock_on_keyboard_down.reset_mock()

    assert hcw.on_keyboard_down(kb, (271, "numpadenter"), text, mods) is True
    mock_on_press.assert_called_once()
    mock_on_keyboard_down.assert_not_called()

    reset_focus_instances()


@patch("kivy.uix.widget.Widget.collide_point")
def test_hoverchange_on_mouse_pos(mock_collide_point):
    mock_window = Mock()
    mouse_pos = FAKE.pyfloat(), FAKE.pyfloat()
    mock_collide_point.return_value = False

    widget = HoverChangeWidget()
    assert widget.on_mouse_pos(mock_window, mouse_pos) is False
    assert widget.hovered is False

    mock_collide_point.return_value = True
    assert widget.on_mouse_pos(mock_window, mouse_pos) is True
    assert widget.hovered is True

    reset_focus_instances()


def test_hoverchange_focused_highlight_color():
    widget = HoverChangeWidget()
    assert widget.focused_highlight_color[3] != 0  # not transparent
    reset_focus_instances()


# skip ImageLayout tests

#
# HoverImageButtons
#
@patch("kivy.app.App.get_running_app", return_value=Mock())
def test_hoverimagebutton_on_press(mock_get_running_app):
    app = mock_get_running_app()
    app.popup.open = Mock()

    hover_image_button = HoverImageButton()
    hover_image_button.on_press()
    app.popup.open.assert_called_once()

    reset_focus_instances()


@patch("kivy.app.App.get_running_app", return_value=Mock())
def test_hoverimagetogglebutton_on_press(mock_get_running_app):
    app = mock_get_running_app()
    app.popup.open = Mock()

    hover_image_toggle_button = HoverImageToggleButton()
    hover_image_toggle_button.on_press()
    app.popup.open.assert_called_once()
    app.popup.open.reset_mock()

    hover_image_toggle_button.state = "down"
    hover_image_toggle_button.on_press()
    app.popup.open.assert_not_called()

    reset_focus_instances()
