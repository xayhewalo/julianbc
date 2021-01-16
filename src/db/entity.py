"""The "E" in EAV"""
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
from src.db import utils
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import relationship, validates


class Entity(utils.Base):
    """Parent Class for all entities"""

    __tablename__ = "entity"
    id = Column(Integer, primary_key=True)
    _name = Column(Unicode(255), nullable=False)
    aliases = Column(JSON)  # todo string validation

    # todo related calendar
    @validates("aliases")
    def _sanitize_aliases(self, _, aliases: list) -> list:
        return utils.string_sanitization(aliases)

    description = Column(UnicodeText)
    creation_od = Column(Float)  # as an ordinal decimal
    destruction_od = Column(Float)  # as an ordinal decimal

    # todo can be nullable, check constraint that calendars and clocks are not null when creation/destruction_od or not null
    calendar_id = Column(
        Integer, ForeignKey("convertible_calendar.id"), nullable=False
    )
    calendar = relationship("ConvertibleCalendar")

    clock_id = Column(
        Integer, ForeignKey("convertible_clock.id"), nullable=False
    )
    clock = relationship("ConvertibleClock")

    def __repr__(self) -> str:
        return f"Entity: {self.id}, {self._name}"
