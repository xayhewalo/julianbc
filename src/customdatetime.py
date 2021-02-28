"""Where the UI, time-tracking, and date-tracking meet"""
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
import sympy

from src.customdate import ConvertibleDate, DateUnit, Ymd_tuple
from src.customtime import ConvertibleTime, TimeUnit, Hms_tuple
from typing import Union

DateTimeEnum = Union[DateUnit, TimeUnit]
DateTime_interval = list[int, DateTimeEnum]


class ConvertibleDateTime:
    """
    Manipulates dates and times with ConvertibleDate and ConvertibleTime

    * `Day decimal` is the progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` or `od` is an `ordinal` plus a `day decimal`
    """

    def __init__(self, date: ConvertibleDate, time: ConvertibleTime):
        self.date = date
        self.time = time
        self.initial_interval = [6, DateUnit.MONTH]
        self.datetime_units = list(DateUnit)
        self.datetime_units.extend(TimeUnit)  # largest to smallest

        # There is a one day gap between the end of the proleptic era and start
        # of the first non-proleptic era. All other eras have at least a one
        # year difference between them
        self.era_start_ordinals = [0]  # proleptic era always ends at 0 ordinal
        for idx, era_range in enumerate(self.date.calendar.era_ranges):
            if idx == 0:  # skip proleptic era
                continue

            start_hr_year = era_range[0]
            start_ast_year = self.date.hr_to_ast(start_hr_year, idx)
            self.era_start_ordinals.append(start_ast_year)

    def __str__(self):
        return f"{self.date.calendar.name} - {self.time.clock.name}"

    @staticmethod
    def get_primary_interval(unit: DateTimeEnum) -> DateTime_interval:
        """
        interval of Timeline.primary_mark
        :returns: an interval with a DateTimeUnit larger than the unit given
        :raises: ValueError for invalid primary interval unit
        """
        if unit == DateUnit.YEAR:
            primary_unit = DateUnit.ERA
        elif unit in (DateUnit.MONTH, DateUnit.DAY):
            primary_unit = DateUnit.YEAR
        elif unit in TimeUnit:
            primary_unit = DateUnit.DAY
        else:
            raise ValueError(f"Can't find primary interval for unit {unit}")
        return [1, primary_unit]

    def extend_od(
        self,
        ordinal_decimal: float,
        interval: DateTime_interval,
        factor: int = 1,
        reverse=False,
    ) -> float:
        """
        convenience method to extend start and end ordinals using shift_od
        :raises ValueError: factor is less than or equal to zero
        """
        if factor <= 0:
            raise ValueError(f"Can't widen span by factor of {factor}")

        delta, unit = interval
        delta = -delta * factor if reverse else delta * factor
        if unit == DateUnit.DAY:
            return ordinal_decimal + delta
        interval = [delta, unit]
        return self.shift_od(ordinal_decimal, [interval])

    def shift_od(self, ordinal_decimal: float, intervals: list) -> float:
        """
        :param ordinal_decimal: beginning ordinal decimal
        :param intervals: amount of units to shift by
        :return: an ordinal decimal
        """
        date_intervals = []
        time_intervals = []
        for interval in intervals:
            unit = interval[1]
            if unit in DateUnit:
                date_intervals.append(interval)
            elif unit in TimeUnit:
                time_intervals.append(interval)
            else:
                raise ValueError(f"Can't shift ordinal decimal by {unit}")

        if date_intervals:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            ast_ymd = self.date.shift_ast_ymd(ast_ymd, date_intervals)
            ordinal_decimal = self.ast_ymd_to_od(ast_ymd)
        if time_intervals:
            hms = self.od_to_hms(ordinal_decimal)
            hms, day_delta = self.time.shift_hms(hms, time_intervals)
            ordinal_decimal = self.set_hms(ordinal_decimal, hms, day_delta)
        return ordinal_decimal

    def next_od(
        self, ordinal_decimal: float, interval: DateTime_interval, forward=True
    ) -> float:
        """Ordinal decimal variation of next_ast_ymd and next_hms"""
        _, unit = interval

        if unit in DateUnit:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            ast_ymd = self.date.next_ast_ymd(ast_ymd, interval, forward)
            return self.ast_ymd_to_od(ast_ymd)
        elif unit in TimeUnit:
            hms = self.od_to_hms(ordinal_decimal)
            hms, day_delta = self.time.next_hms(hms, interval, forward)
            ordinal_decimal = self.set_hms(ordinal_decimal, hms, day_delta)
            return ordinal_decimal
        raise ValueError(f"Can't shift ordinal decimal by {unit}")

    def get_frequencies(self, unit: DateTimeEnum) -> list:
        """:raises ValueErorr: if unit is not a DateUnit or TimeUnit"""
        values = None
        if unit == DateUnit.YEAR:
            # fmt: off
            values = [
                1, 2, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000,
                7500, 10_000, 25_000, 50_000, 75_000, 100_000,
            ]
            # fmt: on
        elif unit == DateUnit.MONTH:
            num_common_months = self.date.calendar.months_in_common_year
            num_leap_months = self.date.calendar.months_in_leap_year
            least_months_in_year = min(num_common_months, num_leap_months)
            values = sympy.proper_divisors(least_months_in_year)
        elif unit == DateUnit.DAY:
            calendar = self.date.calendar
            min_common_month_len = min(calendar.days_in_common_year_months)
            min_leap_month_len = min(calendar.days_in_leap_year_months)
            min_days_in_month = min(min_leap_month_len, min_common_month_len)
            multiples_of_five = list(range(0, min_days_in_month + 1, 5))
            multiples_of_five.remove(0)
            values = [1, 2]
            values.extend(multiples_of_five)
        elif unit == TimeUnit.HOUR:
            values = sympy.proper_divisors(self.time.clock.hours_in_day)
        elif unit == TimeUnit.MINUTE:
            values = sympy.proper_divisors(self.time.clock.minutes_in_hour)
        elif unit == TimeUnit.SECOND:
            values = sympy.proper_divisors(self.time.clock.seconds_in_minute)

        if values is None:
            raise ValueError(f"Cannot find valid frequencies for {unit}")
        return values

    def od_to_hr_date(self, ordinal_decimal: float, unit: DateTimeEnum) -> str:
        """:raises ValueError: if unit is not a DateUnit or TimeUnit"""
        if unit in DateUnit:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            return self.date.format_hr_date(ast_ymd)
        elif unit in TimeUnit:
            hms = self.od_to_hms(ordinal_decimal)
            return self.time.hms_to_hr_time(hms)
        raise ValueError(f"{unit} not a valid date or time unit")

    def ast_ymd_to_od(self, ast_ymd: Ymd_tuple) -> float:
        ordinal_date = self.date.ast_ymd_to_ordinal_date(ast_ymd)
        return float(self.date.ordinal_date_to_ordinal(ordinal_date))

    def od_to_ast_ymd(self, ordinal_decimal: float) -> Ymd_tuple:
        ordinal = int(ordinal_decimal)
        ordinal_date = self.date.ordinal_to_ordinal_date(ordinal)
        return self.date.ordinal_date_to_ast_ymd(ordinal_date)

    def od_to_hms(self, ordinal_decimal: float) -> Hms_tuple:
        day_decimal = ordinal_decimal - int(ordinal_decimal)
        seconds = round(self.time.clock.seconds_in_day * day_decimal)
        return self.time.seconds_to_hms(seconds)

    def set_hms(
        self, ordinal_decimal: float, hms: Hms_tuple, day_delta: int = 0
    ) -> float:
        """
        :param ordinal_decimal: starting ordinal decimal
        :param hms: hour, minute, second
        :param day_delta: optional amount of days between starting and final od
        :return: ordinal decimal set to the hms and shifted by day_delta
        """
        day_decimal = self.hms_to_day_decimal(hms)
        return int(ordinal_decimal) + day_delta + day_decimal

    def hms_to_day_decimal(self, hms: Hms_tuple) -> float:
        seconds = self.time.hms_to_seconds(hms)
        return seconds / self.time.clock.seconds_in_day

    @staticmethod
    def is_datetime_unit(unit: DateTimeEnum, attr_name: str) -> bool:
        attr_name = attr_name.upper()
        expected_unit = getattr(DateUnit, attr_name, None)
        if expected_unit == unit:
            return True

        expected_unit = getattr(TimeUnit, attr_name, None)
        if expected_unit == unit:
            return True
        return False
