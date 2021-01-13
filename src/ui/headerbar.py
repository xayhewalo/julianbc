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

    Image:
        source: "plus.svg"

    Button:
        id: add_event_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.x + self.parent.button_padding
        text: "+Event"

    Button:
        id: add_entity_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_event_button.x + self.parent.button_padding + self.width
        text: "+Entity"

    Button:
        id: swap_calendar_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_entity_button.x + self.parent.button_padding + self.width
        text: "+/-> Cal"

    Button:
        id: swap_calendar_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: add_entity_button.x + self.parent.button_padding + self.width
        text: "+/<-> Cal"

    #
    # View Modes
    #
    ToggleButton:
        id: timeline_view_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: entity_view_button.x - self.width - self.parent.button_padding
        text: "TL View"

    ToggleButton:
        id: entity_view_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.center_x - self.parent.button_padding / 2 - self.width
        text: "Ent View"

    ToggleButton:
        id: wiki_view_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: entity_view_button.x + self.parent.button_padding + self.width
        text: "Wiki\\nView"

    ToggleButton:
        id: thread_view_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: wiki_view_button.x + self.parent.button_padding + self.width
        text: "Thread\\nView"

    #
    # Util Buttons
    #
    Button:
        id: inspector_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: search_button.x - self.width - self.parent.button_padding
        text: "Inspector"

    Button:
        id: search_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: filter_button.x - self.width - self.parent.button_padding
        text: "Search"

    Button:
        id: filter_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: settings_button.x - self.width - self.parent.button_padding
        text: "Filter"

    Button:
        id: settings_button
        size_hint: 0.07, .9
        pos_hint: {"center_y": 0.5}
        x: self.parent.width  - self.parent.button_padding - self.width
        text: "Cog"
""")


class HeaderBar(FloatLayout):
    pass
