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
from kivy.properties import BooleanProperty, NumericProperty


# noinspection PyUnresolvedReferences
class ZoomBehavior:
    disable_zoom_in = BooleanProperty(False)
    disable_zoom_out = BooleanProperty(False)
    zoom_delta = NumericProperty("20sp")
    zoom_by = NumericProperty(0)

    def on_touch_down(self, touch):
        if super(ZoomBehavior, self).on_touch_down(touch):
            return True

        if touch.button == "scrollup" and not self.disable_zoom_in:
            self.zoom_by = self.zoom_delta
        elif touch.button == "scrolldown" and not self.disable_zoom_out:
            self.zoom_by = -self.zoom_delta

        if self.zoom_by:
            self.zoom_by = 0
            return True
        return False
