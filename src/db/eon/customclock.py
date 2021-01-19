"""Time-tracking models"""
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
from src.db import utils
from sqlalchemy import CheckConstraint, Column, Integer, Unicode
from sqlalchemy.orm import column_property


class ConvertibleClock(utils.Base):
    """User-defined time"""

    __tablename__ = "convertible_time"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    seconds_in_minute = Column(
        Integer,
        CheckConstraint("seconds_in_minute >= 1"),
        default=60,
        nullable=False,
    )
    minutes_in_hour = Column(
        Integer,
        CheckConstraint("minutes_in_hour >= 1"),
        default=60,
        nullable=False,
    )
    hours_in_day = Column(
        Integer,
        CheckConstraint("hours_in_day >= 1"),
        default=24,
        nullable=False,
    )
    seconds_in_hour = column_property(seconds_in_minute * minutes_in_hour)
    seconds_in_day = column_property(seconds_in_hour * hours_in_day)

    def __repr__(self):
        return f"{self.name}(Seconds in a Day: {self.seconds_in_day})"
