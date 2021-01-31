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
import math

from src.customdate import ConvertibleDate, DateUnit, Ymd_tuple
from src.customtime import ConvertibleTime, TimeUnit, Hms_tuple
from src.ui.timeline import Timeline
from typing import Union

DateTime_interval = list[int, Union[DateUnit, TimeUnit]]


class ConvertibleDateTime:
    """
    Manipulates dates and times with ConvertibleDate and ConvertibleTime

    * `Day decimal` is the progress into a day. 0.5 represents 12 noon on Earth
    * `Ordinal decimal` or `od` is an `ordinal` plus a `day decimal`
    """

    def __init__(self, date: ConvertibleDate, time: ConvertibleTime):
        self.date = date
        self.time = time
        self.initial_interval = [1, DateUnit.DAY]
        self.datetime_units = list(DateUnit)
        self.datetime_units.extend(TimeUnit)  # largest to smallest

    def change_interval(
        self,
        interval: DateTime_interval,
        timeline: Timeline,
        increase=True,
        recursive=False,
    ) -> list:
        """# increase delta until the new_interval width is > interval_width
            start_od = timeline.start_od
            start_x = timeline.od_to_x(start_od)
            assert start_x == 0, f"start_x should be 0, it's {start_x}"

            sign = 1 if increase else -1
            # delta = 5 * sign
            if frequency == 1:
                delta = 2
            elif frequency == 2:
                delta = 5
            else:
                delta = 5
            new_frequency = frequency + (delta - (frequency % delta))
            new_od = self.shift_od(start_od, [[new_frequency, unit]])
            new_width = timeline.od_to_x(new_od)
            mark = timeline.ids["mark"]
            label_width = mark.max_label_width + (2 * mark.label_padding_x)
            while label_width / new_width >= 0.5:  # fixme
                new_frequency += delta
                new_od = self.shift_od(start_od, [[new_frequency, unit]])
                new_width = timeline.od_to_x(new_od)
            return [new_frequency, unit]"""

        frequency, unit = interval
        frequencies = self.get_frequencies(unit)
        max_frequency = max(frequencies)
        min_frequency = min(frequencies)
        increase_unit = increase and frequency == max_frequency
        decrease_unit = not increase and frequency == min_frequency
        unit_idx = self.datetime_units.index(unit)

        if increase_unit:
            if unit == DateUnit.YEAR:
                raise ValueError("Interval unit can't be more than a year")

            err_msg = "year must be last datetime_unit"
            assert self.datetime_units[0] == DateUnit.YEAR, err_msg

            bigger_unit = self.datetime_units[unit_idx - 1]
            frequency = min(self.get_frequencies(bigger_unit))
            interval = [frequency, bigger_unit]
            return self.change_interval(interval, timeline, increase, True)
        elif decrease_unit:
            if unit == TimeUnit.SECOND:
                raise ValueError("Interval unit can't be less than a second")

            err_msg = "second must be last datetime_unit"
            assert self.datetime_units[-1] == TimeUnit.SECOND, err_msg

            smaller_unit = self.datetime_units[unit_idx + 1]
            frequency = max(self.get_frequencies(smaller_unit))
            interval = [frequency, smaller_unit]
            return self.change_interval(interval, timeline, increase, True)

        sign = 1 if increase else -1
        new_frequency = frequency
        if not recursive:
            idx = frequencies.index(frequency)
            new_idx = idx + sign
            new_frequency = frequencies[new_idx]

        start_od = timeline.start_od
        start_x = timeline.od_to_x(start_od)
        assert start_x == 0, f"start_od should be at x = 0, it's {start_x}"

        new_od = self.extend_od(start_od, [new_frequency, unit])
        new_width = timeline.od_to_x(new_od)
        mark = timeline.ids["mark"]
        label_width = mark.max_label_width + (2 * mark.label_padding_x)  # FIXME dry draw_marks?
        while label_width / new_width >= 0.5:  # fixme
            idx = frequencies.index(new_frequency)
            new_idx = idx + sign
            new_frequency = frequencies[new_idx]
            new_od = self.extend_od(start_od, [new_frequency, unit])
            new_width = timeline.od_to_x(new_od)
        return [new_frequency, unit]

    def get_frequencies(self, unit: Union[DateUnit, TimeUnit]) -> list:
        def exclusive_divisors(num: int) -> list:
            """:returns: divisors of `num` excluding `num`"""
            divs = {1}
            for i in range(2, int(math.sqrt(num)) + 1):
                if num % i == 0:
                    divs.update((i, num // i))
            return list(divs)

        if unit == DateUnit.YEAR:  # fixme
            return [
                1, 2, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000,
                7500, 10_000, 25_000, 50_000, 75_000, 100_000,
            ]
        elif unit == DateUnit.MONTH:
            num_common_months = self.date.calendar.months_in_common_year
            num_leap_months = self.date.calendar.months_in_leap_year
            least_months_in_year = min(num_common_months, num_leap_months)
            return exclusive_divisors(least_months_in_year)
        elif unit == DateUnit.DAY:
            calendar = self.date.calendar
            min_common_month_len = min(calendar.days_in_common_year_months)
            min_leap_month_len = min(calendar.days_in_leap_year_months)
            min_days_in_month = min(min_leap_month_len, min_common_month_len)
            multiples_of_five = list(range(0, min_days_in_month + 1, 5))
            multiples_of_five.remove(0)
            frequencies = [1, 2]
            frequencies.extend(multiples_of_five)
            return frequencies
        elif unit == TimeUnit.HOUR:
            return exclusive_divisors(self.time.clock.hours_in_day)
        elif unit == TimeUnit.MINUTE:
            return exclusive_divisors(self.time.clock.minutes_in_hour)
        elif unit == TimeUnit.SECOND:
            return exclusive_divisors(self.time.clock.seconds_in_minute)
        raise ValueError(f"Cannot find valid frequencies for {unit}")

    def extend_od(
        self,
        ordinal_decimal: float,
        interval: list,
        factor: int = 1,
        reverse=False,
    ) -> float:
        """
        convenience method to extend start and end ordinals using shift_od
        :raises ValueError: factor <= 0
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

    def next_od(self, ordinal_decimal: float, interval: list) -> float:
        """Ordinal decimal variation of next_ast_ymd and next_hms"""
        _, unit = interval

        if unit in DateUnit:
            ast_ymd = self.od_to_ast_ymd(ordinal_decimal)
            ast_ymd = self.date.next_ast_ymd(ast_ymd, interval)
            return self.ast_ymd_to_od(ast_ymd)
        elif unit in TimeUnit:
            hms = self.od_to_hms(ordinal_decimal)
            hms, day_delta = self.time.next_hms(hms, interval)
            ordinal_decimal = self.set_hms(ordinal_decimal, hms, day_delta)
            return ordinal_decimal
        raise ValueError(f"Can't shift ordinal decimal by {unit}")

    def od_to_hr_date(self, ordinal_decimal: float, unit) -> str:
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
