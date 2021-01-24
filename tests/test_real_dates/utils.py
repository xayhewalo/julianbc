import convertdate

from collections import deque
from src.db import ConvertibleCalendar, CalendarConversion
from src.customdate import ConvertibleDate
from tests.utils import CalendarTestCase, FAKE


class RealCalendarTestCase(CalendarTestCase):
    """
    Helper methods to test Convertible Calendars.
    Assumes astronomical year numbering unless stated otherwise
    """

    def setUp(self):
        super(RealCalendarTestCase, self).setUp()
        # noinspection PyTypeChecker
        self.main_calendar = None  # type: ConvertibleCalendar
        self.to_gregorian_ymd = None  # type: callable
        self.common_ordinals: tuple
        # noinspection PyTypeChecker
        self.cycle_length = None  # type: int
        self.all_cycle_ordinals: deque
        self.leap_years_in_normal_cycle: int
        self.common_years_in_normal_cycle: int
        self.days_in_leap_years: int
        self.days_in_common_year: int

        self.gregorian = ConvertibleCalendar(
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
        self.gregorian_cd = ConvertibleDate(calendar=self.gregorian)
        self.gregorian_dc = convertdate.daycount.DayCount(
            convertdate.gregorian.EPOCH
        )

        self.coptic = ConvertibleCalendar(
            name="Coptic",
            weekday_names=(
                "Tkyriaka",
                "Pesnau",
                "Pshoment",
                "Peftoou",
                "Ptiou",
                "Psoou",
                "Psabbton",
            ),
            weekday_start=0,
            weekends=(5, 6),
            epoch_weekday=5,
            common_year_month_names=(
                "Thout",
                "Paopi",
                "Hathor",
                "Koiak",
                "Tobi",
                "Meshir",
                "Paremhat",
                "Parmouti",
                "Pashons",
                "Paoni",
                "Epip",
                "Mesori",
                "Pi Kogi Enavot",
            ),
            # fmt: off
            days_in_common_year_months=(
                30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5
            ),
            # fmt: on
            has_leap_year=True,
            leap_year_month_names=(
                "Thout",
                "Paopi",
                "Hathor",
                "Koiak",
                "Tobi",
                "Meshir",
                "Paremhat",
                "Parmouti",
                "Pashons",
                "Paoni",
                "Epip",
                "Mesori",
                "Pi Kogi Enavot",
            ),
            # fmt: off
            days_in_leap_year_months=(
                30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6
            ),
            # fmt: on
            leap_year_cycles=[4],
            leap_year_cycle_start=1,
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=-1,
            leap_year_cycle_ordinals=[4],
            eras=("BC", "AM"),
            era_ranges=(("-inf", 1), (1, "inf")),
            jd_epoch=1825030,
        )
        self.coptic_cd = ConvertibleDate(calendar=self.coptic)
        self.coptic_dc = convertdate.daycount.DayCount(
            convertdate.coptic.EPOCH
        )
        self.gregorian2coptic = CalendarConversion(
            source_calendar=self.gregorian,
            target_calendar=self.coptic,
            source_sync_ordinal=1,
            target_sync_ordinal=-103603,
        )

        self.indian = ConvertibleCalendar(
            name="शालिवाहन शक कैलेंडर",
            weekday_names=(
                "रविवार",
                "सोमवार",
                "मंगलवार",
                "बुधवार",
                "गुरूवार",
                "शुक्रवार",
                "शनिवार",
            ),
            weekday_start=0,
            weekends=(0, 6),
            epoch_weekday=2,
            common_year_month_names=(
                "चैत्र",
                "बैसाख",
                "ज्येष्ठ",
                "आसाढ़",
                "श्रावण",
                "भादों",
                "अश्विन्",
                "अगहन",
                "पूस",
                "माघ",
                "माघ",
                "फागुन",
            ),
            # fmt: off
            days_in_common_year_months=(
                30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30
            ),
            # fmt: on
            has_leap_year=True,
            leap_year_month_names=(
                "चैत्र",
                "बैसाख",
                "ज्येष्ठ",
                "आसाढ़",
                "श्रावण",
                "भादों",
                "अश्विन्",
                "अगहन",
                "पूस",
                "माघ",
                "माघ",
                "फागुन",
            ),
            # fmt: off
            days_in_leap_year_months=(
                31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30
            ),
            # fmt: on
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
            leap_year_offset=-77,
            eras=("बी ई", "एस ई"),
            era_ranges=(("-inf", 1), (0, "inf")),
            jd_epoch=1749630,
        )
        self.gregorian2indian = CalendarConversion(
            source_calendar=self.gregorian,
            target_calendar=self.indian,
            source_sync_ordinal=1,
            target_sync_ordinal=-28203,
        )
        self.indian_cd = ConvertibleDate(calendar=self.indian)
        self.indian_dc = convertdate.daycount.DayCount(1749630 - 0.5)

        self.l_hijri = ConvertibleCalendar(  # lunar hijri
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
        self.l_hijri_cd = ConvertibleDate(calendar=self.l_hijri)
        self.l_hijri_dc = convertdate.daycount.DayCount(
            convertdate.islamic.EPOCH
        )
        self.gregorian2islamic = CalendarConversion(
            source_calendar=self.gregorian,
            target_calendar=self.l_hijri,
            source_sync_ordinal=1,
            target_sync_ordinal=-227013,
        )

        self.julian = ConvertibleCalendar(
            name="Julian",
            weekday_names=(
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ),
            weekday_start=0,
            weekends=(5, 6),
            epoch_weekday=5,
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
            leap_year_cycles=[4],
            leap_year_cycle_ordinals=(4,),
            leap_year_cycle_start=1,
            eras=("BC", "AD"),
            era_ranges=[("-inf", 1), (1, "inf")],
            jd_epoch=1721424,
        )
        self.gregorian2julian = CalendarConversion(
            source_calendar=self.gregorian,
            target_calendar=self.julian,
            source_sync_ordinal=1,
            target_sync_ordinal=3,
        )
        self.julian_cd = ConvertibleDate(calendar=self.julian)
        self.julian_dc = convertdate.daycount.DayCount(
            convertdate.julian.JULIAN_EPOCH
        )

        self.s_hijri = ConvertibleCalendar(  # solar hijri
            name="گاه‌شماری هجری خورشیدی",
            weekday_names=(
                "Shanbeh",  # Saturday
                "Yekshambe",
                "Doshambe",
                "Seshambe",
                "Chæharshambe",
                "Panjshambe",
                "Jom'e",
            ),
            weekday_start=0,
            weekends=(6,),
            epoch_weekday=6,
            common_year_month_names=(
                "فروردین",
                "اردیبهشت",
                "خرداد",
                "تیر",
                "مرداد",
                "شهریور",
                "مهر",
                "آبان",
                "آذر",
                "دی",
                "بهمن",
                "اسفند",
            ),
            # fmt: off
            days_in_common_year_months=(
                31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29,
            ),
            # fmt: on
            has_leap_year=True,
            leap_year_month_names=(
                "فروردین",
                "اردیبهشت",
                "خرداد",
                "تیر",
                "مرداد",
                "شهریور",
                "مهر",
                "آبان",
                "آذر",
                "دی",
                "بهمن",
                "اسفند",
            ),
            # fmt: off
            days_in_leap_year_months=(
                31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30,
            ),
            # fmt: on
            special_common_years=(),
            special_leap_years=(),
            # fmt: off
            leap_year_cycles=(
                29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33,
                29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33,
                29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33,
                29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33,
                29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33, 29, 33, 33, 33,
                29, 33, 33, 33, 29, 33, 33, 37,
            ),
            # fmt: on
            leap_year_cycle_start=0,
            leap_year_cycle_ordinals=(4, 8, 12, 16, 20, 24, 28, 32, 36),
            leap_year_offset=-1304,  # current cycle started in 1925 CE
            eras=("BH", "AH"),
            era_ranges=(("-inf", 1), (1, "inf")),
            jd_epoch=1948321,
        )
        self.gregorian2s_hijri = CalendarConversion(
            source_calendar=self.gregorian,
            target_calendar=self.s_hijri,
            source_sync_ordinal=1,
            target_sync_ordinal=3,
        )
        self.s_hijri_cd = ConvertibleDate(calendar=self.s_hijri)
        self.s_hijri_dc = convertdate.daycount.DayCount(
            convertdate.persian.EPOCH
        )

        self.l_hijri2julian = CalendarConversion(
            source_calendar=self.l_hijri,
            target_calendar=self.julian,
            source_sync_ordinal=1,
            target_sync_ordinal=227017,
        )
        self.l_hijri2indian = CalendarConversion(
            source_calendar=self.l_hijri,
            target_calendar=self.indian,
            source_sync_ordinal=1,
            target_sync_ordinal=198811,
        )
        self.l_hijri2coptic = CalendarConversion(
            source_calendar=self.l_hijri,
            target_calendar=self.coptic,
            source_sync_ordinal=1,
            target_sync_ordinal=123411,
        )

        self.coptic2julian = CalendarConversion(
            source_calendar=self.coptic,
            target_calendar=self.julian,
            source_sync_ordinal=1,
            target_sync_ordinal=103607,
        )
        self.coptic2indian = CalendarConversion(
            source_calendar=self.coptic,
            target_calendar=self.indian,
            source_sync_ordinal=1,
            target_sync_ordinal=75401,
        )

        self.indian2julian = CalendarConversion(
            source_calendar=self.indian,
            target_calendar=self.julian,
            source_sync_ordinal=1,
            target_sync_ordinal=28207,
        )

        self.session.add_all(
            [
                self.gregorian,
                self.coptic,
                self.indian,
                self.l_hijri,
                self.julian,
                self.s_hijri,
                self.gregorian2coptic,
                self.gregorian2indian,
                self.gregorian2islamic,
                self.gregorian2julian,
                self.gregorian2s_hijri,
                self.l_hijri2julian,
                self.l_hijri2indian,
                self.l_hijri2coptic,
                self.coptic2julian,
                self.coptic2indian,
                self.indian2julian,
            ]
        )
        self.session.commit()

    #
    # Calendar **independent** methods
    #
    def make_cycle_start_year(self, completed_cycles: int, proleptic=False):
        """assumes astronomical year numbering"""
        start_year = (completed_cycles * self.cycle_length) + 1
        if proleptic:
            start_year = -(completed_cycles * self.cycle_length)
        return start_year

    def make_cycle_end_year(self, completed_cycles: int, proleptic=False):
        """assumes astronomical year numbering"""
        cycle_length = self.cycle_length
        end_year = (completed_cycles * cycle_length) + cycle_length
        if proleptic:
            end_year = -(completed_cycles * cycle_length) - cycle_length + 1
        return end_year

    def random_year(self) -> int:
        if FAKE.random_int() > 5000:
            return self.random_common_year()
        return self.random_leap_year()

    def random_bce_year(self) -> int:
        if FAKE.random_int() > 5000:
            return self.random_common_bce_year()
        return self.random_leap_bce_year()

    def random_ce_year(self) -> int:
        if FAKE.random_int() > 5000:
            return self.random_common_ce_year()
        return self.random_leap_ce_year()

    def random_common_ce_year(self) -> int:
        common_ce_year = self.random_common_year()
        while common_ce_year <= 0:
            common_ce_year = self.random_common_year()
        return common_ce_year

    def random_common_bce_year(self) -> int:
        common_bce_year = self.random_common_year()
        while common_bce_year > 0:
            common_bce_year = self.random_common_year()
        return common_bce_year

    def random_leap_ce_year(self) -> int:
        leap_ce_year = self.random_leap_year()
        while leap_ce_year <= 0:
            leap_ce_year = self.random_leap_year()
        return leap_ce_year

    def random_leap_bce_year(self) -> int:
        leap_bce_year = self.random_leap_year()
        while leap_bce_year > 0:
            leap_bce_year = self.random_leap_year()
        return leap_bce_year

    def random_common_month_and_day(
        self, calendar: ConvertibleCalendar = None
    ) -> tuple[int, int]:
        cal = self.main_calendar
        if calendar:
            cal = calendar

        return super(RealCalendarTestCase, self).random_common_month_and_day(
            cal
        )

    def random_leap_month_and_day(
        self, calendar: ConvertibleCalendar = None
    ) -> tuple[int, int]:
        cal = self.main_calendar
        if calendar:
            cal = calendar

        return super(RealCalendarTestCase, self).random_leap_month_and_day(cal)

    def random_ymd(self) -> tuple:
        if FAKE.random_int() > 5000:
            return self.random_common_ymd()
        return self.random_leap_ymd()

    def random_ce_ymd(self) -> tuple:
        if FAKE.random_int() > 5000:
            return self.random_common_ce_ymd()
        return self.random_leap_ce_ymd()

    def random_bce_ymd(self) -> tuple:
        if FAKE.random_int() > 5000:
            return self.random_common_bce_ymd()
        return self.random_leap_bce_ymd()

    @staticmethod
    def random_gregorian_common_year() -> int:
        common_year = (FAKE.random_int(-9999, 9999) * 4) - 1
        assert not convertdate.gregorian.isleap(common_year)
        return common_year

    def random_gregorian_common_bce_year(self) -> int:
        common_bce_year = self.random_gregorian_common_year()
        while common_bce_year > 0:
            common_bce_year = self.random_gregorian_common_year()
        return common_bce_year

    def random_gregorian_common_ce_year(self) -> int:
        common_ce_year = self.random_gregorian_common_year()
        while common_ce_year <= 0:
            common_ce_year = self.random_gregorian_common_year()
        return common_ce_year

    @staticmethod
    def random_gregorian_leap_year() -> int:
        leap_year = FAKE.random_int(-99, 99) * 400
        assert convertdate.gregorian.isleap(leap_year)
        return leap_year

    def random_gregorian_leap_bce_year(self) -> int:
        leap_bce_year = self.random_gregorian_leap_year()
        while leap_bce_year > 0:
            leap_bce_year = self.random_gregorian_leap_year()
        return leap_bce_year

    def random_gregorian_leap_ce_year(self) -> int:
        leap_ce_year = self.random_gregorian_leap_year()
        while leap_ce_year <= 0:
            leap_ce_year = self.random_gregorian_leap_year()
        return leap_ce_year

    def random_gregorian_ymd(self) -> tuple[int, int, int]:
        if FAKE.random_int() > 5000:
            return self.random_gregorian_common_ymd()
        return self.random_gregorian_leap_ymd()

    def random_convertible_gregorian_ymd(self) -> tuple[int, int, int]:
        """
        returns gregorian year, month, day with ast_year >-4716.
        Use to work around `convertdate` limitations
        """
        _, month, day = self.random_gregorian_ymd()

        # convertdate doesn't work for years < -4716
        if month == 2 and day == 29:
            year = self.random_gregorian_leap_year()
            while year <= -4716:
                year = self.random_gregorian_leap_year()
        else:
            year = self.random_gregorian_common_year()
            while year <= -4716:
                year = self.random_gregorian_common_year()
        return year, month, day

    def random_gregorian_common_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_common_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_common_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    def random_gregorian_common_bce_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_common_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_common_bce_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    def random_gregorian_common_ce_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_common_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_common_ce_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    def random_gregorian_leap_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_leap_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_leap_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    def random_gregorian_leap_bce_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_leap_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_leap_bce_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    def random_gregorian_leap_ce_ymd(self) -> tuple[int, int, int]:
        month, day = self.random_leap_month_and_day(self.gregorian)
        ast_year = self.random_gregorian_leap_ce_year()
        assert convertdate.gregorian.legal_date(ast_year, month, day)
        return ast_year, month, day

    @staticmethod
    def make_indian_ast_ymd(gregorian_ymd) -> tuple[int, int, int]:
        indian_hr_ymd = convertdate.indian_civil.from_gregorian(*gregorian_ymd)
        indian_ast_year = indian_hr_ymd[0] + 1  # hr years start from zero
        return indian_ast_year, indian_hr_ymd[1], indian_hr_ymd[2]

    def random_common_ymd(self) -> tuple:
        month, day = self.random_common_month_and_day()
        year = self.random_common_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def random_common_bce_ymd(self) -> tuple:
        month, day = self.random_common_month_and_day()
        year = self.random_common_bce_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def random_common_ce_ymd(self) -> tuple:
        month, day = self.random_common_month_and_day()
        year = self.random_common_ce_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def random_leap_ymd(self) -> tuple:
        month, day = self.random_leap_month_and_day()
        year = self.random_leap_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def random_leap_bce_ymd(self) -> tuple:
        month, day = self.random_leap_month_and_day()
        year = self.random_leap_bce_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def random_leap_ce_ymd(self) -> tuple:
        month, day = self.random_leap_month_and_day()
        year = self.random_leap_ce_year()
        assert self.date_validator((year, month, day)), "ymd is invalid"
        return year, month, day

    def date_validator(self, ymd: tuple) -> bool:
        return convertdate.gregorian.legal_date(*self.to_gregorian_ymd(*ymd))

    #
    # Calendar dependant methods, should be overwritten in subclass
    #
    @staticmethod
    def random_common_year() -> int:
        raise NotImplementedError

    @staticmethod
    def random_leap_year() -> int:
        raise NotImplementedError
