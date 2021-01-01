"""where the User-interface and database clock-keeping meet"""
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


class ConvertibleTime:
    """
    Manipulate seconds with database clocks.

    * `Seconds` (plural) refers to seconds into a day, not seconds from a
      calendar's epoch.
    * `Second` (singular) refers to the second in a minute.
    * `HMS` stands for the hour, minute, second of a day.
    * `Hour` is always in military time, i.e 24-hour clock on Earth.
    * `HR time` is human-readable time, which may or may not have hour labels
    * `Hour labels` are string like "AM" or "PM"
    Clocks can only be converted if they have the same seconds in a day.

    **not** a drop-in replacement for datetime.clock
    """

    def __init__(self, clock, clock_sep=":", hour_labels=None):
        # fmt: off
        self.clock = clock  # type: from src.models import ConvertibleClock  # noqa: F723, E501
        # fmt: on
        self.clock_sep = clock_sep
        self.hour_labels = hour_labels or list()
        """I.e AM or PM"""
        assert self.are_valid_hour_labels(
            self.hour_labels
        ), f"{self.hour_labels} are invalid day labels"

    def convert_hms(self):
        raise NotImplementedError

    def convertible_clocks(self):
        raise NotImplementedError

    def hms_to_seconds(self, hms: tuple[int, int, int]) -> int:
        hour, minute, second = hms
        return (
            (hour * self.seconds_in_hour())
            + (minute * self.clock.seconds_in_minute)
            + second
        )

    def seconds_to_hms(self, seconds: int) -> tuple[int, int, int]:
        seconds = seconds % self.seconds_in_day()
        hour = self.hour(seconds)
        seconds = seconds % self.seconds_in_hour()
        minute = self.minute(seconds)
        second = seconds % self.clock.seconds_in_minute
        hms = hour, minute, second
        assert self.is_valid_hms(hms), f"{hms} is an invalid hms"
        return hour, minute, second

    def hour(self, seconds: int) -> int:
        """hour of the day"""
        hour = math.trunc(seconds / self.seconds_in_hour())
        assert self.is_valid_hour(hour), f"{hour} is invalid"
        return hour

    def minute(self, seconds: int) -> int:
        """minute of the hour"""
        seconds_in_minute = self.clock.seconds_in_minute
        minute = math.trunc(seconds / seconds_in_minute) % seconds_in_minute
        assert self.is_valid_minute(minute), f"{minute} is invalid"
        return minute

    def seconds_in_hour(self) -> int:
        return self.clock.seconds_in_minute * self.clock.minutes_in_hour

    def seconds_in_day(self) -> int:
        return self.seconds_in_hour() * self.clock.hours_in_day

    def is_valid_hms(self, hms: tuple[int, int, int]) -> bool:
        hour, minute, second = hms
        return (
            self.is_valid_hour(hour)
            and self.is_valid_minute(minute)
            and 0 <= second < self.clock.seconds_in_minute
        )

    def is_valid_hour(self, hour: int) -> bool:
        return 0 <= hour < self.clock.hours_in_day

    def is_valid_minute(self, minute: int) -> bool:
        return 0 <= minute < self.clock.minutes_in_hour

    def hms_to_hr_time(
        self, hms: tuple[int, int, int], use_hour_label=False
    ) -> str:
        hour_digits = len(str(self.clock.hours_in_day))
        minute_digits = len(str(self.clock.minutes_in_hour))
        second_digits = len(str(self.clock.seconds_in_minute))

        hour, minute, second = hms
        minute_str = str(minute).zfill(minute_digits)
        second_str = str(second).zfill(second_digits)

        clock_sep = self.clock_sep
        hour_str = str(hour).zfill(hour_digits)
        if use_hour_label:
            labeled_hour, hour_label = self.labeled_hour(hour)
            hour_str = str(labeled_hour).zfill(hour_digits)
            return clock_sep.join(
                [hour_str, minute_str, second_str, hour_label]
            )
        return clock_sep.join([hour_str, minute_str, second_str])

    def hr_time_to_hms(self, hr_time: str) -> tuple[int, int, int]:
        hour_label = None
        try:
            hour, minute, second, hour_label = hr_time.split(self.clock_sep)
        except ValueError:
            hour, minute, second = hr_time.split(self.clock_sep)

        hour, minute, second = int(hour), int(minute), int(second)
        if hour_label:
            demarcations = self.day_demarcations()
            index = self.hour_labels.index(hour_label)
            hour = int(hour) + demarcations[index]  # from 12 -> 24 hour clock
        return hour, minute, second

    def labeled_hour(self, hour: int) -> tuple[int, str]:
        """
        :returns: hour and the hour label. I.e 2 PM, 6 AM, etc.
        :raises ValueError: if there are no hour labels for this class
        :raises RuntimeError: if no hour label is found
        """
        num_labels = len(self.hour_labels)
        if not num_labels:
            raise ValueError("No hour labels for this ConvertibleTime")

        demarcations = self.day_demarcations()
        hour_label_index = None
        for demarcation_index, this_demarcation in enumerate(demarcations):
            if demarcation_index == 0:
                continue

            last_demarcation = demarcations[demarcation_index - 1]
            if last_demarcation <= hour < this_demarcation:
                hour_label_index = demarcation_index - 1
                break

        if hour_label_index is None:
            raise RuntimeError(f"Unable to find hour label for hour: {hour}")

        labeled_hour = hour - demarcations[hour_label_index]
        return labeled_hour, self.hour_labels[hour_label_index]

    def day_demarcations(self) -> list:
        """i.e [0, 12, 24] for a 12-hour clock"""
        num_labels = len(self.hour_labels)
        hours_in_day = self.clock.hours_in_day
        division_length = int(hours_in_day / num_labels)
        assert (
            int(division_length) == division_length
        ), f"{self.hour_labels} cannot evenly divide {hours_in_day} hours"
        return [hour for hour in range(0, hours_in_day + 1, division_length)]

    def are_valid_hour_labels(self, hour_label: list) -> bool:
        num_labels = len(hour_label)
        if num_labels == 0:
            return True
        return self.clock.hours_in_day % len(hour_label) == 0