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
from sqlalchemy.future import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from src.customdate import ConvertibleDate
from src.customdatetime import ConvertibleDateTime
from src.customtime import ConvertibleTime
from src.db import CalendarConversion, ConvertibleCalendar, ConvertibleClock
from src.db.utils import Base

engine = create_engine("sqlite+pysqlite://", future=True)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base.metadata.create_all(engine)
session.commit()
gregorian = ConvertibleCalendar(
    name="Gregorian",
    weekday_names=(
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ),
    weekends=(5, 6),
    weekday_start=6,
    epoch_weekday=0,
    common_year_month_names=(
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ),
    # fmt: off
    days_in_common_year_months=(
        31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ),
    # fmt: on
    leap_year_month_names=(
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ),
    # fmt: off
    days_in_leap_year_months=(
        31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ),
    # fmt: on
    has_leap_year=True,
    leap_year_offset=0,
    leap_year_cycles=(400,),
    leap_year_cycle_start=1,
    # fmt: off
    leap_year_cycle_ordinals=[
        4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64,
        68, 72, 76, 80, 84, 88, 92, 96, 104, 108, 112, 116, 120, 124,
        128, 132, 136, 140, 144, 148, 152, 156, 160, 164, 168, 172,
        176, 180, 184, 188, 192, 196, 204, 208, 212, 216, 220, 224,
        228, 232, 236, 240, 244, 248, 252, 256, 260, 264, 268, 272,
        276, 280, 284, 288, 292, 296, 304, 308, 312, 316, 320, 324,
        328, 332, 336, 340, 344, 348, 352, 356, 360, 364, 368, 372,
        376, 380, 384, 388, 392, 396, 400
    ],
    # fmt: on
    eras=("BCE", "CE"),
    era_ranges=[("-inf", 1), (1, "inf")],
    jd_epoch=1721426,
)
l_hijri = ConvertibleCalendar(  # lunar hijri
    name="ٱلتَّقْوِيم ٱلْهِجْرِيّ",
    weekday_names=(
        "ٱلْأَحَد",
        "ٱلْإِثْنَيْن",
        "ٱلثُّلَاثَاء",
        "ٱلْأَرْبِعَاء",
        "ٱلْخَمِيس",
        "ٱلْجُمْعَة",
        "ٱلسَّبْت",
    ),
    weekday_start=0,
    weekends=(0, 6),
    epoch_weekday=5,
    common_year_month_names=(
        "ٱلْمُحَرَّم",
        "صَفَر",
        "رَبِيع ٱلْأَوَّل",
        "رَبِيع ٱلثَّانِي",
        "جُمَادَىٰ ٱلْأَوَّل",
        "جُمَادَىٰ ٱلثَّانِيَة",
        "رَجَب",
        "شَعْبَان",
        "رَمَضَان",
        "شَوَّال",
        "ذُو ٱلْقَعْدَة",
        "ذُو ٱلْحِجَّة",
    ),
    # fmt: off
    days_in_common_year_months=(
        30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29,
    ),
    # fmt: on
    has_leap_year=True,
    leap_year_month_names=(
        "ٱلْمُحَرَّم",
        "صَفَر",
        "رَبِيع ٱلْأَوَّل",
        "رَبِيع ٱلثَّانِي",
        "جُمَادَىٰ ٱلْأَوَّل",
        "جُمَادَىٰ ٱلثَّانِيَة",
        "رَجَب",
        "شَعْبَان",
        "رَمَضَان",
        "شَوَّال",
        "ذُو ٱلْقَعْدَة",
        "ذُو ٱلْحِجَّة",
    ),
    # fmt: off
    days_in_leap_year_months=(
        30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30,
    ),
    # fmt: on
    leap_year_cycles=[30],
    leap_year_cycle_start=1,
    leap_year_cycle_ordinals=(2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29),
    leap_year_offset=0,
    eras=("BH", "AH"),
    era_ranges=(("-inf", 1), (1, "inf")),
    jd_epoch=1948440,
)
gregorian2islamic = CalendarConversion(
    source_calendar=gregorian,
    target_calendar=l_hijri,
    source_sync_ordinal=1,
    target_sync_ordinal=-227013,
)
earth_clock = ConvertibleClock(name="Earth")
session.add_all([gregorian, l_hijri, gregorian2islamic, earth_clock])
session.commit()
gregorian_date = ConvertibleDate(calendar=gregorian)
l_hijri_date = ConvertibleDate(calendar=l_hijri)
earth_time = ConvertibleTime(clock=earth_clock)
gregorian_datetime = ConvertibleDateTime(date=gregorian_date, time=earth_time)
l_hijri_datetime = ConvertibleDateTime(date=l_hijri_date, time=earth_time)
