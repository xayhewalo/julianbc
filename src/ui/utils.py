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
ELEVATION_0 = 1
ELEVATION_1 = 0.95
ELEVATION_2 = 0.93
ELEVATION_3 = 0.92
ELEVATION_4 = 0.91
ELEVATION_6 = 0.89
ELEVATION_8 = 0.88
ELEVATION_12 = 0.86
ELEVATION_16 = 0.85
ELEVATION_24 = 0.84

BACKGROUND = 0.07, 0.07, 0.07
SURFACE = 0.31, 0.31, 0.31
PRIMARY = 0.73, 0.54, 0.99
ON_BACKGROUND = ON_SURFACE = 1, 1, 1
ON_PRIMARY = 0, 0, 0

BACKGROUND_COLOR = *BACKGROUND, ELEVATION_0
ON_BACKGROUND_COLOR = *ON_BACKGROUND, ELEVATION_0

SURFACE_COLOR = *SURFACE, ELEVATION_1
ON_SURFACE_COLOR = *ON_SURFACE, ELEVATION_1

PRIMARY_COLOR = *PRIMARY, ELEVATION_1
ON_PRIMARY_COLOR = *ON_PRIMARY, ELEVATION_1

HEADER_COLOR = *SURFACE, ELEVATION_6
