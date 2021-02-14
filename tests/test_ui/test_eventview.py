from kivy.lang import Builder
from os.path import join
from src.ui.eventview import EventView
from unittest.mock import patch


try:
    Builder.load_file(join("src", "ui", "eventview.kv"))
except FileNotFoundError:
    Builder.load_file(join("..", "..", "src", "ui", "eventview.kv"))


@patch("src.ui.focusedkeylisten.PassiveFocusBehavior.keyboard_listener")
def test_focused_highlight_color(mock_keyboard_listener):
    event_view = EventView(focus=True)
    assert event_view.focused_highlight_color[3] != 0  # not transparent
