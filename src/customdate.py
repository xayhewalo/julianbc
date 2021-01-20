"""Where the User-interface and database date-keeping meet"""
#  Copyright (c) 2020 author(s) of JulianBC.
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
import itertools

from collections import deque
from src.db import ConvertibleCalendar
from typing import Union


class ConvertibleDate:
    """
    Manipulates dates using database calendars.

    * `astronomical year` or `ast_year` is a year using astronomical year
      numbering, where year 0 is **not** skipped.
      In this project, astronomical years are only concerned with two eras.
      Moving forward from a calendar's epoch (I.e Common Era),
      and moving backwards from the epoch (I.e Before Common Era).
      The first astronomical year of calendar is always 1.
    * `human-readable year` or `hr_year` is a year meant to be presented to
      the end-user. I.e the year before the Gregorian Calendar's epoch is year
      0 in astronomical year numbering, but in human readable years, it's 1 BCE
      Human-readable years **must** be non-negative.
    * `ymd` is short for `Year, Month, Day`
    * `hr_date` is a human-readable date including the era.
      I.e "2020/12/2/CE" is December 2nd, 2020 Common Era
    * `leap year` is a year that contains the leap day(s) of a calendar system.
      I.e 2020 is a leap year for the Gregorian Calendar.
    * `common year` is any year that is not a `leap year`. I.e 2019 is a common
      year for the Gregorian Calendar.
    * `ordinal date` is a date in the following format: "Year/Day of Year".
      I.e the ordinal date for November 30th, 2020 is "2020/335" for the
      Gregorian Calendar. `ordinal date` defaults to an astronomical year.
    * `ordinal` is the number of days since the epoch of a calendar.
      This is consistent with :py:mod:`datetime`.
      This is **contrary** to :py:mod:`convertdate`, which calls the
      `ordinal date` an `ordinal`.
    **Not** a drop in replacement for :mod:`date`.
    """

    def __init__(self, calendar: ConvertibleCalendar, date_sep="/"):
        self.date_sep = date_sep
        self.calendar = calendar

    def convert_ast_ymd(
        self,
        foreign_ast_ymd: tuple,
        foreign_datetime: "ConvertibleDate",
    ) -> tuple[int, Union[int, None], int]:
        """:returns: native ast_ymd equivalent to the foreign ast_ymd"""
        foreign_ordinal_date = foreign_datetime.ast_ymd_to_ordinal_date(
            foreign_ast_ymd
        )
        foreign_ordinal = foreign_datetime.ordinal_date_to_ordinal(
            foreign_ordinal_date
        )
        foreign_sync_ordinal = foreign_datetime.calendar.sync_ordinal(
            self.calendar
        )
        elapsed_days = foreign_ordinal - foreign_sync_ordinal

        native_sync_ordinal = self.calendar.sync_ordinal(
            foreign_datetime.calendar
        )
        new_native_ordinal = native_sync_ordinal + elapsed_days
        new_native_ordinal_date = self.ordinal_to_ordinal_date(
            new_native_ordinal
        )
        return self.ordinal_date_to_ast_ymd(new_native_ordinal_date)

    def ordinal_date_to_ordinal(self, ordinal_date: tuple) -> int:
        """
        assumes astronomical year numbering

        :raises ValueError: for an invalid ordinal date
        """
        if not self.is_valid_ordinal_date(ordinal_date):
            raise ValueError(f"{ordinal_date} is invalid for {self.calendar}")

        ast_year, day_of_year = ordinal_date
        ay, sign = self._start_and_sign(ast_year)
        days_in_elapsed_years = 0
        while abs(ay) < abs(ast_year):
            days_in_elapsed_years += self.days_in_year(ay)
            ay = self._increment_by_one(ay, sign)

        ordinal = day_of_year + days_in_elapsed_years
        if self.is_descending_era(ast_year):
            ordinal = -(
                self.days_in_year(ast_year)
                - day_of_year
                + days_in_elapsed_years
            )
        return ordinal

    def ordinal_to_ordinal_date(self, ordinal: int) -> tuple[int, int]:
        ast_year, sign = self._start_and_sign(ordinal)

        days_in_years_passed = self.days_in_year(ast_year)
        while days_in_years_passed < abs(ordinal):
            ast_year = self._increment_by_one(ast_year, sign)
            days_in_years_passed += self.days_in_year(ast_year)
        days_in_years_passed -= self.days_in_year(ast_year)

        day_of_year = abs(ordinal) - days_in_years_passed
        if sign == -1:
            day_of_year = self.days_in_year(ast_year) - day_of_year
            if day_of_year == 0:
                ast_year = self._increment_by_one(ast_year, sign)
                day_of_year = self.days_in_year(ast_year)
        assert self.is_valid_ordinal_date((ast_year, day_of_year)), (
            f"Ordinal, {ordinal}, produced invalid ordinal date, "
            f"{ast_year, day_of_year}, for the {self.calendar} calendar"
        )
        return ast_year, day_of_year

    @staticmethod
    def _start_and_sign(num: int) -> tuple[int, int]:
        """Useful values for calendar calculations"""
        start_value, sign = 1, 1
        if num <= 0:
            start_value, sign = 0, -1
        return start_value, sign

    @staticmethod
    def _increment_by_one(num: int, sign: int) -> int:
        """Add or subtract one based on the sign"""
        return num + sign * 1

    def ast_ymd_to_ordinal_date(self, ast_ymd: tuple) -> tuple[int, int]:
        """:raises ValueError: for an invalid year, month, day"""
        if not self.is_valid_ast_ymd(ast_ymd):
            raise ValueError(
                f"{ast_ymd} is not a valid year, month, day for the "
                f"{self.calendar.name} calendar"
            )

        ast_year, month, day = ast_ymd
        day_of_year = day
        if month:
            day_of_year = sum(self.days_in_months(ast_year)[: month - 1]) + day
        return ast_year, day_of_year

    def ordinal_date_to_ast_ymd(self, ordinal_date: tuple) -> tuple:
        """:raises ValueError: for invalid ordinal date"""
        if not self.is_valid_ordinal_date(ordinal_date):
            raise ValueError(
                f"{ordinal_date} is not a valid ordinal date"
                f"for {self.calendar}"
            )

        ast_year, day_of_year = ordinal_date
        months_in_year = self.months_in_year(ast_year)
        if not months_in_year:
            return ast_year, None, day_of_year

        days_in_months = self.days_in_months(ast_year)
        day = day_of_year
        month = 0
        days_into_year = days_in_months[month]
        while day_of_year - days_into_year > 0:
            day = day_of_year - days_into_year
            month += 1
            days_into_year += days_in_months[month]
        month += 1  # convert from index into human-readable month
        return ast_year, month, day

    def hr_to_ast(self, hr_year: int, era_idx: int) -> int:
        """
        human-readable year to astronomical year.

        :param hr_year: human-readable year
        :param era_idx: index into py:attr:`self.calendar.era_ranges`
        """
        era_range = self.calendar.era_ranges[era_idx]
        era_start_hr_year = float(era_range[0])
        era_end_hr_year = float(era_range[1])
        if era_start_hr_year == float("-inf"):  # in calendar's proleptic era
            return int(-(hr_year - era_end_hr_year))

        years_before_era = 0
        for era_info in self.gen_years_before_era(start=1):
            if era_info["index"] == era_idx:  # don't add this era's length
                break
            years_before_era += era_info["years_in"]

        years_into_current_era = abs(hr_year - era_start_hr_year) + 1
        return int(years_into_current_era + years_before_era)

    def ast_to_hr(self, ast_year: int) -> tuple[int, int]:
        """
        astronomical year to human-readable year

        :returns: human-readable year and index into the calendar's eras
        :raises RuntimeError: if unable to convert
        """
        if ast_year <= 0:  # the proleptic era
            era_idx = 0
            era_end_hr_year = self.calendar.era_ranges[era_idx][1]
            year_since_epoch = abs(ast_year - 1)
            hr_year = era_end_hr_year + year_since_epoch - 1
            return hr_year, era_idx

        for era_info in self.gen_years_before_era(start=1):
            era_idx = era_info["index"]
            era_range = era_info["hr_range"]
            era_start_ast_year, era_end_ast_year = era_info["ast_range"]
            years_before_era = era_info["years_before"]

            era_start_hr_year = float(era_range[0])
            era_end_hr_year = float(era_range[1])
            if era_end_hr_year == float("inf"):  # the last era
                years_into_current_era = ast_year - era_start_ast_year
                hr_year = era_start_hr_year + years_into_current_era
                return int(hr_year), era_idx

            if years_before_era < ast_year <= era_end_ast_year:
                years_into_current_era = ast_year - era_start_ast_year

                # don't use self.is_descending_era, we already know the era
                if era_range[1] > era_range[0]:
                    hr_year = era_start_hr_year + years_into_current_era
                else:
                    hr_year = era_start_hr_year - years_into_current_era
                return int(hr_year), era_idx
        raise RuntimeError(
            f"Unable to convert astronomical year, {ast_year},"
            f"to a human-readable {self.calendar} year"
        )

    def parse_hr_date(self, hr_date: str) -> tuple:
        """
        inverse operation of :py:meth:`format_hr_date`

        :returns: ast_year, month, date. Month is None for monthless calendar
        """
        month = None
        try:
            hr_year, month, day, era = hr_date.split(self.date_sep)
        except ValueError:
            hr_year, day, era = hr_date.split(self.date_sep)

        hr_year = int(hr_year)
        month = int(month) if month is not None else month
        day = int(day)

        era_idx = self.calendar.eras.index(era)
        ast_year = self.hr_to_ast(hr_year, era_idx)
        return ast_year, month, day

    def format_hr_date(self, ast_ymd: tuple) -> str:
        """inverse operation of :py:meth:`parse_hr_date`"""
        ast_year, month, day = ast_ymd
        hr_year, _ = self.ast_to_hr(ast_year)
        era = self.era(ast_year)
        return self.date_sep.join([str(hr_year), str(month), str(day), era])

    def era(self, ast_year: int) -> str:
        """:raises RuntimeError: If no era found"""
        if ast_year <= 0:  # is proleptic era
            return self.calendar.eras[0]

        years_before_era = 0
        for era_info in self.gen_years_before_era(start=1):
            era_idx = era_info["index"]
            years_in_era = era_info["years_in"]
            era_start_ast_year, era_end_ast_year = era_info["ast_range"]

            if era_start_ast_year <= ast_year <= era_end_ast_year:
                return self.calendar.eras[era_idx]
            years_before_era += years_in_era
        raise RuntimeError(
            f"Could not find {self.calendar} era for year: {ast_year}"
        )

    def is_descending_era(self, ast_year: int) -> bool:
        era = self.era(ast_year)
        era_range = self.calendar.era_ranges[self.calendar.eras.index(era)]
        return abs(float(era_range[0])) > abs(float(era_range[1]))

    def is_leap_year(self, ast_year: int) -> bool:
        if not self.calendar.has_leap_year:
            return False

        if ast_year in self.calendar.special_common_years:
            return False
        if ast_year in self.calendar.special_leap_years:
            return True

        start = self.calendar.leap_year_cycle_start
        cycle_ordinals = deque(  # contains every year in each cycle
            itertools.chain.from_iterable(
                [
                    range(start, cycle + start)
                    for cycle in self.calendar.leap_year_cycles
                ]
            )
        )
        cycle_ordinals.rotate(self.calendar.leap_year_offset)
        cycle_length = len(cycle_ordinals)

        start_ast_year = 1
        ast_year_sign = 1
        if ast_year <= 0:
            start_ast_year = 0
            ast_year_sign = -1
            cycle_ordinals.reverse()

        completed_years = abs(ast_year - start_ast_year)
        completed_cycles = math.trunc(completed_years / cycle_length)

        current_cycle_start_ast_year = (
            (completed_cycles * cycle_length) + start_ast_year
        ) * ast_year_sign
        cycle_index = abs(ast_year) - abs(current_cycle_start_ast_year)
        leap_year_cycle_ordinals = self.calendar.leap_year_cycle_ordinals
        return cycle_ordinals[cycle_index] in leap_year_cycle_ordinals

    def is_valid_ast_ymd(self, ast_ymd: tuple) -> bool:
        ast_year, month, day = ast_ymd
        max_days = self.days_in_year(ast_year)
        if month:
            max_months = self.months_in_year(ast_year)
            if not 1 <= month <= max_months:
                return False
            max_days = self.days_in_months(ast_year)[month - 1]
        return 1 <= day <= max_days

    def is_valid_ordinal_date(self, ordinal_date: tuple) -> bool:
        """assumes astronomical year numbering"""
        ast_year, day_of_year = ordinal_date
        return 1 <= day_of_year <= self.days_in_year(ast_year)

    def gen_years_before_era(self, start: int = 0) -> dict:
        """
        Generator for useful values related to an era range

        :param start: Index to start iterating from.
            **Includes** era range at this index.
        :returns: the era range, index into the era range, years in the era,
            and sum of years in previous eras.
            Years in the era can be an integer or infinity.
            Sum of years in previous eras **skips** infinite eras.
        """
        for era_idx, era_range in enumerate(
            self.calendar.era_ranges[start:], start=start
        ):
            years_before_era = sum(
                abs(float(era_range[1]) - float(era_range[0])) + 1
                for era_range in self.calendar.era_ranges[1:era_idx]
            )
            start_hr_year = float(era_range[0])
            end_hr_year = float(era_range[1])
            years_in_era = abs(end_hr_year - start_hr_year) + 1

            ast_range = (
                years_before_era + 1,
                years_before_era + years_in_era,
            )
            if start_hr_year == float("-inf"):
                ast_range = (float("-inf"), 0)
            yield {
                "index": era_idx,
                "hr_range": era_range,
                "ast_range": ast_range,
                "years_in": years_in_era,
                "years_before": years_before_era,
            }

    def days_in_months(self, ast_year: int) -> tuple:
        if self.is_leap_year(ast_year):
            return self.calendar.days_in_leap_year_months
        return self.calendar.days_in_common_year_months

    def days_in_year(self, ast_year: int) -> int:
        if self.is_leap_year(ast_year):
            return sum(self.calendar.days_in_leap_year_months)
        return sum(self.calendar.days_in_common_year_months)

    def months_in_year(self, ast_year: int) -> int:
        if self.is_leap_year(ast_year):
            return len(self.calendar.leap_year_month_names)
        return len(self.calendar.common_year_month_names)

    def day_of_week(self, ordinal: int) -> Union[int, None]:
        """
        :returns: index into :py:attr:`calendar.weekday_names` or None if
        calendar has no weeks
        """
        days_in_weeks = self.calendar.days_in_weeks
        if days_in_weeks:
            return (ordinal + self.calendar.epoch_weekday - 1) % days_in_weeks
