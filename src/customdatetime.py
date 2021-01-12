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
import math

from .customdate import ConvertibleDate, DateUnits
from .customtime import ConvertibleTime, TimeUnits
from typing import Union


class ConvertibleDateTime:
    """
    Manipulates dates and times with ConvertibleDate and ConvertibleTime

    * `Day decimal` - progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` or `od` - an `ordinal` plus a `day decimal`
    * `Interval` is an amount of DateUnits or TimeUnits i.e. [3, Month]
    """

    def __init__(self, date: ConvertibleDate, time: ConvertibleTime):
        def exclusive_divisors(num: int) -> list:
            """:returns: divisors of `num` excluding `num`"""
            divs = {1}
            for i in range(2, int(math.sqrt(num)) + 1):
                if num % i == 0:
                    divs.update((i, num // i))
            return list(divs)

        self.date = date
        self.time = time
        # fmt: off
        self.year_deltas = [
            1, 2, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000,
            7500, 10_000, 25_000, 50_000, 75_000, 100_000
        ]
        # fmt: on
        num_common_months = len(self.date.calendar.common_year_month_names)
        num_leap_months = len(self.date.calendar.leap_year_month_names)
        least_months_in_year = min(num_common_months, num_leap_months)
        self.month_deltas = exclusive_divisors(least_months_in_year)

        self.day_deltas = [1, 5, 10, 15, 20, 25]
        self.hour_deltas = exclusive_divisors(self.time.clock.hours_in_day)
        minutes_in_hour = self.time.clock.minutes_in_hour
        self.minute_deltas = exclusive_divisors(minutes_in_hour)
        seconds_in_minute = self.time.clock.seconds_in_minute
        self.second_deltas = exclusive_divisors(seconds_in_minute)

    '''def next_dateunit(self, od: float, interval: list) -> float:
        """
        "First of next month", "first of two years ago", etc.
        If today is 2020/11/15, first of next month is 2020/12/1
        If today is 1917/4/3 first of four years ago is 1913/1/1

        :returns: ordinal decimal `delta` dateunits away from `od`
        """
        year, month, day = self.od_to_ast_ymd(od)
        delta, dateunit = interval
        sign = int(math.copysign(1, delta))

        if dateunit == DateUnits.YEAR:
            year += delta
            return self.ast_ymd_to_od((year, 1, 1))
        elif dateunit == DateUnits.MONTH and month:
            new_month = month + delta
            months_in_year = self.date.months_in_year(year)
            while new_month > months_in_year:
                year += 1 * sign  # todo should year += after delta calc?
                months_in_year = self.date.months_in_year(year)
                delta += months_in_year * -sign  # fixme assumes # months is same each year
                new_month = month + delta
            month = new_month
            """delta -= months_in_year * -sign
            year -= 1 * sign

            if sign == 1:
                delta -= self.date.months_in_year(year) - month
                month = 1 + delta
            else:
                delta += month
                month = self.date.months_in_year(year) + delta"""
            """while not self.date.is_valid_month(year, new_month):
                year += 1 * sign
                if sign == 1:
                    delta -= self.date.months_in_year(year) - month
                    month = 1 + delta
                else:
                    delta += month
                    month = self.date.months_in_year(year) + delta
                new_month = month"""
                # month = 1 if sign == 1 else self.date.months_in_year(year)
            # return self.ast_ymd_to_od((year, new_month, 1))
            return self.ast_ymd_to_od((year, month, 1))
        else:
            raise ValueError(f"Cannot find first day of DateUnit: {dateunit}")'''

    """def raise_interval(self, interval: list) -> list:
        delta, dateunit = interval
        if dateunit == DateUnits.YEAR:
            for idx, this_year_delta in enumerate(self.year_deltas):
                if idx == 0:
                    continue
                if idx == len(self.year_deltas) - 1:
                    delta = self.year_deltas[-1]
                    break

                last_year_delta = self.year_deltas[idx - 1]
                if last_year_delta <= delta < this_year_delta:
                    delta = this_year_delta
                    break
            return [delta, dateunit]
        raise NotImplementedError

    def lower_interval(self, interval: list) -> list:
        delta, dateunit = interval
        if dateunit == DateUnits.YEAR:
            for idx, this_year_delta in enumerate(self.year_deltas):
                if idx == 0:
                    continue
                if idx == len(self.year_deltas) - 1:
                    delta = self.year_deltas[-1]
                    break

                last_year_delta = self.year_deltas[idx - 1]
                if last_year_delta < delta <= this_year_delta:
                    delta = last_year_delta
                    break
            return [delta, dateunit]
        raise NotImplementedError"""

    def change_interval(self, interval: list, increase: bool = True) -> list:
        _, unit = interval
        # todo pass width and choose smallest interval that's greater than this?
        if unit == DateUnits.YEAR:
            return self.change_year_interval(interval, increase)
        elif unit == DateUnits.MONTH:
            return self.change_month_interval(interval, increase)
        elif unit == DateUnits.DAY:
            return self.change_day_interval(interval, increase)
        elif unit == TimeUnits.HOUR:
            return self.change_hour_interval(interval, increase)
        elif unit == TimeUnits.MINUTE:
            return self.change_minute_interval(interval, increase)
        elif unit == TimeUnits.SECOND:
            return self.change_second_interval(interval, increase)
        else:
            RuntimeError(f"{unit} is not a DateUnit or TimeUnit")

    # fixme make change_unit_interval DRY
    def change_year_interval(
        self, interval: list, increase: bool = True
    ) -> list:
        """:raises RuntimeError: if new interval isn't set"""
        delta, unit = interval

        if delta == min(self.year_deltas) and not increase:
            delta = max(self.month_deltas)
            unit = DateUnits.MONTH
            return [delta, unit]

        last_idx = len(self.year_deltas) - 1
        for idx, this_delta in enumerate(self.year_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = self.year_deltas[-1]
                return [delta, unit]

            prev_delta = self.year_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change year interval: {interval}")

    def change_month_interval(self, interval: list, increase: bool = True):
        delta, unit = interval

        if delta == min(self.month_deltas) and not increase:
            delta = min(self.day_deltas)
            unit = DateUnits.DAY
            return [delta, unit]

        last_idx = len(self.month_deltas) - 1
        if last_idx < 0:
            RuntimeError("Can't change interval for monthless calendar")

        for idx, this_delta in enumerate(self.month_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = min(self.year_deltas)
                unit = DateUnits.YEAR
                return [delta, unit]

            prev_delta = self.month_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change month interval: {interval}")

    def change_day_interval(
        self, interval: list, increase: bool = True
    ) -> list:
        delta, unit = interval

        if delta == min(self.day_deltas) and not increase:
            delta = 12
            unit = TimeUnits.HOUR
            return [delta, unit]

        last_idx = len(self.day_deltas) - 1
        for idx, this_delta in enumerate(self.day_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = min(self.month_deltas)
                unit = DateUnits.MONTH
                return [delta, unit]

            prev_delta = self.day_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change day interval: {interval}")

    def change_hour_interval(
        self, interval: list, increase: bool = True
    ) -> list:
        delta, unit = interval
        if delta == min(self.hour_deltas) and not increase:
            delta = max(self.minute_deltas)
            unit = TimeUnits.MINUTE
            return [delta, unit]

        last_idx = len(self.hour_deltas) - 1
        for idx, this_delta in enumerate(self.hour_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = min(self.day_deltas)
                unit = DateUnits.DAY
                return [delta, unit]

            prev_delta = self.hour_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change hour interval: {interval}")

    def change_minute_interval(
        self, interval: list, increase: bool = True
    ) -> list:
        delta, unit = interval
        if delta == min(self.minute_deltas) and not increase:
            delta = max(self.second_deltas)
            unit = TimeUnits.SECOND
            return [delta, unit]

        last_idx = len(self.minute_deltas) - 1
        for idx, this_delta in enumerate(self.minute_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = min(self.hour_deltas)
                unit = DateUnits.DAY
                return [delta, unit]

            prev_delta = self.minute_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change minute interval: {interval}")

    def change_second_interval(
        self, interval: list, increase: bool = True
    ) -> list:
        delta, unit = interval
        if delta == min(self.second_deltas) and not increase:
            return [delta, unit]  # don't go smaller than 1 second interval

        last_idx = len(self.second_deltas) - 1
        for idx, this_delta in enumerate(self.second_deltas):
            if idx == 0:
                continue

            if idx == last_idx and increase:
                delta = min(self.minute_deltas)
                unit = DateUnits.DAY
                return [delta, unit]

            prev_delta = self.second_deltas[idx - 1]
            if prev_delta <= delta < this_delta and increase:
                delta = this_delta
                return [delta, unit]
            if prev_delta < delta <= this_delta and not increase:
                delta = prev_delta
                return [delta, unit]
        raise RuntimeError(f"Failed to change minute interval: {interval}")

    def next_od(self, ordinal_decimal: float, interval: list) -> float:
        _, unit = interval

        if unit in DateUnits:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            ast_ymd = self.date.next_ast_ymd(ast_ymd, interval)
            return self.ast_ymd_to_od(ast_ymd)  # fixme this is causing hr_dates to be wrong for BCE years
        elif unit in TimeUnits:
            hms = self.od_to_hms(ordinal_decimal)
            hms, day_diff = self.time.next_hms(hms, interval)
            """seconds = self.time.hms_to_seconds(hms)
            seconds_decimal = seconds / self.time.clock.seconds_in_day
            return int(ordinal_decimal) + day_diff + seconds_decimal"""
            return self.shift_od_by_hms(ordinal_decimal, hms, day_diff)
        raise RuntimeError(f"Can not shift by {unit}")

    def shift_od_by_hms(
        self,
        ordinal_decimal: float,
        hms: tuple[int, int, int],
        day_diff: int = 0,
    ) -> float:
        seconds = self.time.hms_to_seconds(hms)
        seconds_decimal = seconds / self.time.clock.seconds_in_day
        return int(ordinal_decimal) + day_diff + seconds_decimal

    def ast_ymd_to_od(
        self, ast_ymd: tuple[int, Union[int, None], int]
    ) -> float:
        ordinal_date = self.date.ast_ymd_to_ordinal_date(ast_ymd)
        return float(self.date.ordinal_date_to_ordinal(ordinal_date))

    def od_to_ast_ymd(self, od: float) -> tuple[int, Union[int, None], int]:
        ordinal = int(od)
        ordinal_date = self.date.ordinal_to_ordinal_date(ordinal)
        return self.date.ordinal_date_to_ast_ymd(ordinal_date)

    def od_to_hr_date(self, ordinal_decimal: float, unit) -> str:
        if unit in DateUnits:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            return self.date.format_hr_date(ast_ymd, unit=unit)
        elif unit in TimeUnits:
            hms = self.od_to_hms(ordinal_decimal)
            return self.time.hms_to_hr_time(hms)
        raise RuntimeError(f"{unit} not a valid date or time unit")

    def od_to_hms(self, ordinal_decimal: float) -> tuple[int, int, int]:
        decimal = ordinal_decimal - int(ordinal_decimal)
        seconds = round(self.time.clock.seconds_in_day * decimal)
        hms = self.time.seconds_to_hms(seconds)
        return hms
