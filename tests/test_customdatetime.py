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
import copy
import pytest

from enum import Enum
from tests.factories import ConvertibleCalendarFactory, ConvertibleTimeFactory
from tests.utils import FAKE, TimeTestCase
from src.customdate import ConvertibleDate, DateUnit
from src.customdatetime import ConvertibleDateTime, TimeUnit
from unittest.mock import patch


class DumEnum(Enum):
    DUM = 0


class ConvertibleDateTimeTest(TimeTestCase):
    def setUp(self):
        super(ConvertibleDateTimeTest, self).setUp()
        self.calendar_factory = ConvertibleCalendarFactory
        self.time_factory = ConvertibleTimeFactory

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_span_for_days(self, patch_shift_od):
        start = FAKE.pyfloat()
        end = FAKE.pyfloat()
        time_span = end - start
        delta = FAKE.random_int(min=1)
        interval = [delta, DateUnit.DAY]
        factor = FAKE.random_int(min=1)

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        made_start, made_end = cdt.extend_span(start, end, interval, factor)
        made_time_span = made_end - made_start
        assert made_start < start
        assert made_end > end
        assert made_time_span > time_span
        assert made_time_span == time_span + (2 * delta * factor)
        patch_shift_od.assert_not_called()

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_span_for_non_day_units(self, patch_shift_od):
        start = FAKE.pyfloat()
        end = FAKE.pyfloat()
        delta = FAKE.random_int(min=1)
        factor = FAKE.random_int(min=1)
        fake_unit = FAKE.random_int(min=-9999, max=-1)
        interval = [delta, fake_unit]
        extended_interval = [delta * factor, fake_unit]
        backwards_interval = [-delta * factor, fake_unit]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        cdt.extend_span(start, end, interval, factor)
        patch_shift_od.assert_any_call(start, [backwards_interval])
        patch_shift_od.assert_any_call(end, [extended_interval])

    def test_extend_span_raises(self):
        start = FAKE.pyfloat()
        end = FAKE.pyfloat()
        bad_interval = [FAKE.random_int(min=-9999, max=0), DateUnit.DAY]
        bad_factor = FAKE.random_int(min=-9999, max=0)

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        with pytest.raises(ValueError):
            cdt.extend_span(start, end, FAKE.pylist(), bad_factor)
        with pytest.raises(ValueError):
            cdt.extend_span(FAKE.pyfloat(), FAKE.pyfloat(), bad_interval)

    @patch("src.customdatetime.ConvertibleDateTime.od_to_ast_ymd")
    @patch("src.customdate.ConvertibleDate.shift_ast_ymd")
    @patch("src.customdatetime.ConvertibleDateTime.ast_ymd_to_od")
    @patch("src.customdatetime.ConvertibleDateTime.od_to_hms")
    @patch("src.customtime.ConvertibleTime.shift_hms")
    @patch("src.customdatetime.ConvertibleDateTime.set_hms")
    def test_shift_od(self, *patches):
        patch_set_hms = patches[0]
        patch_shift_hms = patches[1]
        patch_od_to_hms = patches[2]
        patch_ast_ymd_to_od = patches[3]
        patch_shift_ast_ymd = patches[4]
        patch_od_to_ast_ymd = patches[5]

        fake_ordinal_decimal1 = FAKE.pyfloat()
        fake_ordinal_decimal2 = FAKE.pyfloat()
        fake_day_delta = FAKE.random_int(min=1)
        fake_ordinal_decimal3 = FAKE.pyfloat()
        fake_ast_ymd1 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_ast_ymd2 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_hms1 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_hms2 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()

        patch_od_to_ast_ymd.return_value = fake_ast_ymd1
        patch_shift_ast_ymd.return_value = fake_ast_ymd2
        patch_ast_ymd_to_od.return_value = fake_ordinal_decimal2
        patch_od_to_hms.return_value = fake_hms1
        patch_shift_hms.return_value = fake_hms2, fake_day_delta
        patch_set_hms.return_value = fake_ordinal_decimal3

        date_intervals = []
        for i in range(FAKE.random_int(min=1, max=3)):
            date_intervals.append([i, FAKE.random_element(elements=DateUnit)])
        time_intervals = []
        for i in range(FAKE.random_int(min=1, max=3)):
            time_intervals.append([i, FAKE.random_element(elements=TimeUnit)])
        intervals = copy.deepcopy(date_intervals)
        intervals.extend(time_intervals)

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert cdt.shift_od(fake_ordinal_decimal1, []) == fake_ordinal_decimal1
        assert (
            cdt.shift_od(fake_ordinal_decimal1, intervals)
            == fake_ordinal_decimal3
        )
        patch_od_to_ast_ymd.assert_called_once_with(fake_ordinal_decimal1)
        patch_shift_ast_ymd.assert_called_once_with(
            fake_ast_ymd1, date_intervals
        )
        patch_ast_ymd_to_od.assert_called_once_with(fake_ast_ymd2)
        patch_od_to_hms.assert_called_once_with(fake_ordinal_decimal2)
        patch_shift_hms.assert_called_once_with(fake_hms1, time_intervals)
        patch_set_hms.assert_called_once_with(
            fake_ordinal_decimal2, fake_hms2, fake_day_delta
        )

    def test_shift_od_raises(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        with pytest.raises(ValueError):
            cdt.shift_od(FAKE.pyfloat(), [[FAKE.random_int(), DumEnum.DUM]])

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

    @patch("src.customdatetime.ConvertibleDateTime.od_to_ast_ymd")
    @patch("src.customdate.ConvertibleDate.next_ast_ymd")
    @patch("src.customdatetime.ConvertibleDateTime.ast_ymd_to_od")
    def test_next_od_for_date_unit(self, *patches):
        patch_ast_ymd_to_od = patches[0]
        patch_next_ast_ymd = patches[1]
        patch_od_to_ast_ymd = patches[2]

        ordinal_decimal1 = FAKE.pyfloat()
        ordinal_decimal2 = FAKE.pyfloat()
        fake_ast_ymd1 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_ast_ymd2 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        interval = [FAKE.random_int(), FAKE.random_element(elements=DateUnit)]

        patch_od_to_ast_ymd.return_value = fake_ast_ymd1
        patch_next_ast_ymd.return_value = fake_ast_ymd2
        patch_ast_ymd_to_od.return_value = ordinal_decimal2

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert cdt.next_od(ordinal_decimal1, interval) == ordinal_decimal2
        patch_od_to_ast_ymd.assert_called_once_with(ordinal_decimal1)
        patch_next_ast_ymd.assert_called_once_with(fake_ast_ymd1, interval)
        patch_ast_ymd_to_od.assert_called_once_with(fake_ast_ymd2)

    @patch("src.customdatetime.ConvertibleDateTime.od_to_hms")
    @patch("src.customtime.ConvertibleTime.next_hms")
    @patch("src.customdatetime.ConvertibleDateTime.set_hms")
    def test_next_od_for_time_unit(self, *patches):
        patch_set_hms = patches[0]
        patch_next_hms = patches[1]
        patch_od_to_hms = patches[2]

        fake_hms1 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_hms2 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        fake_od = FAKE.random_int()
        day_delta = FAKE.random_int()
        interval = [FAKE.random_int(), FAKE.random_element(elements=TimeUnit)]

        patch_od_to_hms.return_value = fake_hms1
        patch_next_hms.return_value = fake_hms2, day_delta
        patch_set_hms.return_value = fake_od

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert cdt.next_od(fake_od, interval) == fake_od
        patch_od_to_hms.assert_called_once_with(fake_od)
        patch_next_hms.assert_called_once_with(fake_hms1, interval)
        patch_set_hms.assert_called_once_with(fake_od, fake_hms2, day_delta)

    def test_next_od_raises(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        with pytest.raises(ValueError):
            cdt.next_od(FAKE.pyfloat(), [FAKE.random_int(), DumEnum.DUM])

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
        day_decimal = self.seconds / 86400
        ordinal_decimal = self.py_dt.toordinal() + day_decimal
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.earth_ct)
        cdt.od_to_hms(ordinal_decimal)
        patch_seconds_to_hms.assert_called_once_with(self.seconds)

    def test_set_hms(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.earth_ct)
        fake_ordinal = FAKE.random_int()
        fake_day_decimal = 1 / FAKE.random_int(min=2, max=10)

        hours = FAKE.random_int(max=23)
        minutes = FAKE.random_int(max=59)
        seconds = FAKE.random_int(max=59)
        hms = hours, minutes, seconds
        day_decimal = ((hours * 3600) + (minutes * 60) + seconds) / 86400
        day_delta = FAKE.random_int(min=-9999)
        assert (
            cdt.set_hms(fake_ordinal + fake_day_decimal, (0, 0, 0))
            == fake_ordinal
        )
        assert (
            cdt.set_hms(fake_ordinal + fake_day_decimal, (6, 0, 0))
            == fake_ordinal + 0.25
        )
        assert (
            cdt.set_hms(fake_ordinal + fake_day_decimal, (12, 0, 0))
            == fake_ordinal + 0.5
        )
        assert (
            cdt.set_hms(fake_ordinal + fake_day_decimal, (18, 0, 0))
            == fake_ordinal + 0.75
        )
        assert (
            cdt.set_hms(fake_ordinal + fake_day_decimal, hms, day_delta)
            == fake_ordinal + day_delta + day_decimal
        )

    def test_hms_to_day_decimal(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.earth_ct)
        hours = FAKE.random_int(min=0, max=23)
        minutes = FAKE.random_int(min=0, max=60)
        seconds = FAKE.random_int(min=0, max=60)
        seconds_from_hours = hours * 3600
        seconds_from_minutes = minutes * 60
        total_seconds = seconds_from_hours + seconds_from_minutes + seconds
        hms = hours, minutes, seconds
        assert cdt.hms_to_day_decimal((0, 0, 0)) == 0
        assert cdt.hms_to_day_decimal((0, 0, 1)) == 1 / 86400
        assert cdt.hms_to_day_decimal((0, 1, 0)) == 60 / 86400
        assert cdt.hms_to_day_decimal((1, 0, 0)) == 3600 / 86400
        assert cdt.hms_to_day_decimal((1, 1, 1)) == 3661 / 86400
        assert cdt.hms_to_day_decimal((12, 0, 0)) == 0.5
        assert cdt.hms_to_day_decimal(hms) == total_seconds / 86400
