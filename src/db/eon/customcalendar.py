"""Date-tracking models"""
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
import itertools

from src.db import utils
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    CheckConstraint,
    event,
    ForeignKey,
    func,
    Integer,
    JSON,
    Unicode,
)
from sqlalchemy.orm import column_property, relationship, Session, validates
from typing import Union


def default_eras() -> list[str, str]:
    return ["BCE", "CE"]


def default_era_ranges() -> list[list[str, int], list[str, str]]:
    """Inclusive end and start human-readable(ish) years for default era"""
    return [["-inf", 1], [1, "inf"]]


class ConvertibleCalendar(utils.Base):
    """User-Defined Calendars"""

    __tablename__ = "convertible_calendar"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)

    #
    # Weeks
    #
    weekday_names = Column(
        JSON,
        CheckConstraint(
            """
            json_array_length(weekday_names) == 0
            OR
            (
                epoch_weekday IS NOT NULL
                AND weekday_start IS NOT NULL
            )
            """,
            name=f"ck_{__tablename__}_weekday_names",
        ),
        default=list,
        nullable=False,
    )

    @validates("weekday_names")
    def _sanitize_weekday_names(self, _, weekday_names: list) -> list:
        return list(utils.string_sanitization(weekday_names))

    days_in_weeks = column_property(func.json_array_length(weekday_names))
    epoch_weekday = Column(  # index into weekday names
        Integer,
        CheckConstraint(
            """
            (   -- calendar has weeks
                epoch_weekday >= 0
                AND epoch_weekday < json_array_length(weekday_names)
            )
            OR
            (
                -- weekless calendar
                json_array_length(weekday_names) == 0
                AND epoch_weekday IS NULL
            )
            """,
            name=f"ck_{__tablename__}_epoch_weekday",
        ),
    )
    weekday_start = Column(
        Integer,
        CheckConstraint(
            """
            (   -- calendar has weeks
                weekday_start >= 0
                AND weekday_start < json_array_length(weekday_names)
            )
            OR
            (
                -- weekless calendar
                json_array_length(weekday_names) == 0
                AND weekday_start IS NULL
            )
            """,
            name=f"ck_{__tablename__}_weekday_start",
        ),
    )
    weekends = Column(JSON, default=list, nullable=False)

    @validates("weekends")
    def _validate_weekends(self, _, weekends: list) -> list:
        if len(self.weekday_names) == 0:
            assert len(weekends) == 0
            return weekends

        for idx in weekends:
            assert 0 <= idx < len(self.weekday_names), "invalid weekend index"
        return utils.integer_sanitization(weekends)

    #
    # Common years
    #
    common_year_month_names = Column(
        JSON,
        CheckConstraint(
            """
            (   -- a calendar with months
                json_array_length(common_year_month_names)
                == json_array_length(days_in_common_year_months)
            )
            OR
            (   -- a monthless calendar
                json_array_length(common_year_month_names) == 0
                AND json_array_length(days_in_common_year_months) == 1
            )
            """,
            name=f"ck_{__tablename__}_common_months",
        ),
        default=list,
        nullable=False,
    )
    months_in_common_year = column_property(
        func.json_array_length(common_year_month_names)
    )
    days_in_common_year_months = Column(JSON, nullable=False)

    #
    # Leap years
    #
    """
    There are two main ways calendars determine leap years: cycles and
    divisibility. For example, the Hebrew calendar has a 19-year cycle where
    the cycle years 3, 6, 8, 11, 14, 17, and 19 are leap years. In contrast,
    for the Gregorian Calendar, leap years are divisible by 400 or divisible by
    4 but not 100. Instead of having two separate systems, this class
    represents divisible "leap year rules" using "leap year cycles". The
    Gregorian calendar's divisibility rules can be represented as a 400 year
    cycle with the following cycle years being leap years:
    4, 8, 12, 16, 20, ..., 96, 104, ..., 196, 204, ..., 296, 304, ..., 396, 400
    """
    has_leap_year = Column(Boolean(create_constraint=True), default=False)
    leap_year_month_names = Column(
        JSON,
        CheckConstraint(
            """
            (   -- calendar with months and leap years
                has_leap_year == 1
                AND
                (
                    json_array_length(leap_year_month_names)
                    == json_array_length(days_in_leap_year_months)
                )
            )
            OR
            (
                -- calendar has leap years, but no months
                has_leap_year == 1
                AND json_array_length(leap_year_month_names) == 0
                AND json_array_length(days_in_leap_year_months) == 1
            )
            OR
            (   -- calendar has no leap years
                has_leap_year == 0
                AND json_array_length(leap_year_month_names) == 0
                AND json_array_length(days_in_leap_year_months) == 0
            )
            """,
            name=f"ck_{__tablename__}_leap_months",
        ),
        default=list,
        nullable=False,
    )
    months_in_leap_year = column_property(
        func.json_array_length(leap_year_month_names)
    )
    days_in_leap_year_months = Column(JSON, default=list, nullable=False)

    @validates("common_year_month_names", "leap_year_month_names")
    def _sanitize_month_names(self, _, month_names: list) -> list:
        return utils.string_sanitization(month_names)

    @validates("days_in_common_year_months", "days_in_leap_year_months")
    def _validate_days_in_months(self, key, days_in_months: list) -> list:
        assert all([days > 0 for days in days_in_months]), "days must be > 0"
        if days_in_months:  # skip if days_in_months is empty
            assert sum(days_in_months) > 0, f"{key} can not have zero days"
        return utils.integer_sanitization(days_in_months)

    leap_year_cycles = Column(
        JSON,
        CheckConstraint(
            """
            (
                has_leap_year == 1
                AND json_array_length(leap_year_cycles) != 0
                AND json_array_length(leap_year_cycle_ordinals) != 0
                AND leap_year_cycle_start IS NOT NULL
            )
            OR
            (
                has_leap_year == 0
                AND json_array_length(leap_year_cycles) == 0
                AND json_array_length(leap_year_cycle_ordinals) == 0
                AND leap_year_cycle_start IS NULL
            )
            """,
            name=f"ck_{__tablename__}_leap_year_cycles",
        ),
        default=list,
        nullable=False,
    )

    @validates("leap_year_cycles")
    def _validate_leap_cycles(self, _, leap_year_cycles: list) -> list:
        sanitized_cycles = utils.integer_sanitization(leap_year_cycles)
        for cycle in sanitized_cycles:
            assert cycle >= 1, "leap year cycles must be positive"
        return sanitized_cycles

    leap_year_cycle_start = Column(
        Integer,
        CheckConstraint(
            "leap_year_cycle_start >=0",
            name=f"ck_{__tablename__}_leap_year_cycle_start",
        ),
    )
    leap_year_cycle_ordinals = Column(JSON, default=list, nullable=False)

    @validates("leap_year_cycle_ordinals")
    def _validate_cycle_ordinals(self, _, cycle_ordinals: list) -> list:
        sanitized_cycle_ordinals = utils.integer_sanitization(cycle_ordinals)
        for cycle_ordinal in sanitized_cycle_ordinals:
            assert cycle_ordinal >= 0, "cycle ordinals must be non-negative"
        return sanitized_cycle_ordinals

    special_common_years = Column(  # common years no matter leap year rules
        JSON,
        CheckConstraint(
            """
            has_leap_year == 1
            OR json_array_length(special_common_years) == 0
            """,
            name=f"ck_{__tablename__}_leap_year_exceptions",
        ),
        default=list,
        nullable=False,
    )
    special_leap_years = Column(  # leap years no matter leap year rules
        JSON,
        CheckConstraint(
            """
            has_leap_year == 1
            OR json_array_length(special_leap_years) == 0
            """,
            name=f"ck_{__tablename__}_leap_year_overrules",
        ),
        default=list,
        nullable=False,
    )
    leap_year_offset = Column(
        Integer,
        CheckConstraint(
            "has_leap_year == 1 OR leap_year_offset IS NULL",
            name=f"ck_{__tablename__}_leap_year_offset",
        ),
    )

    @staticmethod
    def validate_disjoint_special_years(_, __, target: "ConvertibleCalendar"):
        """
        :raises AssertionError: if special_common_years and special_leap_years
            are **not** mutually exclusive
        """
        if target.special_common_years and target.special_leap_years:
            special_leap = set(target.special_leap_years)
            special_commons = set(target.special_common_years)
            disjoint_special_years = special_leap.isdisjoint(special_commons)
            assert disjoint_special_years, "special years must be disjoint"

    #
    # Eras, assumes human-readable years
    #
    eras = Column(
        JSON,
        CheckConstraint(
            """
            json_array_length(eras) >= 2
            AND json_array_length(eras) == json_array_length(era_ranges)
            """,
            name=f"ck_{__tablename__}_eras",
        ),
        default=default_eras,
        nullable=False,
    )
    era_ranges = Column(JSON, default=default_era_ranges, nullable=False)

    @validates("era_ranges")
    def _validate_era_ranges(self, _, era_ranges: list) -> list:
        flat_era_ranges = list(itertools.chain.from_iterable(era_ranges))
        assert flat_era_ranges[0] == "-inf", "first era must be infinite"
        assert flat_era_ranges[-1] == "inf", "last era must be infinite"

        finite_era_ranges = utils.integer_sanitization(flat_era_ranges[1:-1])
        for hr_year in finite_era_ranges:
            assert hr_year >= 0, "human-readable years must be non-negative"
        return era_ranges

    jd_epoch = Column(Integer, default=1721426)  # Julian Day of the epoch
    # should just be used to convert calendars

    _target_conversions = relationship(  # from self to target
        "CalendarConversion",
        primaryjoin="ConvertibleCalendar.id==CalendarConversion.source_calendar_id",  # noqa: E501
        back_populates="source_calendar",
    )
    _source_conversions = relationship(  # from source to self
        "CalendarConversion",
        primaryjoin="ConvertibleCalendar.id==CalendarConversion.target_calendar_id",  # noqa: E501
        back_populates="target_calendar",
    )

    def __repr__(self):
        return f"{self.name}(Epoch: {self.jd_epoch})"

    def calendars(self) -> list:
        """All the calendars this one can be converted to and from"""
        target_calendars = [
            conversion.target_calendar
            for conversion in self._target_conversions
        ]
        source_calendars = [
            conversion.source_calendar
            for conversion in self._source_conversions
        ]
        calendars = list(itertools.chain(target_calendars, source_calendars))
        return calendars

    def conversions(self) -> list:
        """All conversions this calendar is involved in"""
        conversions = list(
            itertools.chain(self._source_conversions, self._target_conversions)
        )
        return conversions

    def sync_ordinal(self, cal: "ConvertibleCalendar") -> Union[int, None]:
        """:returns: this calendar's sync ordinal for the given calendar"""
        conversion = self.conversion(cal)
        if conversion is None:
            return None

        if conversion.target_calendar is self:
            return conversion.target_sync_ordinal
        return conversion.source_sync_ordinal

    def conversion(
        self, calendar: "ConvertibleCalendar"
    ) -> Union["CalendarConversion", None]:
        """:returns: CalendarConversion for this and the given calendar"""
        conversions = self.conversions()
        for conversion in conversions:
            if {conversion.target_calendar, conversion.source_calendar} == {
                self,
                calendar,
            }:
                return conversion
        return None


