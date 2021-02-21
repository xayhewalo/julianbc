import src.main

from kivy.lang import Builder
from os.path import join, split
from src.main import JulianBC
from unittest.mock import patch


def test_julianbc_popup():
    julian_bc = JulianBC()
    assert julian_bc.popup
    assert "not implemented" in julian_bc.popup.children[0].text.lower()


def test_julianbc_build():
    julian_bc = JulianBC()
    abs_src_path = split(src.main.__file__)[0]
    assert (
        julian_bc.build().__class__
        == Builder.load_file(join(abs_src_path, "main.kv")).__class__
    )


@patch.object(src.main, "__name__", "")
@patch.object(JulianBC, "run")
def test_main_func(mock_run):
    src.main.main()
    mock_run.assert_not_called()

    src.main.__name__ = "__main__"
    src.main.main()
    mock_run.assert_called_once()
