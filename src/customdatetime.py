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
from typing import Union


class ConvertibleDateTime:
    """
    Manipulates dates and times ConvertibleDates and ConvertibleTimes

    * `Moment` - Day and time represented as an ordinal and seconds into a day.
    * `Day decimal` is progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` is an `ordinal` plus a `day decimal`
    """

    def __init__(self, date, time):
        self.date = date  # type: from src.customdate import ConvertibleDate
        self.time = time  # type: from src.customtime import ConvertibleTime

    def ast_ymd_to_moment(
        self, ast_ymd: tuple[int, Union[int, None], int]
    ) -> tuple[int, int]:
        ordinal_date = self.date.ast_ymd_to_ordinal_date(ast_ymd)
        ordinal = self.date.ordinal_date_to_ordinal(ordinal_date)
        return ordinal, 0

    def moment_to_ast_ymd(  # todo get rid of moments
        self, moment: tuple[int, int]
    ) -> tuple[int, Union[int, None], int]:
        ordinal, _ = moment
        ordinal_date = self.date.ordinal_to_ordinal_date(ordinal)
        return self.date.ordinal_date_to_ast_ymd(ordinal_date)

    def moment_to_ordinal_decimal(self, moment: tuple[int, int]) -> float:
        ordinal, seconds = moment
        return ordinal + (seconds / self.time.clock.seconds_in_day)

    def moment_to_hr_date(self, moment: tuple[int, int]) -> str:
        ast_ymd = self.moment_to_ast_ymd(moment)
        return self.date.format_hr_date(ast_ymd)

    def elapsed_seconds(
        self, moment1: tuple[int, int], moment2: tuple[int, int]
    ) -> int:
        """:returns: a day decimal"""
        ordinal1, seconds1 = moment1
        ordinal2, seconds2 = moment2
        elapsed_days = ordinal2 - ordinal1
        seconds_in_elapsed_days = elapsed_days * self.time.clock.seconds_in_day
        return seconds2 - seconds1 + seconds_in_elapsed_days

    def split_ordinal_decimal(self, ordinal_decimal: float) -> tuple[int, float]:
        """:returns: ordinal, seconds into a day"""
        ordinal = int(ordinal_decimal)
        seconds = (ordinal_decimal - ordinal) * self.time.clock.seconds_in_day
        return ordinal, seconds
