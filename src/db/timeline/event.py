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
import sys

from src.db.entity import Entity
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    func,
    Float,
)
from sqlalchemy.ext.hybrid import hybrid_property


class Event(Entity):
    """Events on a Timeline"""

    __tablename__ = "event"
    __mapper_args__ = {"polymorphic_identity": "event"}
    id = Column(ForeignKey("entity.id"), primary_key=True)

    # noinspection PyPropertyAccess
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.creation_od = self.start
        self.destruction_od = self.end

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @hybrid_property
    def start(self):
        return self.creation_od

    @start.setter
    def start(self, start):
        if not start:
            raise ValueError("Event must have a start value")
        self.creation_od = start

    duration = Column(  # todo make this hybrid property based on end
        Float,
        CheckConstraint("duration >= 0", name=f"ck_{__tablename__}_duration"),
        default=sys.float_info.min,
        nullable=False
    )

    @hybrid_property
    def end(self):
        # noinspection PyPropertyAccess
        return self.start + self.duration

    @end.setter
    def end(self, value):
        if value is not None:  # change duration if self.end is set
            # noinspection PyPropertyAccess
            self.duration = abs(value - self.start)
            self.destruction_od = value
        else:  # base self.end on self.duration and self.start if it's None
            # noinspection PyPropertyAccess
            self.end = self.start + self.duration

    # noinspection PyUnresolvedReferences,PyMethodParameters
    @end.update_expression
    def end(cls, value):
        # noinspection PyPropertyAccess
        return [(cls.duration, func.abs(value + cls.start))]

    def __repr__(self):
        # noinspection PyPropertyAccess
        return (
            f"{self.name} ({self.start}, {self.end}, "
            f"{self.calendar}, {self.clock})"
        )
