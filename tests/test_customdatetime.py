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
from tests.factories import ConvertibleCalendarFactory, ConvertibleTimeFactory
from tests.utils import TimeTestCase
from src.customdate import ConvertibleDate
from src.customdatetime import ConvertibleDateTime
from unittest.mock import patch


class ConvertibleDateTimeTest(TimeTestCase):
    def setUp(self):
        super(ConvertibleDateTimeTest, self).setUp()
        self.calendar_factory = ConvertibleCalendarFactory
        self.time_factory = ConvertibleTimeFactory

    @patch("src.customtime.ConvertibleTime.seconds_to_hms")
    def test_od_to_hms(self, patch_seconds_to_hms):
        seconds_into_day_as_decimal = self.seconds / 86400
        ordinal_decimal = self.py_dt.toordinal() + seconds_into_day_as_decimal
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.earth_ct)
        cdt.od_to_hms(ordinal_decimal)
        patch_seconds_to_hms.assert_called_with(self.seconds)
