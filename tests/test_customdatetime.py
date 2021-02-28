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
from src.dbsetup import gregorian_cdt
from src.ui.mark import Mark
from src.ui.timeline import Timeline
from unittest.mock import Mock, patch


class DumEnum(Enum):
    DUM = 0


class ConvertibleDateTimeTest(TimeTestCase):
    def setUp(self):
        super(ConvertibleDateTimeTest, self).setUp()
        self.calendar_factory = ConvertibleCalendarFactory
        self.time_factory = ConvertibleTimeFactory
        # fmt: off
        self.datetime_units = [
            DateUnit.ERA, DateUnit.YEAR, DateUnit.MONTH, DateUnit.DAY,
            TimeUnit.HOUR, TimeUnit.MINUTE, TimeUnit.SECOND,
        ]
        # fmt: on
        self.timeline = Timeline(
            primary_mark=Mark(),
            secondary_mark=Mark(),
            event_view_mark=Mark(),
            cdt=gregorian_cdt,
        )

    @patch("src.customdate.ConvertibleDate.hr_to_ast")
    def test__init__(self, mock_hr_to_ast):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert isinstance(cdt.initial_interval[0], int)
        assert isinstance(cdt.initial_interval[1], DateUnit) or isinstance(
            cdt.initial_interval[1], TimeUnit
        )
        # fmt: off
        assert cdt.datetime_units == [
            DateUnit.ERA, DateUnit.YEAR, DateUnit.MONTH, DateUnit.DAY,
            TimeUnit.HOUR, TimeUnit.MINUTE, TimeUnit.SECOND,
        ]
        # fmt: on
        assert 0 in cdt.era_start_ordinals
        assert mock_hr_to_ast.return_value in cdt.era_start_ordinals
        mock_hr_to_ast.assert_called()

    def test__str__(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        ct = self.time_factory.build()
        cdt = ConvertibleDateTime(date=cd, time=ct)
        assert cd.calendar.name in cdt.__str__()
        assert ct.clock.name in cdt.__str__()

    def test_change_interval(self):  # relies on the UI but let's keep it here
        timeline = self.timeline
        old_frequency = 100_000
        interval = [old_frequency, DateUnit.YEAR]
        timeline.secondary_mark_interval = interval
        timeline.end_od = timeline.start_od + old_frequency * 365.25
        new_freq, new_unit = gregorian_cdt.change_interval(interval, timeline)
        assert new_freq < old_frequency or new_unit != DateUnit.YEAR

        old_frequency = 1
        interval = [old_frequency, DateUnit.DAY]
        new_freq, new_unit = gregorian_cdt.change_interval(interval, timeline)
        assert new_freq < old_frequency or new_unit not in DateUnit

        old_frequency = 1
        interval = [old_frequency, TimeUnit.SECOND]
        timeline.secondary_mark_interval = interval
        timeline.end_od = timeline.start_od + 365.25
        new_freq, new_unit = gregorian_cdt.change_interval(
            interval, timeline, increase=False
        )
        assert new_freq < old_frequency or new_unit != DateUnit.YEAR

    @patch("src.customdatetime.ConvertibleDateTime.change_unit")
    @patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
    @patch("src.customdatetime.ConvertibleDateTime.extend_od")
    def test_change_interval_recursively_changing_unit(self, *mocks):
        mock_change_unit = mocks[2]

        expected_interval = [FAKE.random_int(min=1), FAKE.random_element(elements=self.datetime_units)]
        mock_change_unit.side_effect = [None, expected_interval]

        tl = self.timeline
        tl.od_to_x = Mock()
        # mock too few marks on screen
        tl.od_to_x.side_effect = [0, tl.width + FAKE.random_int(min=1)]

        old_frequency = FAKE.random_int(min=1)
        interval = [FAKE.random_int(min=1), FAKE.random_element(elements=self.datetime_units)]
        tl.secondary_mark_interval = interval
        tl.end_od = tl.start_od + old_frequency * 365.25
        assert gregorian_cdt.change_interval(interval, tl) == expected_interval

    @patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
    @patch("src.customdatetime.ConvertibleDateTime.change_interval")
    def test_change_unit_when_increasing_unit(self, *mocks):
        non_year_or_era_units = [DateUnit.MONTH, DateUnit.DAY]
        non_year_or_era_units.extend(TimeUnit)
        non_year_unit = FAKE.random_element(elements=non_year_or_era_units)
        frequencies = [FAKE.random_int(min=1) for _ in range(5)]

        mock_change_interval = mocks[0]
        mock_get_frequencies = mocks[1]
        mock_timeline = Mock()
        mock_get_frequencies.return_value = frequencies

        non_year_interval = [max(frequencies), non_year_unit]
        non_year_unit_idx = non_year_or_era_units.index(non_year_unit)
        next_unit = non_year_or_era_units[non_year_unit_idx - 1]
        next_interval = [min(frequencies), next_unit]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        cdt.datetime_units = self.datetime_units

        cdt.change_unit(non_year_interval, mock_timeline, increase=False)
        mock_change_interval.assert_called_once_with(
            next_interval, mock_timeline, False, True
        )

        year_interval = [max(frequencies), DateUnit.YEAR]
        with pytest.raises(ValueError):
            cdt.change_unit(year_interval, mock_timeline, increase=False)

    @patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
    @patch("src.customdatetime.ConvertibleDateTime.change_interval")
    def test_change_unit_when_decreasing_unit(self, *mocks):
        non_sec_units = [*DateUnit]
        non_sec_units.extend([TimeUnit.HOUR, TimeUnit.MINUTE])
        non_sec_unit = FAKE.random_element(elements=non_sec_units)
        frequencies = [FAKE.random_int(min=1) for _ in range(5)]

        mock_change_interval = mocks[0]
        mock_get_frequencies = mocks[1]
        mock_timeline = Mock()
        mock_get_frequencies.return_value = frequencies

        non_sec_interval = [min(frequencies), non_sec_unit]
        non_year_unit_idx = non_sec_units.index(non_sec_unit)
        next_unit = self.datetime_units[non_year_unit_idx + 1]
        next_interval = [max(frequencies), next_unit]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        cdt.datetime_units = self.datetime_units

        cdt.change_unit(non_sec_interval, mock_timeline, increase=True)
        mock_change_interval.assert_called_once_with(
            next_interval, mock_timeline, True, True
        )

        second_interval = [min(frequencies), TimeUnit.SECOND]
        with pytest.raises(ValueError):
            cdt.change_unit(second_interval, mock_timeline, increase=True)

    @patch("src.customdatetime.ConvertibleDateTime.get_frequencies")
    @patch("src.customdatetime.ConvertibleDateTime.change_interval")
    def test_change_unit_can_do_nothing(self, *mocks):
        mock_change_interval = mocks[0]
        mock_get_frequencies = mocks[1]
        frequencies = [FAKE.random_int(min=1) for _ in range(5)]
        frequencies.sort()
        mock_get_frequencies.return_value = frequencies
        frequency = FAKE.random_element(elements=frequencies[1:-1])
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        interval = [frequency, Mock()]
        assert cdt.change_unit(interval, Mock(), FAKE.pybool()) is None
        mock_change_interval.assert_not_called()

    def test_get_primary_interval(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        cdt.datetime_units = self.datetime_units

        with pytest.raises(ValueError):
            cdt.get_primary_interval(DateUnit.ERA)

        frequency, unit = cdt.get_primary_interval(DateUnit.YEAR)
        assert frequency == 1
        assert unit == DateUnit.ERA

        frequency, unit = cdt.get_primary_interval(DateUnit.MONTH)
        assert frequency == 1
        assert unit == DateUnit.YEAR

        frequency, unit = cdt.get_primary_interval(DateUnit.DAY)
        assert frequency == 1
        assert unit == DateUnit.YEAR

        for unit in TimeUnit:
            frequency, unit = cdt.get_primary_interval(unit)
            assert frequency == 1
            assert unit == DateUnit.DAY

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_od_with_reverse(self, patch_shift_od):
        non_day_units = [DateUnit.YEAR, DateUnit.MONTH]
        non_day_units.extend(TimeUnit)
        non_day_unit = FAKE.random_element(elements=non_day_units)
        delta = FAKE.random_int(min=-9999)
        non_day_interval = [delta, non_day_unit]
        day_interval = [delta, DateUnit.DAY]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        od = FAKE.pyfloat()
        assert cdt.extend_od(od, day_interval, reverse=True) == od - delta
        patch_shift_od.assert_not_called()

        cdt.extend_od(od, non_day_interval, reverse=True)
        patch_shift_od.assert_called_with(od, [[-delta, non_day_unit]])

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_od_with_factor(self, patch_shift_od):
        non_day_units = [DateUnit.YEAR, DateUnit.MONTH]
        non_day_units.extend(TimeUnit)
        non_day_unit = FAKE.random_element(elements=non_day_units)
        delta = FAKE.random_int(min=-9999)
        non_day_interval = [delta, non_day_unit]
        day_interval = [delta, DateUnit.DAY]
        factor = FAKE.random_int()

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        od = FAKE.pyfloat()
        assert cdt.extend_od(od, day_interval, factor) == od + delta * factor
        patch_shift_od.assert_not_called()

        cdt.extend_od(od, non_day_interval, factor)
        patch_shift_od.assert_called_with(od, [[delta * factor, non_day_unit]])

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_od_for_day_interval(self, patch_shift_od):
        delta = FAKE.random_int(min=-9999)
        interval = [delta, DateUnit.DAY]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        od = FAKE.pyfloat()
        assert cdt.extend_od(od, interval) == od + delta
        patch_shift_od.assert_not_called()

    @patch("src.customdatetime.ConvertibleDateTime.shift_od")
    def test_extend_od_for_non_day_interval(self, patch_shift_od):
        units = [DateUnit.YEAR, DateUnit.MONTH]
        units.extend(TimeUnit)
        interval = [FAKE.random_int(), FAKE.random_element(elements=units)]

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        ordinal_decimal = FAKE.pyfloat()
        cdt.extend_od(ordinal_decimal, interval)
        patch_shift_od.assert_called_once_with(ordinal_decimal, [interval])

    def test_extend_od_raises(self):
        units = list(DateUnit)
        units.extend(TimeUnit)
        interval = [FAKE.random_int(), FAKE.random_element(elements=units)]

        bad_factor = FAKE.random_int(min=-9999, max=0)
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        ordinal_decimal = FAKE.pyfloat()
        with pytest.raises(ValueError):
            cdt.extend_od(ordinal_decimal, interval, bad_factor)

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

    @patch("src.customdatetime.ConvertibleDateTime.od_to_ast_ymd")
    @patch("src.customdate.ConvertibleDate.next_ast_ymd")
    @patch("src.customdatetime.ConvertibleDateTime.ast_ymd_to_od")
    def test_next_od_for_date_unit(self, *patches):
        patch_ast_ymd_to_od = patches[0]
        patch_next_ast_ymd = patches[1]
        patch_od_to_ast_ymd = patches[2]

        od1 = FAKE.pyfloat()
        od2 = FAKE.pyfloat()
        ast_ymd1 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        ast_ymd2 = FAKE.random_int(), FAKE.random_int(), FAKE.random_int()
        interval = [FAKE.random_int(), FAKE.random_element(elements=DateUnit)]
        forward = FAKE.pybool()

        patch_od_to_ast_ymd.return_value = ast_ymd1
        patch_next_ast_ymd.return_value = ast_ymd2
        patch_ast_ymd_to_od.return_value = od2

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert cdt.next_od(od1, interval, forward) == od2
        patch_od_to_ast_ymd.assert_called_once_with(od1)
        patch_next_ast_ymd.assert_called_once_with(ast_ymd1, interval, forward)
        patch_ast_ymd_to_od.assert_called_once_with(ast_ymd2)

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
        forward = FAKE.pybool()

        patch_od_to_hms.return_value = fake_hms1
        patch_next_hms.return_value = fake_hms2, day_delta
        patch_set_hms.return_value = fake_od

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        assert cdt.next_od(fake_od, interval, forward) == fake_od
        patch_od_to_hms.assert_called_once_with(fake_od)
        patch_next_hms.assert_called_once_with(fake_hms1, interval, forward)
        patch_set_hms.assert_called_once_with(fake_od, fake_hms2, day_delta)

    def test_next_od_raises(self):
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        with pytest.raises(ValueError):
            cdt.next_od(FAKE.pyfloat(), [FAKE.random_int(), DumEnum.DUM])

    @pytest.mark.db
    @patch("sympy.proper_divisors")
    def test_get_frequencies(self, patch_proper_divisors):
        def all_ints(frequencies: list) -> bool:
            return all([isinstance(freq, int) for freq in frequencies])

        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        ct = self.time_factory.build()
        clk = ct.clock
        cdt = ConvertibleDateTime(date=cd, time=ct)
        with self.session:
            self.session.add_all([clk, cd.calendar])
            self.session.flush()
            year_frequencies = cdt.get_frequencies(DateUnit.YEAR)
            assert all_ints(year_frequencies)

            cdt.get_frequencies(DateUnit.MONTH)
            patch_proper_divisors.assert_called_once()
            patch_proper_divisors.reset_mock()

            day_frequencies = cdt.get_frequencies(DateUnit.DAY)
            assert all_ints(day_frequencies)

            cdt.get_frequencies(TimeUnit.HOUR)
            patch_proper_divisors.assert_called_once_with(clk.hours_in_day)
            patch_proper_divisors.reset_mock()

            cdt.get_frequencies(TimeUnit.MINUTE)
            patch_proper_divisors.assert_called_once_with(clk.minutes_in_hour)
            patch_proper_divisors.reset_mock()

            cdt.get_frequencies(TimeUnit.SECOND)
            patch_proper_divisors.assert_called_once_with(
                clk.seconds_in_minute
            )
            patch_proper_divisors.reset_mock()

            with pytest.raises(ValueError):
                # noinspection PyTypeChecker
                cdt.get_frequencies(DumEnum.DUM)

    @pytest.mark.db
    @patch("src.customtime.ConvertibleTime.hms_to_hr_time")
    @patch("src.customdatetime.ConvertibleDateTime.od_to_hms")
    @patch("src.customdate.ConvertibleDate.format_hr_date")
    @patch("src.customdatetime.ConvertibleDateTime.od_to_ast_ymd")
    def test_od_to_hr_date(self, *patches):
        patch_format_hr_date = patches[1]
        patch_hms_to_hr_time = patches[3]

        ordinal_decimal = FAKE.pyfloat()
        dateunit = FAKE.random_element(elements=DateUnit)
        timeunit = FAKE.random_element(elements=TimeUnit)
        cd = ConvertibleDate(calendar=self.calendar_factory.build())
        cdt = ConvertibleDateTime(date=cd, time=self.time_factory.build())
        with self.session:
            self.session.add_all([cd.calendar, cdt.time.clock])
            self.session.flush()
            cdt.od_to_hr_date(ordinal_decimal, dateunit)
            patch_format_hr_date.assert_called_once()

            cdt.od_to_hr_date(ordinal_decimal, timeunit)
            patch_hms_to_hr_time.assert_called_once()
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            cdt.od_to_hr_date(ordinal_decimal, DumEnum.DUM)

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
