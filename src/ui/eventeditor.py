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
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from src.eventcontroller import EventController
from src.setup_db import gregorian_datetime
# noinspection PyUnresolvedReferences
from src.ui.textboundlabel import TextBoundLabel

# todo add more alignment constants
# todo only allow numbers
# todo make resseting hint_text label it's own widget
# todo redraw events on accepted event
# todo enable disable aliases?
# todo enable disable description?
Builder.load_string("""
#:import utils src.ui.utils
<EventEditor>:
    id: event_editor
    window_padding: sp(18)
    small_vert_padding: sp(6)
    big_vert_padding: sp(18)

    hor_padding: sp(12)
    hor_align_mark: self.x + self.width * (1 / 3)

    canvas:
        Color:
            rgba: utils.SURFACE_COLOR
        Rectangle:
            pos: self.pos
            size: self.size

    #
    # Name
    #
    TextInput:
        id: name_input
        size_hint: None, 0.05
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: event_editor.top - event_editor.window_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        multiline: False
        hint_text: "Untitled Event"

    TextBoundLabel:
        text: "Name: "
        center_y: name_input.center_y
        x: name_input.x - event_editor.hor_padding - self.width

    TextInput:
        id: alias_input
        size_hint: None, 0.05
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: name_input.y - event_editor.big_vert_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        multiline: False
        hint_text: "Alternate Names i.e 'The Great War' for 'World War I'"

    TextBoundLabel:
        text: "Aliases: "
        center_y: alias_input.center_y
        x: alias_input.x - event_editor.hor_padding - self.width

    #
    # Start
    #
    TextInput:
        id: start_input
        size_hint: None, 0.05
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: alias_input.y - event_editor.big_vert_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        multiline: False
        hint_text: "Start Ordinal Decimal"

    TextBoundLabel:
        text: "Start :"
        center_y: start_input.center_y
        x: start_input.x - event_editor.hor_padding - self.width

    #
    # Duration/End
    #
    ToggleButton:
        id: set_end_button
        size_hint: 0.15, 0.05
        text: "Set End"
        group: "set_end"
        allow_no_selection: False
        state: "down"
        y: start_input.y - event_editor.big_vert_padding - self.height
        right: start_input.center_x

    ToggleButton:
        id: set_duration_button
        size_hint: 0.15, 0.05
        text: "Set Duration"
        group: "set_end"
        allow_no_selection: False
        x: set_end_button.right
        y: set_end_button.y

    TextInput:
        id: end_input
        init_hint_text: "End Ordinal Decimal"
        init_hint_text_color: [0.5, 0.5, 0.5, 1]
        size_hint: None, 0.05
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: set_end_button.y - event_editor.big_vert_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        hint_text: self.init_hint_text
        disabled: set_end_button.state == "normal"
        multiline: False
        on_disabled: self.text = ""
        on_disabled: self.text = ""; self.hint_text = self.init_hint_text; self.hint_text_color = self.init_hint_text_color

    TextBoundLabel:
        text: "End :"
        center_y: end_input.center_y
        x: end_input.x - event_editor.hor_padding - self.width
        disabled: end_input.disabled

    TextInput:
        id: duration_input
        init_hint_text: "Duration Ordinal Decimal"
        init_hint_text_color: [0.5, 0.5, 0.5, 1]
        size_hint: None, 0.05
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: end_input.y - event_editor.big_vert_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        hint_text: self.init_hint_text
        multiline: False
        disabled: set_duration_button.state == "normal"
        on_disabled: self.text = ""; self.hint_text = self.init_hint_text; self.hint_text_color = self.init_hint_text_color

    TextBoundLabel:
        text: "Duration :"
        center_y: duration_input.center_y
        x: duration_input.x - event_editor.hor_padding - self.width
        disabled: duration_input.disabled

    #
    # Description
    #
    TextInput:
        id: description_input
        init_hint_text: "Event Description"
        init_hint_text_color: [0.5, 0.5, 0.5, 1]
        size_hint: None, 0.3
        x: (event_editor.hor_padding / 2) + event_editor.hor_align_mark
        y: duration_input.y - event_editor.big_vert_padding - self.height
        width: event_editor.right - event_editor.window_padding - self.x
        hint_text: self.init_hint_text

    TextBoundLabel:
        text: "Description :"
        top: description_input.top
        x: description_input.x - event_editor.hor_padding - self.width

    #
    # Confirm
    #
    Button:
        size_hint: 0.1, 0.05
        text: "Accept"
        right: event_editor.right - event_editor.window_padding
        top: description_input.y - event_editor.big_vert_padding
        on_release: event_editor.confirm_input()
""")


class EventEditor(FloatLayout):
    """Where the end-user changes event details"""

    cdt = ObjectProperty(gregorian_datetime)
    start = NumericProperty(None)
    end = NumericProperty(None)
    # todo should be all the fields from event

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ec = EventController(cdt=self.cdt)

        if self.ids.get("start_input") and self.start is not None:
            self.ids["start_input"].text = str(self.start)
        if self.ids.get("end_input") and self.end is not None:
            self.ids["end_input"].text = str(self.end)

        self.bind(cdt=self.update_ec)

    def confirm_input(self):
        name_input = self.ids["name_input"]
        alias_input = self.ids["alias_input"]
        start_input = self.ids["start_input"]
        end_input = self.ids["end_input"]
        duration_input = self.ids["duration_input"]
        description_input = self.ids["description_input"]

        name = name_input.text or "Untitled Event"
        aliases = alias_input.text.split(",")  # todo less fragile processing
        start = start_input.text
        end = end_input.text
        duration = duration_input.text
        description = description_input.text
        valid_inputs = True
        fields = {"name": name, "aliases": aliases, "description": description}

        try:
            start = float(start)
        except ValueError:
            start_input.hint_text_color = [1, 0, 0, 0.5]
            valid_inputs = False
        else:
            fields["start"] = start

        try:
            end = float(end)
        except ValueError:
            if not end_input.disabled:
                end_input.hint_text_color = [1, 0, 0, 0.5]
                valid_inputs = False
        else:
            fields["end"] = end

        try:
            duration = float(duration)
        except ValueError:
            if not duration_input.disabled:
                duration_input.hint_text_color = [1, 0, 0, 0.5]
                valid_inputs = False
        else:
            fields["duration"] = duration

        if valid_inputs:
            self.ec.make(fields)
            app = App.get_running_app()
            app.hide_event_editor()
            self.reset_text_input()
            # todo dispatch_events changed so they're redrawn?
            # todo lose focus after making event

    def reset_text_input(self) -> None:
        # todo put this into a collection and loop
        self.ids["name_input"].text = ""
        self.ids["alias_input"].text = ""
        self.ids["start_input"].text = ""
        self.ids["end_input"].text = ""
        self.ids["end_input"].hint_text_color = [0.5, 0.5, 0.5, 1]  # todo put in variable
        self.ids["duration_input"].hint_text_color = [0.5, 0.5, 0.5, 1]
        self.ids["duration_input"].text = ""
        self.ids["description_input"].text = ""

    def update_ec(self, *_) -> None:
        self.ec.cdt = self.cdt

    def on_start(self, *_) -> None:
        if self.start is not None:
            try:
                self.ids["start_input"].text = str(self.start)
            except KeyError:
                pass

    def on_end(self, *_) -> None:
        if self.end is not None:
            try:
                self.ids["end_input"].text = str(self.end)
            except KeyError:
                pass
