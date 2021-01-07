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
        self.date = date
        self.time = time

    def next_dateunit(self, od: float, dateunit: int, sign: int = 1) -> float:
        """
        "First of next month", "first of two years ago", etc.
        If today is 2020/11/15, first of next month is 2020/12/1
        If today is 1917/4/3 first of four years ago is 1913/1/1

        A negative`sign` will return a dateunit backwards in time
        """
        year, month, day = self.od_to_ast_ymd(od)
        if dateunit == DateUnits.YEAR:
            year += 1
            return self.ast_ymd_to_od((year, 1, 1))
        elif dateunit == DateUnits.MONTH and month:
            new_month = month + 1
            if self.date.is_valid_month(year, new_month):
                return self.ast_ymd_to_od((year, new_month, 1))

            year += 1 * sign
            month = 1 if sign == 1 else self.date.months_in_year(year)
            return self.ast_ymd_to_od((year, month, 1))
        else:
            raise ValueError(f"Cannot find first day of DateUnit: {dateunit}")

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
