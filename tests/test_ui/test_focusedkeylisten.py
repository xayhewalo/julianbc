from kivy.uix.widget import Widget
from src.ui.focusedkeylisten import (
    FocusKeyListenBehavior,
    PassiveFocusBehavior,
)
from tests.test_ui.utils import reset_focus_instances
from tests.utils import FAKE
from unittest.mock import Mock, patch


class FocusKeyListenWidget(FocusKeyListenBehavior, Widget):
    pass


@patch("src.ui.keylisten.KeyListenBehavior.request_keyboard")
def test_focuskeylisten_on_focus(mock_request_keyboard):
    fkl_widget = FocusKeyListenWidget()
    mock_request_keyboard.reset_mock()
    fkl_widget.focus = True
    mock_request_keyboard.assert_called()

    reset_focus_instances()


@patch("src.ui.keylisten.KeyListenBehavior.on_keyboard_down")
@patch("src.ui.focusedkeylisten.FocusKeyListenBehavior.set_focus_previous")
@patch("src.ui.focusedkeylisten.FocusKeyListenBehavior.set_focus_next")
def test_focuskeylisten_on_keyboard_down(*mocks):
    mock_set_focus_next = mocks[0]
    mock_set_focus_previous = mocks[1]
    mock_kl_on_keyboard_down = mocks[2]

    fkl_widget = FocusKeyListenWidget()
    mock_kb = Mock()
    text = FAKE.word()
    fake_mods = FAKE.pylist(value_types=[int, float])
    fake_keycode = FAKE.pylist(nb_elements=2, variable_nb_elements=False)

    assert (
        fkl_widget.on_keyboard_down(mock_kb, fake_keycode, text, fake_mods)
        == mock_kl_on_keyboard_down.return_value
    )
    mock_kl_on_keyboard_down.assert_called_once()
    mock_set_focus_next.assert_not_called()
    mock_set_focus_previous.assert_not_called()
    mock_kl_on_keyboard_down.reset_mock()

    passive_listener = Mock()
    passive_listener.on_keyboard_down.return_value = False
    fkl_widget.passive_listener = passive_listener
    assert (
        fkl_widget.on_keyboard_down(mock_kb, fake_keycode, text, fake_mods)
        == mock_kl_on_keyboard_down.return_value
    )
    mock_kl_on_keyboard_down.assert_called_once()
    mock_set_focus_next.assert_not_called()
    mock_set_focus_previous.assert_not_called()
    passive_listener.on_keyboard_down.assert_called_once_with(
        mock_kb, fake_keycode, text, fake_mods
    )
    mock_kl_on_keyboard_down.reset_mock()
    passive_listener.on_keyboard_down.reset_mock()

    passive_listener.on_keyboard_down.return_value = True
    assert fkl_widget.on_keyboard_down(mock_kb, fake_keycode, text, fake_mods)
    mock_kl_on_keyboard_down.assert_not_called()
    mock_set_focus_previous.assert_not_called()
    passive_listener.on_keyboard_down.assert_called_once_with(
        mock_kb, fake_keycode, text, fake_mods
    )
    passive_listener.on_keyboard_down.reset_mock()

    assert fkl_widget.on_keyboard_down(mock_kb, (9, "tab"), text, fake_mods)
    mock_set_focus_next.assert_called_once()
    mock_set_focus_previous.assert_not_called()
    passive_listener.on_keyboard_down.assert_not_called()
    mock_kl_on_keyboard_down.assert_not_called()
    mock_set_focus_next.reset_mock()

    shift_mods = FAKE.pylist()
    shift_mods.append("shift")
    assert fkl_widget.on_keyboard_down(mock_kb, (9, "tab"), text, shift_mods)
    mock_set_focus_previous.assert_called_once()
    mock_set_focus_next.assert_not_called()
    mock_kl_on_keyboard_down.assert_not_called()

    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.lose_focus")
