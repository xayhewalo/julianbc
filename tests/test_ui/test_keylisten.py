from kivy.core.window import Keyboard
from kivy.uix.widget import Widget
from src.ui.keylisten import KeyListenBehavior
from unittest.mock import Mock, patch


class KeyListenWidget(KeyListenBehavior, Widget):
    pass


@patch("kivy.core.window.Keyboard.bind")
def test_request_keyboard(mock_keyboard_bind):
    key_listen_widget = KeyListenWidget()
    key_listen_widget.request_keyboard()
    assert isinstance(key_listen_widget.keyboard, Keyboard)
    mock_keyboard_bind.assert_called_with(
        on_key_down=key_listen_widget.on_keyboard_down,
        on_key_up=key_listen_widget.on_keyboard_up,
    )


@patch("kivy.core.window.Keyboard.unbind")
def test_keyboard_closed(mock_keyboard_unbind):
    key_listen_widget = KeyListenWidget()
    key_listen_widget.keyboard = Keyboard()
    key_listen_widget.keyboard_closed()
    assert key_listen_widget.keyboard is None
    mock_keyboard_unbind.assert_called_with(
        on_key_down=key_listen_widget.on_keyboard_down
    )


def test_on_keyboard_down():
    key_listen_widget = KeyListenWidget()
    # noinspection PyBroadException
    try:
        key_listen_widget.on_keyboard_down(Mock(), Mock(), Mock(), Mock())
    except Exception:
        assert False, "on_keyboard_down raised an unexpected error"


def test_on_keyboard_up():
    key_listen_widget = KeyListenWidget()
    # noinspection PyBroadException
    try:
        key_listen_widget.on_keyboard_up(Mock(), Mock())
    except Exception:
        assert False, "on_keyboard_up raised an unexpected error"
