#  Copyright (c) 2021 author(s) of JulianBC.
#
#  This file is part of JulianBC.
#
#  JulianBC is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  JulianBC is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with JulianBC.  If not, see <https://www.gnu.org/licenses/>.
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout


Builder.load_string("""
#:import utils src.ui.utils
<ImageButton@ButtonBehavior+Image>:
    canvas.before:
        Color:
            rgb: 0.5, 0.5, 0.5
        Rectangle:
            pos: self.pos
            size: self.size
    source: "./media/plus.png"
    # allow_stretch: True

<HeaderBar>:
    size_hint: 1, 0.1
    pos_hint: {"top": 1}

    button_padding: sp(2)
    canvas:
        Color:
            rgba: utils.HEADER_COLOR
        Rectangle:
            pos: self.pos
            size: self.size

    Button:
        id: add_event_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.x + self.parent.button_padding
        text: "+Event"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: add_entity_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_event_button.x + self.parent.button_padding + self.width
        text: "+Entity"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: swap_calendar_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_entity_button.x + self.parent.button_padding + self.width
        text: "+/-> Cal"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: swap_calendar_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_entity_button.x + self.parent.button_padding + self.width
        text: "+/<-> Cal"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    #
    # View Modes
    #
    ToggleButton:
        id: timeline_view_button
        state: "down"
        group: "view"
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: entity_view_button.x - self.width - self.parent.button_padding
        allow_no_selection: False
        text: "TL View"

    ToggleButton:
        id: entity_view_button
        group: "view"
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.center_x - self.parent.button_padding / 2 - self.width
        allow_no_selection: False
        text: "Ent View"
        on_press: self.state="normal"; timeline_view_button.state="down"; app.show_not_implemented_popup()

    ToggleButton:
        id: wiki_view_button
        group: "view"
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: entity_view_button.x + self.parent.button_padding + self.width
        allow_no_selection: False
        text: "Wiki\\nView"
        on_press: self.state="normal"; timeline_view_button.state="down"; app.show_not_implemented_popup()

    ToggleButton:
        id: thread_view_button
        group: "view"
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: wiki_view_button.x + self.parent.button_padding + self.width
        allow_no_selection: False
        text: "Thread\\nView"
        on_press: self.state="normal"; timeline_view_button.state="down"; app.show_not_implemented_popup()

    #
    # Util Buttons
    #
    Button:
        id: inspector_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: search_button.x - self.width - self.parent.button_padding
        text: "Inspector"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: search_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: filter_button.x - self.width - self.parent.button_padding
        text: "Search"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: filter_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: settings_button.x - self.width - self.parent.button_padding
        text: "Filter"
        on_press: self.state="normal"; app.show_not_implemented_popup()

    Button:
        id: settings_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.width  - self.parent.button_padding - self.width
        text: "Cog"
        on_press: self.state="normal"; app.show_not_implemented_popup()

""")


class HeaderBar(FloatLayout):
    pass
