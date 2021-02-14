from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.widget import Widget
from os.path import join
from src.ui.collapse import CollapseBar, CollapseBehavior
from src.ui.textboundlabel import TextBoundLabel
from tests.utils import FAKE
from unittest.mock import Mock, patch

try:
    Builder.load_file(join("src", "ui", "collapse.kv"))
    Builder.load_file(join("src", "ui", "textboundlabel.kv"))
except FileNotFoundError:
    Builder.load_file(join("..", "..", "src", "ui", "collapse.kv"))
    Builder.load_file(join("..", "..", "src", "ui", "textboundlabel.kv"))
Factory.register("TextBoundLabel", TextBoundLabel)


class CollapseWidget(CollapseBehavior, Widget):
    pass


#
# CollapseBehavior
#
def test__get_collapsed_y():
    cw = CollapseWidget()
    assert cw._get_collapsed_y() == cw.top - cw.collapsed_height
    assert cw.collapsed_y == cw._get_collapsed_y()


def test_collapsed_y():
    collapsed_widget = CollapseWidget()
    collapsed_y1 = collapsed_widget.collapsed_y

    collapsed_widget.expanded_height = FAKE.random_int(min=101)
    collapsed_y2 = collapsed_widget.collapsed_y

    collapsed_widget.expanded_y = FAKE.random_int(min=101)
    collapsed_y3 = collapsed_widget.collapsed_y

    collapsed_widget.collapsed_height = FAKE.random_int(min=101)
    collapsed_y4 = collapsed_widget.collapsed_y
    assert collapsed_y1 != collapsed_y2 != collapsed_y3 != collapsed_y4


def test_collapsing():
    cw = CollapseWidget()
    cw.collapsable = False
    cw.collapsed = True
    assert cw.collapsed is False
    cw.collapsable = True  # reset

    assert cw.y == cw.expanded_y
    assert cw.height == cw.expanded_height

    cw.collapsed = True
    assert cw.y == cw.collapsed_y
    assert cw.height == cw.collapsed_height


#
# CollapseBar
#
def test_collapse_bar_default_images():
    collapse_bar = CollapseBar(keyboard_listener=Mock())
    assert collapse_bar.collapse_image
    assert collapse_bar.expand_image


@patch("src.ui.collapse.CollapseBar.collide_point", return_value=True)
@patch("src.ui.collapse.CollapseBar.modify_dependant")
@patch("kivy.uix.floatlayout.FloatLayout.on_touch_up")
def test_collapse_bar_on_touch_up(*patches):
    patch_floatlayout_on_touch_up = patches[0]
    patch_modify_dependant = patches[1]

    mock_scroll_touch = Mock()
    mock_scroll_touch.button = "".join(["scroll", FAKE.word()])
    mock_scroll_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()
    mock_touch = Mock()
    mock_touch.pos = FAKE.pyfloat(), FAKE.pyfloat()
    mock_touch.button = FAKE.word()
    while "scroll" in mock_touch.button:
        mock_touch.button = FAKE.word()
    collapse_bar = CollapseBar(keyboard_listener=Mock())

    collapse_bar.on_touch_up(mock_scroll_touch)
    patch_floatlayout_on_touch_up.assert_called_once()
    patch_floatlayout_on_touch_up.reset_mock()

    assert collapse_bar.on_touch_up(mock_touch)
    patch_modify_dependant.assert_called_once()
    patch_modify_dependant.reset_mock()

    collapse_bar.collapsable = False
    collapse_bar.on_touch_up(mock_touch)
    patch_modify_dependant.assert_not_called()
    patch_floatlayout_on_touch_up.assert_called_once()


@patch("src.ui.collapse.CollapseBar.modify_dependant")
@patch("src.ui.focusedkeylisten.PassiveFocusBehavior.on_keyboard_down")
def test_collapse_bar_on_keyboard_down(*patches):
    patch_passivefocusbehavior_on_keyboard_down = on_keyboard_down = patches[0]
    patch_modify_dependant = patches[1]

    mock_kb = Mock()
    text = FAKE.words()
    fake_mods = FAKE.pylist()
    fake_keycode = FAKE.random_int(), FAKE.word()
    while {fake_keycode[1]} & {"enter", "numpadenter"}:
        fake_keycode = FAKE.random_int(), FAKE.word()

    cb = CollapseBar(keyboard_listener=Mock())
    assert cb.on_keyboard_down(mock_kb, (13, "enter"), text, fake_mods)
    assert cb.on_keyboard_down(mock_kb, (271, "numpadenter"), text, fake_mods)
    assert patch_modify_dependant.call_count == 2
    cb.on_keyboard_down(mock_kb, fake_keycode, text, fake_mods)
    patch_passivefocusbehavior_on_keyboard_down.assert_called_once_with(
        mock_kb, fake_keycode, text, fake_mods
    )

    patch_passivefocusbehavior_on_keyboard_down.reset_mock()
    patch_modify_dependant.reset_mock()
    cb.collapsable = False
    cb.on_keyboard_down(mock_kb, (13, "enter"), text, fake_mods)
    cb.on_keyboard_down(mock_kb, (271, "numpadenter"), text, fake_mods)
    patch_modify_dependant.assert_not_called()
    assert patch_passivefocusbehavior_on_keyboard_down.call_count == 2
    patch_passivefocusbehavior_on_keyboard_down.assert_has_calls(
        on_keyboard_down(mock_kb, (13, "enter"), text, fake_mods),
        on_keyboard_down(mock_kb, (271, "numpadenter"), text, fake_mods),
    )


@patch("kivy.uix.floatlayout.FloatLayout.add_widget")
@patch("kivy.uix.floatlayout.FloatLayout.remove_widget")
def test_collapse_bar_modify_dependant(patch_remove_widget, patch_add_widget):
    collapse_bar = CollapseBar(keyboard_listener=Mock(), dependant=Mock())
    patch_add_widget.reset_mock()  # ignore initialization calls
    old_dependant_collapsed = collapse_bar.dependant_collapsed
    collapse_bar.modify_dependant()
    assert collapse_bar.dependant_collapsed is not old_dependant_collapsed
    patch_remove_widget.assert_called_with(collapse_bar.dependant)
    patch_add_widget.assert_not_called()
    patch_remove_widget.reset_mock()
    patch_add_widget.reset_mock()

    old_dependant_collapsed = collapse_bar.dependant_collapsed
    collapse_bar.modify_dependant()
    assert collapse_bar.dependant_collapsed is not old_dependant_collapsed
    patch_add_widget.assert_called_with(collapse_bar.dependant)
    patch_remove_widget.assert_not_called()


def test_collapse_bar_on_dependant_collapsed():
    mock_dep = Mock()
    collapse_bar = CollapseBar(keyboard_listener=Mock(), dependant=mock_dep)
    collapse_bar.dependant_collapsed = FAKE.pybool()
    mock_dep.collapsed = not collapse_bar.dependant_collapsed
    collapse_bar.on_dependant_collapsed()
    assert collapse_bar.dependant_collapsed is mock_dep.collapsed


@patch("src.ui.collapse.CollapseBar.bind")
def test_collapse_bar_change_focus_highlight_color(patch_bind):
    cb = CollapseBar(keyboard_listener=Mock())
    patch_bind.assert_called_with(focus=cb.change_focus_highlight_color)
    cb.change_focus_highlight_color()
    assert cb.highlight_color == cb.unfocused_highlight_color

    cb.focus = True
    cb.change_focus_highlight_color()
    assert cb.highlight_color == cb.focused_highlight_color