@patch("src.ui.keylisten.KeyListenBehavior.on_keyboard_up")
def test_focuskeylisten_on_keyboard_up(*mocks):
    mock_kl_on_keyboard_up = mocks[0]
    mock_lose_focus = mocks[1]

    mock_kb = Mock()
    fake_keycode = FAKE.pylist()
    passive_listener = Mock()

    fkl_widget = FocusKeyListenWidget()
    assert (
        fkl_widget.on_keyboard_up(mock_kb, fake_keycode)
        == mock_kl_on_keyboard_up.return_value
    )
    mock_kl_on_keyboard_up.assert_called_once_with(mock_kb, fake_keycode)
    mock_lose_focus.assert_not_called()
    passive_listener.on_keyboard_up.assert_not_called()
    mock_kl_on_keyboard_up.reset_mock()

    fkl_widget.passive_listener = passive_listener
    assert fkl_widget.on_keyboard_up(mock_kb, fake_keycode)
    mock_kl_on_keyboard_up.assert_not_called()
    mock_lose_focus.assert_not_called()
    passive_listener.on_keyboard_up.assert_called_with(mock_kb, fake_keycode)
    passive_listener.on_keyboard_up.reset_mock()
    mock_kl_on_keyboard_up.reset_mock()

    passive_listener.on_keyboard_up.return_value = False
    fkl_widget.passive_listener = passive_listener
    assert fkl_widget.on_keyboard_up(mock_kb, fake_keycode)
    mock_kl_on_keyboard_up.assert_called_once_with(mock_kb, fake_keycode)
    mock_lose_focus.assert_not_called()
    passive_listener.on_keyboard_up.assert_called_with(mock_kb, fake_keycode)
    passive_listener.on_keyboard_up.reset_mock()
    mock_kl_on_keyboard_up.reset_mock()

    assert fkl_widget.on_keyboard_up(mock_kb, (27, "escape"))
    mock_kl_on_keyboard_up.assert_not_called()
    mock_lose_focus.assert_called()
    passive_listener.on_keyboard_up.assert_not_called()

    reset_focus_instances()


class PassiveFocusWidget(PassiveFocusBehavior, Widget):
    pass


def test_passivefocuswidget_on_focus_next():
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=Mock())
    passive_focus_widget.set_focus_next_and_previous = Mock()
    passive_focus_widget.focus_next = Mock()
    passive_focus_widget.set_focus_next_and_previous.assert_called_once()

    reset_focus_instances()


def test_passivefocuswidget_on_focus_previous():
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=Mock())
    passive_focus_widget.set_focus_next_and_previous = Mock()
    passive_focus_widget.focus_previous = Mock()
    passive_focus_widget.set_focus_next_and_previous.assert_called_once()

    reset_focus_instances()


@patch("src.ui.focusedkeylisten.PassiveFocusBehavior.bind_keyboard_listener")
def test_passivefocuswidget_on_keyboard_listener(mock_bind_keyboard_listener):
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=Mock())
    passive_focus_widget.keyboard_listener = Mock()
    mock_bind_keyboard_listener.assert_called()

    reset_focus_instances()


def test_passivefocuswidget_bind_keyboard_listener():
    kb_listener = Mock()
    pf_widget = PassiveFocusWidget(keyboard_listener=kb_listener)
    pf_widget.bind_keyboard_listener()
    kb_listener.bind.assert_called_once_with(keyboard=pf_widget.reset_listener)

    reset_focus_instances()


def test_passivefocuswidget_reset_listener():
    kb_listener = Mock()
    kb_listener.focus_next = None
    kb_listener.focus_previous = None
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=kb_listener)

    passive_focus_widget.reset_listener()
    assert kb_listener.focus_next is None
    assert kb_listener.focus_previous is None

    kb_listener.keyboard = None
    passive_focus_widget.reset_listener()
    assert kb_listener.focus_next == kb_listener.default_focus_next
    assert kb_listener.focus_previous == kb_listener.default_focus_previous

    reset_focus_instances()


def test_passivefocuswidget_set_passive_listener():
    kb_listener = Mock()
    kb_listener.passive_listener = None
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=kb_listener)
    passive_focus_widget.set_passive_listener()
    assert kb_listener.passive_listener is None

    passive_focus_widget.focus = True
    passive_focus_widget.set_passive_listener()
    assert kb_listener.passive_listener == passive_focus_widget

    reset_focus_instances()


@patch("src.ui.focus.AbstractFocus.on_focus")
def test_passivefocuswidget_on_focus(mock_on_focus):
    passive_focus_widget = PassiveFocusWidget()
    passive_focus_widget.set_focus_next_and_previous = Mock()
    passive_focus_widget.set_passive_listener = Mock()

    passive_focus_widget.focus = True
    passive_focus_widget.set_focus_next_and_previous.assert_called_once()
    passive_focus_widget.set_passive_listener.assert_called_once()
    mock_on_focus.assert_called_once()

    reset_focus_instances()


def test_passivefocuswidget_focus_next_and_previous():
    kb_listener = Mock()
    passive_focus_widget = PassiveFocusWidget(keyboard_listener=kb_listener)
    passive_focus_widget.set_focus_next_and_previous()
    assert kb_listener.focus_next != passive_focus_widget.focus_next
    assert kb_listener.focus_previous != passive_focus_widget.focus_previous
    kb_listener.request_keyboard.assert_not_called()

    passive_focus_widget.focus = True
    passive_focus_widget.set_focus_next_and_previous()
    assert kb_listener.focus_next == passive_focus_widget.focus_next
    assert kb_listener.focus_previous == passive_focus_widget.focus_previous
    kb_listener.request_keyboard.assert_called()

    reset_focus_instances()
