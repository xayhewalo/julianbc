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
from kivy.properties import BooleanProperty, ObjectProperty


class AbstractFocus:
    """a shell of kivy's FocusBehavior that decouples the keyboard and focus"""

    _instances = []
    _current_focused_widget = None
    focus = BooleanProperty(False)
    focus_previous = ObjectProperty(allownone=True, rebind=True)
    focus_next = ObjectProperty(allownone=True, rebind=True)
    focus_on_scroll = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection PyUnresolvedReferences
        self.__class__._instances.append(self)

    def set_focus_next(self):
        self.lose_focus()
        try:
            self.focus_next.gain_focus()
        except AttributeError:
            self._ensure_none_focused()

    def set_focus_previous(self):
        self.lose_focus()
        try:
            self.focus_previous.gain_focus()
        except AttributeError:
            self._ensure_none_focused()

    @staticmethod
    def _ensure_none_focused():
        try:
            AbstractFocus._current_focused_widget.lose_focus()
        except AttributeError:
            pass
        else:
            AbstractFocus._current_focused_widget = None

    def on_focus(self, *_):
        self.defocus_others()

    def defocus_others(self):
        if self.focus:
            # noinspection PyUnresolvedReferences
            AbstractFocus._current_focused_widget = self
            for instance in self.__class__._instances:
                if self != instance and instance.focus is True:
                    instance.lose_focus()

    # noinspection PyUnresolvedReferences
    def on_touch_down(self, touch):
        button = touch.button
        if self.collide_point(*touch.pos):
            if self.focus_on_scroll or not button.startswith("scroll"):
                self.gain_focus()
        return super().on_touch_down(touch)

    def gain_focus(self, *_):
        """
        Should be used instead of directly setting focus to allow a subclass to
        implement custom logic when gaining focus
        """

        self.focus = True

    def lose_focus(self, *_):
        """Similar to gain_focus(), useful for custom losing focus logic"""

        self.focus = False

    def give_focus(self, *_):
        """convenience method for widgets/layouts that pass along focus"""

        if self.focus:
            self.set_focus_next()
