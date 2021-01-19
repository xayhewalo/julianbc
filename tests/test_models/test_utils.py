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
from src.db.utils import integer_sanitization, string_sanitization
from tests.utils import FAKE


def test_string_sanitization():
    mixed_type_collection = FAKE.pytuple()
    for element in string_sanitization(mixed_type_collection):
        assert isinstance(element, str)


def test_integer_sanitization():
    mixed_type_collection = FAKE.pylist(
        nb_elements=FAKE.random_int(min=1, max=10),
        variable_nb_elements=False,
        value_types=(float,),
    ) + [
        str(integer)
        for integer in FAKE.pylist(
            nb_elements=FAKE.random_int(min=1, max=10),
            variable_nb_elements=False,
            value_types=(int,),
        )
    ]
    for element in integer_sanitization(mixed_type_collection):
        assert isinstance(element, int)
