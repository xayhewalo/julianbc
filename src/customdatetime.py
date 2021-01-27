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
from src.customdate import ConvertibleDate, DateUnit, Ymd_tuple
from src.customtime import ConvertibleTime, TimeUnit, Hms_tuple
from typing import Union


class ConvertibleDateTime:
    """
    Manipulates dates and times with ConvertibleDate and ConvertibleTime

    * `Day decimal` is the progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` or `od` is an `ordinal` plus a `day decimal`
    """

    def __init__(self, date: ConvertibleDate, time: ConvertibleTime):
        self.date = date
        self.time = time

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
            day_decimal = self.hms_to_day_decimal(hms)
            ordinal_decimal = int(ordinal_decimal) + day_delta + day_decimal
        return ordinal_decimal

    def ast_ymd_to_od(self, ast_ymd: Ymd_tuple) -> float:
        ordinal_date = self.date.ast_ymd_to_ordinal_date(ast_ymd)
        return float(self.date.ordinal_date_to_ordinal(ordinal_date))

    def od_to_ast_ymd(self, ordinal_decimal: float) -> Ymd_tuple:
        ordinal = int(ordinal_decimal)
        ordinal_date = self.date.ordinal_to_ordinal_date(ordinal)
        return self.date.ordinal_date_to_ast_ymd(ordinal_date)

    def od_to_hms(self, ordinal_decimal: float) -> Hms_tuple:
        decimal = ordinal_decimal - int(ordinal_decimal)
        seconds = round(self.time.clock.seconds_in_day * decimal)
        return self.time.seconds_to_hms(seconds)

    def hms_to_day_decimal(self, hms: Hms_tuple) -> float:
        seconds = self.time.hms_to_seconds(hms)
        return seconds / self.time.clock.seconds_in_day
