import src.main

from kivy.lang import Builder
from os.path import join
from src.main import JulianBC
from unittest.mock import patch


def test_julianbc_popup():
    julian_bc = JulianBC()
    assert julian_bc.popup
    assert "not implemented" in julian_bc.popup.children[0].text.lower()


def test_julianbc_build():  # todo os.walk
    julian_bc = JulianBC()
    main_kv_path = join("..", "..", "src", "main.kv")
    try:
        assert (
            julian_bc.build().__class__
            == Builder.load_file(main_kv_path).__class__
        )
    except FileNotFoundError:
        main_kv_path = join("src", "main.kv")
        assert (
            julian_bc.build().__class__
            == Builder.load_file(main_kv_path).__class__
        )


@patch.object(src.main, "__name__", "")
@patch.object(JulianBC, "run")
def test_main_func(mock_run):
    src.main.main()
    mock_run.assert_not_called()

    src.main.__name__ = "__main__"
    src.main.main()
    mock_run.assert_called_once()
