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
from .customtime import ConvertibleTime
from typing import Union


class ConvertibleDateTime:
    """
    Manipulates dates and times with ConvertibleDate and ConvertibleTime

    * `Day decimal` - progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` or `od` - an `ordinal` plus a `day decimal`
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
        """increase or decrease interval based on the sign"""
        delta, dateunit = interval
        if dateunit == DateUnits.YEAR:
            if delta == min(self.year_deltas) and not increase:
                delta = max(self.month_deltas)
                dateunit = DateUnits.MONTH
                return [delta, dateunit]

            last_idx = len(self.year_deltas) - 1
            for idx, this_year_delta in enumerate(self.year_deltas):
                if idx == 0:
                    continue
                if idx == last_idx and increase:
                    delta = self.year_deltas[-1]
                    break

                prev_year_delta = self.year_deltas[idx - 1]
                if prev_year_delta <= delta < this_year_delta and increase:
                    delta = this_year_delta
                    break
                if prev_year_delta < delta <= this_year_delta and not increase:
                    delta = prev_year_delta
                    break
            return [delta, dateunit]
        raise NotImplementedError

    def ast_ymd_to_od(
        self, ast_ymd: tuple[int, Union[int, None], int]
    ) -> float:
        ordinal_date = self.date.ast_ymd_to_ordinal_date(ast_ymd)
        return float(self.date.ordinal_date_to_ordinal(ordinal_date))

    def od_to_ast_ymd(self, od: float) -> tuple[int, Union[int, None], int]:
        ordinal = int(od)
        ordinal_date = self.date.ordinal_to_ordinal_date(ordinal)
        return self.date.ordinal_date_to_ast_ymd(ordinal_date)

    def od_to_hr_date(self, ordinal_decimal: float, dateunit=None) -> str:
        ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
        return self.date.format_hr_date(ast_ymd, dateunit=dateunit)
