from kivy.lang import Builder
from os.path import join
from src.ui.markbar import MarkBar
from tests.test_ui.utils import reset_focus_instances
from unittest.mock import Mock

try:
    Builder.load_file(join("src", "ui", "markbar.kv"))
except FileNotFoundError:
    Builder.load_file(join("..", "..", "src", "ui", "markbar.kv"))


def test_markbar_focused_highlight_color():
    mark_bar = MarkBar(keyboard_listener=Mock())
    assert mark_bar.focused_highlight_color[3] != 0  # not transparent

    reset_focus_instances()
