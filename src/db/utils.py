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
import uuid

from sqlalchemy.orm import declarative_base


def auto_constraint_name(constraint, _):
    """
    hack to make naming convention work
    https://github.com/sqlalchemy/sqlalchemy/issues/4784#issuecomment-516055394
    """
    if constraint.name is None or constraint.name == "_unnamed_":
        return "sa_autoname_%s" % str(uuid.uuid4())[0:5]
    else:
        return constraint.name


NAMING_CONVENTION = {
    "auto_constraint_name": auto_constraint_name,
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(auto_constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base()
Base.metadata.naming_convention = NAMING_CONVENTION
