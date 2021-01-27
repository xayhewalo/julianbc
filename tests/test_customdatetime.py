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
from tests.utils import FAKE, TimeTestCase
from src.customdate import ConvertibleDate
from src.customdatetime import ConvertibleDateTime
from unittest.mock import patch


class ConvertibleDateTimeTest(TimeTestCase):
    def setUp(self):
        super(ConvertibleDateTimeTest, self).setUp()
        self.calendar_factory = ConvertibleCalendarFactory
        self.time_factory = ConvertibleTimeFactory

    def test_extend_span(self):
        raise NotImplementedError

    def test_shift_od(self):
        raise NotImplementedError

    @patch("src.customdate.ConvertibleDate.ast_ymd_to_ordinal_date")
    @patch("src.customdate.ConvertibleDate.ordinal_date_to_ordinal")
    def test_ast_ymd_to_od(self, *patches):
        patch_ordinal_date_to_ordinal = patches[0]
        patch_ast_ymd_to_ordinal_date = patches[1]
        fake_ast_ymd = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_ord_date = FAKE.random_int(), FAKE.random_int()
        patch_ast_ymd_to_ordinal_date.return_value = fake_ord_date

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert isinstance(cdt.ast_ymd_to_od(fake_ast_ymd), float)
        patch_ast_ymd_to_ordinal_date.assert_called_once_with(fake_ast_ymd)
        patch_ordinal_date_to_ordinal.assert_called_once_with(fake_ord_date)

    @patch("src.customdate.ConvertibleDate.ordinal_to_ordinal_date")
    @patch("src.customdate.ConvertibleDate.ordinal_date_to_ast_ymd")
    def test_od_to_ast_ymd(self, *patches):
        patch_ordinal_date_to_ast_ymd = patches[0]
        patch_ordinal_to_ordinal_date = patches[1]
        fake_ordinal_decimal = FAKE.pyfloat()
        fake_ordinal = int(fake_ordinal_decimal)
        fake_ord_date = FAKE.random_int(), FAKE.random_int()
        patch_ordinal_to_ordinal_date.return_value = fake_ord_date

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        cdt.od_to_ast_ymd(fake_ordinal_decimal)

        patch_ordinal_to_ordinal_date.assert_called_once_with(fake_ordinal)
        patch_ordinal_date_to_ast_ymd.assert_called_once_with(fake_ord_date)

    @patch("src.customtime.ConvertibleTime.seconds_to_hms")
    def test_od_to_hms(self, patch_seconds_to_hms):
        seconds_into_day_as_decimal = self.seconds / 86400
        ordinal_decimal = self.py_dt.toordinal() + seconds_into_day_as_decimal
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.earth_ct)
        cdt.od_to_hms(ordinal_decimal)
        patch_seconds_to_hms.assert_called_once_with(self.seconds)
