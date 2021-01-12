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

from enum import Enum, unique
from sqlalchemy.future import select
from sqlalchemy.orm import object_session
from src.models import ConvertibleClock
from .utils import _increment_by_one


@unique
class TimeUnits(Enum):
    HOUR = 0
    MINUTE = 1
    SECOND = 2


class ConvertibleTime:
    """
    Manipulate seconds with database clocks.

    * `Seconds` (plural) refers to seconds into a day, not seconds from a
      calendar's epoch.
    * `Second` (singular) refers to the second in a minute.
    * `HMS` stands for the hour, minute, second of a day.
    * `Hour` is always in military time, i.e 24-hour clock on Earth.
    * `HR time` is human-readable time, which may or may not have hour labels
    * `Hour labels` are strings like "AM" or "PM"
    Clocks can only be converted if they have the same seconds in a day.

    **not** a drop-in replacement for datetime.time
    """

    def __init__(
        self, clock: ConvertibleClock, clock_sep=":", hour_labels=None
    ):
        self.clock = clock
        self.clock_sep = clock_sep
        self.hour_labels = hour_labels or list()
        """I.e AM or PM"""
        assert self.are_valid_hour_labels(
            self.hour_labels
        ), f"{self.hour_labels} are invalid day labels"

    def convert_hms(
        self,
        foreign_hms: tuple[int, int, int],
        foreign_time: "ConvertibleTime",
    ) -> tuple[int, int, int]:
        foreign_clock = foreign_time.clock
        if foreign_clock not in self.convertible_clocks():
            raise ValueError(f"{foreign_clock} cannot be converted to {self}")

        seconds = foreign_time.hms_to_seconds(foreign_hms)
        return self.seconds_to_hms(seconds)

    def next_hms(  # todo break up into smaller functions, also is really gross
        self, hms: tuple[int, int, int], interval: list, sign: int = 1
    ) -> tuple[tuple[int, int, int], int]:
        """:returns: desired hms and whether it is in a different day"""
        # todo convert to hms and frequeny to seconds and find modulo == 0?
        """
        i.e:
        frequency_seconds = frequency * unit * seconds_in_unit
        seconds = self.hms_to_seconds(hms)
        seconds += sign * 1
        seconds_shifted = 0
        while seconds % frequency_seconds != 0:
            seconds_shifted += 1
            seconds += 1
        assert seconds_shifted <= seconds_in_day
        if seconds_shifted >= seconds_in_day:
            day_diff = 1
            
        hms = self.seconds_to_hms(seconds
        return hms, day_diff
        """
        if not self.is_valid_hms(hms):
            raise ValueError(f"{hms} is an invalid hms for {self.clock}")

        frequency, unit = interval

        if not 0 < frequency == int(frequency):  # todo same in next_ast_ymd
            msg = f"Frequency: {frequency} is not an integer greater than zero"
            raise ValueError(msg)

        hour, minute, second = hms
        day_diff = 0

        if unit == TimeUnits.HOUR:
            if frequency > self.clock.hours_in_day - 1:
                msg = f"Can't find every {frequency} hour for {self.clock}"
                raise ValueError(msg)

            hour = _increment_by_one(hour, sign)
            if not self.is_valid_hour(hour):
                hour = 0
                day_diff = sign

            while hour % frequency != 0:
                hour = _increment_by_one(hour, sign)
                if not self.is_valid_hour(hour):  # todo probs don't have to check twice
                    assert not day_diff, "shifted into a different day twice"
                    hour = 0
                    day_diff = sign
            return (hour, 0, 0), day_diff
        elif unit == TimeUnits.MINUTE:
            if frequency > self.clock.minutes_in_hour - 1:
                msg = f"Can't find every {frequency} minute for {self.clock}"
                raise ValueError(msg)

            minute += sign * 1
            if not self.is_valid_minute(minute):
                minute = 0
                hour += sign * 1
                if not self.is_valid_hour(hour):
                    hour = 0
                    day_diff = sign

            while minute % frequency != 0:
                minute += sign * 1
                if not self.is_valid_minute(minute):
                    minute = 0
                    hour += sign * 1
                    if not self.is_valid_hour(hour):
                        assert not day_diff, "moved into a different day twice"
                        hour = 0
                        day_diff = sign
            return (hour, minute, 0), day_diff
        elif unit == TimeUnits.SECOND:
            if frequency > self.clock.seconds_in_minute - 1:
                msg = f"Can't find every {frequency} second for {self.clock}"
                raise ValueError(msg)

            second += sign * 1
            if not self.is_valid_second(second):
                second = 0
                minute += sign * 1
                if not self.is_valid_minute(minute):
                    minute = 0
                    hour += sign * 1
                    if not self.is_valid_hour(hour):
                        hour = 0
                        day_diff = sign

            while second % frequency != 0:
                second += sign * 1
                if not self.is_valid_second(second):
                    second = 0
                    minute += sign * 1
                    if not self.is_valid_minute(minute):
                        minute = 0
                        hour += sign * 1
                        if not self.is_valid_hour(hour):
                            assert not day_diff, "moved days twice"
                            hour = 0
                            day_diff = sign
            return (hour, minute, second), day_diff
        else:
            raise ValueError(f"{unit} is an invalid TimeUnit")

    def shift_hms(  # todo break up into different functions
        self, hms: tuple[int, int, int], intervals: list
    ) -> tuple[tuple[int, int, int], int]:
        """

        :param hms: hour, minute, second
        :param intervals: amount of TimeUnits to shift by
        :returns: an hms and whether the shift moved into a different day
        """
        if not self.is_valid_hms(hms):
            msg = f"{hms} is invalid for {self.clock}"
            raise ValueError(msg)

        hour, minute, second = hms
        day_diff = 0

        for interval in intervals:
            delta, unit = interval
            if delta == 0:
                continue

            sign = int(math.copysign(1, delta))
            if unit == TimeUnits.HOUR:  # todo DRY
                terminal_hour = 0 if sign == 1 else self.clock.hours_in_day

                new_hour = hour + delta
                while not self.is_valid_hour(new_hour):  # todo test every 24 hours returns 0, not 24
                    day_diff += sign * 1
                    if sign == 1:
                        delta -= self.clock.hours_in_day - hour
                    else:
                        delta += hour
                    hour = terminal_hour
                    new_hour = hour + delta
                hour = new_hour
                assert self.is_valid_hms(
                    (hour, minute, second)
                ), f"{hour, minute, second} is invalid for {self.clock}"
                return (hour, minute, second), day_diff  # fixme wrong because it won't shift be all the date units
            elif unit == TimeUnits.MINUTE:
                minutes_in_hour = self.clock.minutes_in_hour
                terminal_minute = 0 if sign == 1 else minutes_in_hour

                new_minute = minute + delta
                while not self.is_valid_minute(new_minute):
                    hour += sign * 1
                    if not self.is_valid_hour(hour):  # fixme DRY
                        day_diff += sign * 1
                        hour = 0 if sign == 1 else self.clock.hours_in_day  # todo DRY?

                    if sign == 1:
                        delta -= minutes_in_hour - minute
                    else:
                        delta += minute
                    minute = terminal_minute
                    new_minute = minute + delta
                minute = new_minute
                assert self.is_valid_hms(
                    (hour, minute, second)
                ), f"{hour, minute, second} is invalid for {self.clock}"
                return (hour, minute, second), day_diff
            elif unit == TimeUnits.SECOND:
                seconds_in_minute = self.clock.seconds_in_minute
                terminal_second = 0 if sign == 1 else seconds_in_minute

                new_second = second + delta
                while not self.is_valid_second(new_second):
                    minute += sign * 1
                    if not self.is_valid_minute(minute):
                        minute = 0 if sign == 1 else self.clock.minutes_in_hour
                        hour += sign * 1
                        if not self.is_valid_hour(hour):
                            hour = 0 if sign == 1 else self.clock.hours_in_day
                            day_diff += sign * 1

                    if sign == 1:
                        delta -= seconds_in_minute - second
                    else:
                        delta += second
                    second = terminal_second
                    new_second = second + delta
                second = new_second
                if not self.is_valid_hms((hour, minute, second)):
                    print(hour, minute, second)
                assert self.is_valid_hms(
                    (hour, minute, second)
                ), f"{hour, minute, second} is invalid for {self.clock}"
                return (hour, minute, second), day_diff
            else:
                RuntimeError(f"{unit} is an invalid TimeUnit")

    def convertible_clocks(self) -> list:  # todo move to db?, property?
        session = object_session(self.clock)
        return (
            session.execute(
                select(ConvertibleClock).filter(
                    ConvertibleClock.seconds_in_day
                    == self.clock.seconds_in_day,
                    ConvertibleClock.id != self.clock.id,
                )
            )
            .scalars()
            .all()
        )

    def hms_to_seconds(self, hms: tuple[int, int, int]) -> int:
        hour, minute, second = hms
        return (
            (hour * self.clock.seconds_in_hour)
            + (minute * self.clock.seconds_in_minute)
            + second
        )

    def seconds_to_hms(self, seconds: int) -> tuple[int, int, int]:
        seconds = seconds % self.clock.seconds_in_day
        hour = self.hour(seconds)
        seconds = seconds % self.clock.seconds_in_hour
        minute = self.minute(seconds)
        second = seconds % self.clock.seconds_in_minute
        hms = hour, minute, second
        assert self.is_valid_hms(hms), f"{hms} is an invalid hms"
        return hour, minute, second

    def hour(self, seconds: int) -> int:
        """hour of the day"""
        hour = math.trunc(seconds / self.clock.seconds_in_hour)
        assert self.is_valid_hour(hour), f"{hour} is invalid"
        return hour

    def minute(self, seconds: int) -> int:
        """minute of the hour"""
        seconds_in_minute = self.clock.seconds_in_minute
        minute = math.trunc(seconds / seconds_in_minute) % seconds_in_minute
        assert self.is_valid_minute(minute), f"{minute} is invalid"
        return minute

    def is_valid_hms(self, hms: tuple[int, int, int]) -> bool:
        hour, minute, second = hms
        return (
            self.is_valid_hour(hour)
            and self.is_valid_minute(minute)
            # and 0 <= second < self.clock.seconds_in_minute
            and self.is_valid_second(second)
        )

    def is_valid_hour(self, hour: int) -> bool:
        return 0 <= hour < self.clock.hours_in_day

    def is_valid_minute(self, minute: int) -> bool:
        return 0 <= minute < self.clock.minutes_in_hour

    def is_valid_second(self, second: int) -> bool:
        return 0 <= second < self.clock.seconds_in_minute

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

        max_hr_hour = self.max_hr_hour()
        hour_index = (hour % max_hr_hour) - 1
        labeled_hour = range(1, max_hr_hour + 1)[hour_index]
        return labeled_hour, self.hour_labels[hour_label_index]

    def day_demarcations(self) -> list:
        """i.e [0, 12, 24] for a 12-hour clock"""
        hours_in_day = self.clock.hours_in_day
        max_hr_hour = self.max_hr_hour()
        return [hour for hour in range(0, hours_in_day + 1, max_hr_hour)]

    def max_hr_hour(self) -> int:
        """:raises AssertionError: if max_hr_hour is not a whole number"""
        max_hr_hour = self.clock.hours_in_day / len(self.hour_labels)
        assert (
            int(max_hr_hour) == max_hr_hour
        ), f"Max hr hour must be a whole number: {max_hr_hour} is not"
        return int(max_hr_hour)

    def are_valid_hour_labels(self, hour_label: list) -> bool:
        num_labels = len(hour_label)
        if num_labels == 0:
            return True
        # return self.clock.hours_in_day % len(hour_label) == 0
        return self.clock.hours_in_day % num_labels == 0
