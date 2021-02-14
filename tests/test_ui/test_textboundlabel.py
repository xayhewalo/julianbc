import os

from kivy.lang import Builder
from src.ui.textboundlabel import TextBoundLabel
from tests.utils import FAKE

Builder.load_file(os.path.join("src", "ui", "textboundlabel.kv"))


def test_textboundlabel_size():
    tbl = TextBoundLabel(text=FAKE.sentence(), font_size=FAKE.random_int())
    tbl.texture_update()
    assert tbl.size == tbl.texture_size