event.listen(
    ConvertibleCalendar,
    "before_insert",
    ConvertibleCalendar.validate_disjoint_special_years,
)
event.listen(
    ConvertibleCalendar,
    "before_update",
    ConvertibleCalendar.validate_disjoint_special_years,
)


class CalendarConversion(utils.Base):
    """Calendar-to-Calendar Association Object"""

    __tablename__ = "calendar_conversion"
    source_calendar_id = Column(
        Integer, ForeignKey("convertible_calendar.id"), primary_key=True
    )
    target_calendar_id = Column(
        Integer, ForeignKey("convertible_calendar.id"), primary_key=True
    )
    source_sync_ordinal = Column(BigInteger, nullable=False)
    target_sync_ordinal = Column(BigInteger, nullable=False)

    target_calendar = relationship(
        ConvertibleCalendar,
        foreign_keys=[target_calendar_id],
        back_populates="_source_conversions",
    )
    source_calendar = relationship(
        ConvertibleCalendar,
        foreign_keys=[source_calendar_id],
        back_populates="_target_conversions",
    )

    def __repr__(self):
        return " <-> ".join(
            [str(self.source_calendar), str(self.target_calendar)]
        )

    @staticmethod
    def make_mutual_conversions(session: Session, *_):
        """
        If Calendar1 and Calendar2 can be converted and Calendar2 and Calendar3
        can be converted, make a conversion between Calendar1 and Calendar3.
        Designed to be an event listener before flush
        """
        calendars_in_session = [
            object_
            for object_ in session.new.union(session.dirty)
            if isinstance(object_, ConvertibleCalendar)
        ]
        for source_calendar in calendars_in_session:
            convertible_calendars = set(source_calendar.calendars())
            for calendar in convertible_calendars:
                linked_calendars = set(
                    cal
                    for cal in calendar.calendars()
                    if cal.id != source_calendar.id
                )
                if linked_calendars.issubset(convertible_calendars):
                    continue

                mutual_calendar = calendar
                missing_calendars = linked_calendars - convertible_calendars
                for missing_calendar in missing_calendars:
                    mutual2missing_sync_ordinal = mutual_calendar.sync_ordinal(
                        missing_calendar
                    )
                    old_missing_sync_ordinal = missing_calendar.sync_ordinal(
                        mutual_calendar
                    )

                    mutual2source_sync_ordinal = mutual_calendar.sync_ordinal(
                        source_calendar
                    )
                    old_source_sync_ordinal = source_calendar.sync_ordinal(
                        mutual_calendar
                    )

                    mutual_ordinal_diff = (
                        mutual2source_sync_ordinal
                        - mutual2missing_sync_ordinal
                    )
                    new_missing_sync_ordinal = (
                        old_missing_sync_ordinal + mutual_ordinal_diff
                    )
                    new_source_sync_ordinal = (
                        old_source_sync_ordinal + mutual_ordinal_diff
                    )

                    session.add(
                        CalendarConversion(
                            source_calendar=source_calendar,
                            source_sync_ordinal=new_source_sync_ordinal,
                            target_calendar=missing_calendar,
                            target_sync_ordinal=new_missing_sync_ordinal,
                        )
                    )


event.listen(
    Session, "before_flush", CalendarConversion.make_mutual_conversions
)
