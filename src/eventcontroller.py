"""Where the user-interface and database events meet"""
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
from src.customdatetime import ConvertibleDateTime
from src.db import ConvertibleCalendar, Event
from src.setup_db import session
from sqlalchemy import and_, asc, or_
from sqlalchemy.future import select


class EventController:
    """Business logic for database events"""

    def __init__(self, cdt: ConvertibleDateTime):
        self.cdt = cdt

    def make(self, fields: dict) -> Event:
        """
        make an Event using `fields`
        :raise ValueError: if `start`, `end`, `duration` are not sensible
        """
        # todo get all the columns from the mapped class
        start = fields.get("start")
        end = fields.get("end")
        duration = fields.get("duration")
        if end is not None and duration is not None:
            if end - start != duration:
                raise ValueError(
                    f"Duration, {duration}, conflicts with "
                    f"start and end ordinal decimals: {start}, {end}"
                )

        # fixme a negative duration doesn't raise errors, change duration to hybrid property first
        calendar = self.cdt.date.calendar
        clock = self.cdt.time.clock
        event = Event(
            name=fields.get("name", "Untitled Event"),
            aliases=fields.get("aliases", ""),
            start=start,
            duration=duration,
            end=end,
            description=fields.get("description", ""),
            calendar_id=fields.get("calendar_id", calendar.id),
            clock_id=fields.get("clock_id", clock.id),
        )
        session.add(event)  # todo try catches?
        session.commit()
        # todo pull event from the db again with context manager?
        return event

    def get_events(
        self,
        start_ordinal_decimal: float,
        end_ordinal_decimal: float,
        calendar: ConvertibleCalendar = None,
    ) -> list:
        """Query for events within the start and end ordinal decimal"""
        if calendar is None:
            calendar = self.cdt.date.calendar

        inclusive_calendars = calendar.calendars()
        inclusive_calendars.append(calendar)

        # with session:
        result = list()
        for _, foreign_cal in enumerate(inclusive_calendars):  # fixme iteration breaks without enumeration for some reason
            # called "foreign" but the native calendar is in this list
            native_sync_ordinal = calendar.sync_ordinal(foreign_cal) or 0
            foreign_sync_ordinal = foreign_cal.sync_ordinal(calendar) or 0
            ordinal_diff = foreign_sync_ordinal - native_sync_ordinal

            start = start_ordinal_decimal + ordinal_diff
            end = end_ordinal_decimal + ordinal_diff

            # noinspection PyPropertyAccess,PyTypeChecker
            result.extend(
                session.execute(
                    select(Event).where(
                        or_(
                            # right edge of event is visible
                            and_(start <= Event.end, Event.end <= end),

                            # entire event is visible
                            and_(
                                and_(
                                    start <= Event.start,
                                    Event.start <= end,
                                ),
                                and_(
                                    start <= Event.end,
                                    Event.end <= end,
                                ),
                            ),

                            # left edge of event is visible
                            and_(start <= Event.start, Event.start <= end),

                            # middle of event is visible, but ends are not
                            and_(Event.start <= start, Event.end >= end)
                        ),
                    )
                    .order_by(asc(Event.start))
                )  # fixme ensure calendar id matches
                .scalars()
                .all()
            )
        return result
