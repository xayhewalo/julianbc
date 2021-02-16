from src.ui.mouselisten import MouseListenBehavior
from tests.utils import FAKE
from unittest.mock import Mock, patch


@patch("kivy.core.window.Window.bind")
def test_mouse_pos_binding(mock_window_bind):
    mouse_listen = MouseListenBehavior()
    mock_window_bind.assert_called_with(mouse_pos=mouse_listen.on_mouse_pos)


def test_mouse_pos():
    mouse_listen = MouseListenBehavior()
    mock_win = Mock()
    mouse_pos = FAKE.pyfloat(), FAKE.pyfloat()

    mouse_listen.disabled = True
    assert mouse_listen.on_mouse_pos(mock_win, mouse_pos) is True

    mouse_listen.disabled = False
    mouse_listen.children = []
    assert mouse_listen.on_mouse_pos(mock_win, mouse_pos) is not True

    for _ in range(FAKE.random_int(min=1, max=10)):
        mock_child = Mock()
        mock_child.dispatch.return_value = False
        mouse_listen.children.append(mock_child)
    assert mouse_listen.on_mouse_pos(mock_win, mouse_pos) is not True
    for child in mouse_listen.children:
        child.dispatch.assert_called_with("on_mouse_pos", mock_win, mouse_pos)
        child.dispatch.reset_mock()

    # stop propagating events if a child returns true
    consumed_mouse_widget = FAKE.random_element(elements=mouse_listen.children)
    consumed_mouse_widget.dispatch.return_value = True
    consuming_widget_idx = mouse_listen.children.index(consumed_mouse_widget)
    mouse_listen.on_mouse_pos(mock_win, mouse_pos)
    for child in mouse_listen.children[: consuming_widget_idx + 1]:
        child.dispatch.assert_called_with("on_mouse_pos", mock_win, mouse_pos)
    # fmt:off
    for child in mouse_listen.children[consuming_widget_idx + 1:]:
        # fmt: on
        child.dispatch.assert_not_called()
