from kivy.lang import Builder
from os.path import join
from src.ui.eventview import EventView


try:
    Builder.load_file(join("src", "ui", "eventview.kv"))
except FileNotFoundError:
    Builder.load_file(join("..", "..", "src", "ui", "eventview.kv"))


def test_focused_highlight_color():
    event_view = EventView(focus=True)
    assert event_view.focused_highlight_color[3] != 0  # not transparent
