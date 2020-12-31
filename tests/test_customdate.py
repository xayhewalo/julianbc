import pytest

from src.customdate import ConvertibleDate
from tests.factories import ConvertibleCalendarFactory
from tests.utils import CalendarTestCase, FAKE
from unittest.mock import patch


class ConvertibleDateTimeTest(CalendarTestCase):
    def setUp(self):
        super(ConvertibleDateTimeTest, self).setUp()
        self.calendar_factory = ConvertibleCalendarFactory

    #
    # Helper functions
    #
    @staticmethod
    def make_ast_year(
        era_range: tuple, hr_year: int, years_before_era: int
    ) -> int:
        era_start_hr_year = float(era_range[0])
        era_end_hr_year = float(era_range[1])
        if era_end_hr_year == float("inf"):
            years_into_current_era = abs(era_start_hr_year - hr_year) + 1
            return int(years_into_current_era + years_before_era)
        elif era_start_hr_year == float("-inf"):
            years_into_current_era = abs(hr_year - era_end_hr_year) + 1
            # years_before_era should be zero for proleptic eras
            return int(-(years_into_current_era - 1))
        else:
            years_into_current_era = abs(hr_year - era_start_hr_year) + 1
            return int(years_into_current_era + years_before_era)

    @staticmethod
    def random_hr_year(era_range: tuple) -> int:
        era_start_hr_year = float(era_range[0])
        era_end_hr_year = float(era_range[1])
        if era_end_hr_year == float("inf"):
            return int(era_start_hr_year + FAKE.random_int())
        elif era_start_hr_year == float("-inf"):
            return int(era_end_hr_year + FAKE.random_int())
        else:
            return FAKE.random_int(
                min=min(era_start_hr_year, era_end_hr_year),
                max=max(era_start_hr_year, era_end_hr_year),
            )

    @staticmethod
    def years_before_era(
        calendar: ConvertibleCalendarFactory, era_idx: int
    ) -> int:
        """excludes eras with infinite ranges"""
        era_ranges = calendar.era_ranges
        years_before_era = 0
        for era_range in era_ranges[:era_idx]:
            start_hr_year = float(era_range[0])
            end_hr_year = float(era_range[1])
            if start_hr_year == float("-inf") or end_hr_year == float("inf"):
                continue
            years_before_era += abs(end_hr_year - start_hr_year) + 1
        return years_before_era

    def random_monthless_calendar(
        self,
    ) -> tuple[ConvertibleCalendarFactory, int]:
        days_in_year = FAKE.random_int(min=1)
        monthless_calendar = self.calendar_factory.build(
            common_year_month_names=(),
            days_in_common_year_months=(days_in_year,),
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_exceptions=(),
            leap_year_overrules=(),
            leap_year_offset=None,
        )
        return monthless_calendar, days_in_year

    #
    # Ordinal Conversions
    #

    # ConvertibleDateTime.increment_ast_ymd tested in test_gregorian.py
    # ConvertibleDateTime.ordinal_date_to_ordinal in test_gregorian.py
    # ConvertibleDateTime.ordinal_to_ordinal_date in test_gregorian.py

    def test__start_and_sign(self):
        non_positive_num = FAKE.random_int(min=-9999, max=-1)
        positive_num = FAKE.random_int(min=1)
        cdt = ConvertibleDate(calendar=self.calendar_factory.build())
        assert cdt._start_and_sign(non_positive_num) == (0, -1)
        assert cdt._start_and_sign(positive_num) == (1, 1)

    def test__increment_by_one(self):
        num = FAKE.random_int(min=-9999)
        positive_sign = 1
        negative_sign = -1
        cdt = ConvertibleDate(calendar=self.calendar_factory.build())
        assert cdt._increment_by_one(num, positive_sign) == num + 1
        assert cdt._increment_by_one(num, negative_sign) == num - 1

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    def test_ast_ymd_to_ordinal_date_with_no_months(self, _):
        monthless_calendar, days_in_year = self.random_monthless_calendar()
        day_of_year = FAKE.random_int(min=1, max=days_in_year)
        ast_year = FAKE.random_int()
        monthless_ast_ymd = ast_year, None, day_of_year
        ordinal_date = ast_year, day_of_year
        cdt = ConvertibleDate(calendar=monthless_calendar)
        assert cdt.ast_ymd_to_ordinal_date(monthless_ast_ymd) == ordinal_date

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    def test_ordinal_date_to_ast_ymd_with_no_months(self, _):
        monthless_calendar, days_in_year = self.random_monthless_calendar()
        ast_year = FAKE.random_int()
        day_of_year = FAKE.random_int(min=1, max=days_in_year)
        ordinal_date = ast_year, day_of_year
        cdt = ConvertibleDate(calendar=monthless_calendar)
        assert cdt.ordinal_date_to_ast_ymd(ordinal_date) == (
            ast_year,
            None,
            day_of_year,
        )

    def test_ordinal_date_to_ast_ymd_with_no_months_are_reversible(self):
        monthless_calendar, days_in_year = self.random_monthless_calendar()
        day_of_year = FAKE.random_int(min=1, max=days_in_year)
        ast_year = FAKE.random_int()
        monthless_ast_ymd = ast_year, None, day_of_year
        ordinal_date = ast_year, day_of_year
        cdt = ConvertibleDate(calendar=monthless_calendar)
        assert cdt.ordinal_date_to_ast_ymd(ordinal_date) == monthless_ast_ymd
        assert cdt.ast_ymd_to_ordinal_date(monthless_ast_ymd) == ordinal_date

    #
    # Human readable years
    #
    def test_hr_to_ast(self):
        calendar = self.calendar_factory.build()
        cdt = ConvertibleDate(calendar=calendar)
        era_range = FAKE.random_element(elements=calendar.era_ranges)
        era_idx = calendar.era_ranges.index(era_range)
        hr_year = self.random_hr_year(era_range)
        years_in_previous_eras = self.years_before_era(calendar, era_idx)
        ast_year = self.make_ast_year(
            era_range, hr_year, years_in_previous_eras
        )
        assert cdt.hr_to_ast(hr_year, era_idx) == ast_year

    def test_ast_to_hr(self):
        calendar = self.calendar_factory.build()
        era_range = FAKE.random_element(elements=calendar.era_ranges)
        era_idx = calendar.era_ranges.index(era_range)
        years_in_previous_eras = self.years_before_era(calendar, era_idx)
        hr_year = self.random_hr_year(era_range)
        ast_year = self.make_ast_year(
            era_range, hr_year, years_in_previous_eras
        )
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.ast_to_hr(ast_year) == (hr_year, era_idx)

    def test_ast_to_hr_for_finite_ascending_era(self):
        calendar = self.calendar_factory.build()
        ascending_era_range = (
            FAKE.random_int(min=1),
            FAKE.random_int(min=10000, max=20000),
        )
        calendar.era_ranges.insert(1, ascending_era_range)
        hr_year = self.random_hr_year(ascending_era_range)
        ast_year = self.make_ast_year(ascending_era_range, hr_year, 0)
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.ast_to_hr(ast_year) == (hr_year, 1)

    def test_ast_to_hr_for_finite_descending_era(self):
        calendar = self.calendar_factory.build()
        descending_era_range = (
            FAKE.random_int(min=10000, max=20000),
            FAKE.random_int(min=1),
        )
        calendar.era_ranges.insert(1, descending_era_range)
        hr_year = self.random_hr_year(descending_era_range)
        ast_year = self.make_ast_year(descending_era_range, hr_year, 0)
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.ast_to_hr(ast_year) == (hr_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        calendar = self.calendar_factory.build()
        era_range = FAKE.random_element(elements=calendar.era_ranges)
        hr_year = self.random_hr_year(era_range)
        era_idx = calendar.era_ranges.index(era_range)
        years_before_era = self.years_before_era(calendar, era_idx)
        ast_year = self.make_ast_year(era_range, hr_year, years_before_era)
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.ast_to_hr(cdt.hr_to_ast(hr_year, era_idx)) == (
            hr_year,
            era_idx,
        )
        assert cdt.hr_to_ast(*cdt.ast_to_hr(ast_year)) == ast_year

    @patch(
        "src.customdate.ConvertibleDate.gen_years_before_era",
    )
    def test_ast_to_hr_can_raise(self, _):
        calendar = self.calendar_factory.build()
        cdt = ConvertibleDate(calendar=calendar)
        ast_ce_year = FAKE.random_int(min=1)
        with pytest.raises(RuntimeError):
            cdt.ast_to_hr(ast_ce_year)

    def test_parse_hr_date_and_format_hr_date_are_reversible(self):
        calendar = self.calendar_factory.build(
            leap_year_cycles=(4,),
            leap_year_cycle_ordinals=(4,),
            leap_year_cycle_start=1,
            leap_year_overrules=(),
            leap_year_exceptions=(),
            leap_year_offset=0,
            era_ranges=(("-inf", 1), (1, "inf")),
            eras=(FAKE.word(), FAKE.word()),
        )
        cdt = ConvertibleDate(calendar=calendar)
        common_ce_ast_year = (FAKE.random_int(min=1) * 4) - 1
        common_ce_hr_year = common_ce_ast_year
        common_bce_ast_year = (FAKE.random_int(min=-9999, max=0) * 4) - 1
        common_bce_hr_year = abs(common_bce_ast_year - 1)
        common_month, common_day = self.random_common_month_and_day(calendar)
        common_ce_ymd = common_ce_ast_year, common_month, common_day
        common_bce_ymd = common_bce_ast_year, common_month, common_day
        common_ce_hr_date = cdt.date_sep.join(
            [
                str(common_ce_hr_year),
                str(common_month),
                str(common_day),
                calendar.eras[1],
            ]
        )
        common_bce_hr_date = cdt.date_sep.join(
            [
                str(common_bce_hr_year),
                str(common_month),
                str(common_day),
                calendar.eras[0],
            ]
        )

        leap_ce_ast_year = leap_ce_hr_year = FAKE.random_int(min=1) * 4
        leap_bce_ast_year = FAKE.random_int(min=-9999, max=0) * 4
        leap_bce_hr_year = abs(leap_bce_ast_year - 1)
        leap_month, leap_day = self.random_leap_month_and_day(calendar)
        leap_ce_ymd = leap_ce_ast_year, leap_month, leap_day
        leap_bce_ymd = leap_bce_ast_year, leap_month, leap_day
        leap_bce_hr_date = cdt.date_sep.join(
            [
                str(leap_bce_hr_year),
                str(leap_month),
                str(leap_day),
                calendar.eras[0],
            ]
        )
        leap_ce_hr_date = cdt.date_sep.join(
            [
                str(leap_ce_hr_year),
                str(leap_month),
                str(leap_day),
                calendar.eras[1],
            ]
        )
        assert (
            cdt.parse_hr_date(cdt.format_hr_date(common_bce_ymd))
            == common_bce_ymd
        )
        assert (
            cdt.parse_hr_date(cdt.format_hr_date(common_ce_ymd))
            == common_ce_ymd
        )
        assert (
            cdt.parse_hr_date(cdt.format_hr_date(leap_bce_ymd)) == leap_bce_ymd
        )
        assert (
            cdt.parse_hr_date(cdt.format_hr_date(leap_ce_ymd)) == leap_ce_ymd
        )
        assert (
            cdt.format_hr_date(cdt.parse_hr_date(common_bce_hr_date))
            == common_bce_hr_date
        )
        assert (
            cdt.format_hr_date(cdt.parse_hr_date(common_ce_hr_date))
            == common_ce_hr_date
        )
        assert (
            cdt.format_hr_date(cdt.parse_hr_date(leap_bce_hr_date))
            == leap_bce_hr_date
        )
        assert (
            cdt.format_hr_date(cdt.parse_hr_date(leap_ce_hr_date))
            == leap_ce_hr_date
        )

    def test_parse_hr_date_with_no_months(self):
        monthless_calendar, day_of_year = self.random_monthless_calendar()
        era_range = FAKE.random_element(elements=monthless_calendar.era_ranges)
        hr_year = self.random_hr_year(era_range)
        era_idx = monthless_calendar.era_ranges.index(era_range)
        years_before_era = self.years_before_era(monthless_calendar, era_idx)
        era = monthless_calendar.eras[era_idx]
        cdt = ConvertibleDate(calendar=monthless_calendar)
        hr_date = cdt.date_sep.join([str(hr_year), str(day_of_year), era])
        ast_year = self.make_ast_year(era_range, hr_year, years_before_era)
        assert cdt.parse_hr_date(hr_date) == (ast_year, None, day_of_year)

    def test_format_hr_date_with_no_months(self):
        monthless_calendar, day_of_year = self.random_monthless_calendar()
        era_range = FAKE.random_element(elements=monthless_calendar.era_ranges)
        hr_year = self.random_hr_year(era_range)
        era_idx = monthless_calendar.era_ranges.index(era_range)
        years_before_era = self.years_before_era(monthless_calendar, era_idx)
        ast_year = self.make_ast_year(era_range, hr_year, years_before_era)
        era = monthless_calendar.eras[era_idx]

        cdt = ConvertibleDate(calendar=monthless_calendar)
        date_sep = cdt.date_sep
        hr_date = date_sep.join(
            [str(hr_year), str(None), str(day_of_year), str(era)]
        )
        ast_ymd = ast_year, None, day_of_year
        assert cdt.format_hr_date(ast_ymd) == hr_date

    #
    # ConvertibleDateTime.era
    #
    def test_era_for_valid_ranges(self):
        calendar = self.calendar_factory.build()
        era_range = FAKE.random_element(elements=calendar.era_ranges)
        era_idx = calendar.era_ranges.index(era_range)
        years_in_previous_eras = self.years_before_era(calendar, era_idx)
        hr_year = self.random_hr_year(era_range)
        ast_year = self.make_ast_year(
            era_range, hr_year, years_in_previous_eras
        )
        expected_era = calendar.eras[era_idx]
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.era(ast_year) == expected_era

    def test_era_for_one_year_range(self):
        """human readable years unless labeled otherwise"""
        first_era_end_year = FAKE.random_int(min=1, max=9999)
        second_era_start_year = FAKE.random_int(min=1, max=9999)
        second_era_end_year = FAKE.random_int(min=1, max=9999)
        years_in_second_era = (
            abs(second_era_end_year - second_era_start_year) + 1
        )
        tiny_era_year = FAKE.random_int(min=1, max=9999)
        final_era_start_year = FAKE.random_int(min=1, max=9999)

        era_ranges = (
            ("-inf", first_era_end_year),
            (second_era_start_year, second_era_end_year),
            (tiny_era_year, tiny_era_year),
            (final_era_start_year, "inf"),
        )
        first_era_ast_year = FAKE.random_int(min=-9999, max=0)
        second_era_ast_year = FAKE.random_int(min=1, max=years_in_second_era)
        tiny_era_ast_year = years_in_second_era + 1
        final_era_ast_year = FAKE.random_int(
            min=years_in_second_era + 2,  # + tiny era span and off by 1 offset
            max=years_in_second_era + 2 + FAKE.random_int(min=1),
        )
        eras = ("BCE", "Second", "Tiny", "CE")
        calendar = self.calendar_factory.build(
            era_ranges=era_ranges, eras=eras
        )
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.era(first_era_ast_year) == eras[0]
        assert cdt.era(second_era_ast_year) == eras[1]
        assert cdt.era(tiny_era_ast_year) == eras[2]
        assert cdt.era(final_era_ast_year) == eras[3]

    @patch(
        "src.customdate.ConvertibleDate.gen_years_before_era",
    )
    def test_era_can_raise(self, _):
        calendar = self.calendar_factory.build()
        year = FAKE.random_int(min=1)
        with pytest.raises(RuntimeError):
            ConvertibleDate(calendar=calendar).era(year)

    #
    # ConvertibleDateTime.is_descending_era
    #
    def test_is_descending_era(self):
        calendar = self.calendar_factory.build()
        era_range = FAKE.random_element(elements=calendar.era_ranges)

        hr_year = self.random_hr_year(era_range)
        era_idx = calendar.era_ranges.index(era_range)
        years_in_previous_eras = self.years_before_era(calendar, era_idx)
        ast_year = self.make_ast_year(
            era_range, hr_year, years_in_previous_eras
        )

        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.is_descending_era(ast_year) is (
            abs(era_range[0]) > abs(era_range[1])
        )

    #
    # ConvertibleDateTime.is_leap_year
    #
    def test_is_leap_year_with_cycles(self):
        calendar = self.calendar_factory.build(
            leap_year_exceptions=(),
            leap_year_overrules=(),
            leap_year_cycles=(5, 7),
            leap_year_cycle_start=0,
            leap_year_cycle_ordinals=(0, 3, 5),
            leap_year_offset=0,
        )
        ce_leap_ast_years = (1, 4, 6, 9, 11, 13, 16, 18, 21, 23)
        bce_leap_ast_years = (-1, -3, -6, -8, -11, -13, -15, -18, -20, -23)
        # fmt: off
        ce_common_ast_years = (
            2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24
        )
        bce_common_ast_years = (
            0, -2, -4, -5, -7, -9, -10, -12, -14, -16, -17, -19, -21, -22
        )
        # fmt: on
        cdt = ConvertibleDate(calendar=calendar)
        for ce_leap_year in ce_leap_ast_years:
            assert cdt.is_leap_year(ce_leap_year)
        for bce_leap_year in bce_leap_ast_years:
            assert cdt.is_leap_year(bce_leap_year)
        for ce_common_year in ce_common_ast_years:
            assert cdt.is_leap_year(ce_common_year) is False
        for bce_common_year in bce_common_ast_years:
            assert cdt.is_leap_year(bce_common_year) is False

    def test_is_leap_year_cycles_with_offset(self):
        calendar = self.calendar_factory.build(
            leap_year_exceptions=(),
            leap_year_overrules=(),
            leap_year_cycles=(9, 1),
            leap_year_cycle_start=0,
            leap_year_cycle_ordinals=(1, 4, 5, 8),
            leap_year_offset=3,
        )
        ce_leap_ast_years = (2, 5, 8, 12, 15, 18, 19, 22, 25)
        bce_leap_ast_years = (-1, -2, -5, -8, -11, -12, -15, -18, -21, -22)
        # fmt: off
        ce_common_ast_years = (
            1, 3, 4, 6, 7, 10, 11, 13, 14, 16, 17, 20, 21, 23, 24, 26
        )
        bce_common_ast_years = (
            0, -3, -4, -6, -7, -9, -10, -13, -14, -16, -17, -19, -20, -23
        )
        # fmt: on
        cdt = ConvertibleDate(calendar=calendar)
        for ce_leap_year in ce_leap_ast_years:
            assert cdt.is_leap_year(ce_leap_year)
        for bce_leap_year in bce_leap_ast_years:
            assert cdt.is_leap_year(bce_leap_year)
        for ce_common_year in ce_common_ast_years:
            assert cdt.is_leap_year(ce_common_year) is False
        for bce_common_year in bce_common_ast_years:
            assert cdt.is_leap_year(bce_common_year) is False

    def test_is_leap_year_with_non_zero_start(self):
        calendar = self.calendar_factory.build(
            leap_year_exceptions=(),
            leap_year_overrules=(),
            leap_year_cycles=(2, 5),
            leap_year_cycle_start=2,
            leap_year_cycle_ordinals=(3, 6),
            leap_year_offset=0,
        )
        ce_leap_ast_years = (2, 4, 7, 9, 11, 14, 16, 18, 21)
        bce_leap_ast_years = (0, -3, -5, -7, -10, -12, -14, -17, -19)
        ce_common_ast_years = (1, 3, 5, 6, 8, 10, 12, 13, 15, 17, 19, 20)
        # fmt: off
        bce_common_ast_years = (
            -1, -2, -4, -6, -8, -9, -11, -13, -15, -16, -18, -20
        )
        # fmt: on
        cdt = ConvertibleDate(calendar=calendar)
        for ce_leap_year in ce_leap_ast_years:
            assert cdt.is_leap_year(ce_leap_year)
        for bce_leap_year in bce_leap_ast_years:
            assert cdt.is_leap_year(bce_leap_year)
        for ce_common_year in ce_common_ast_years:
            assert cdt.is_leap_year(ce_common_year) is False
        for bce_common_year in bce_common_ast_years:
            assert cdt.is_leap_year(bce_common_year) is False

    def test_is_leap_year_with_no_leap_year(self):
        calendar = self.calendar_factory.build(has_leap_year=False)
        cdt = ConvertibleDate(calendar=calendar)
        year = FAKE.random_int(-9999, 9999)
        assert cdt.is_leap_year(year) is False

    def test_is_leap_year_with_overrules(self):
        calendar = self.calendar_factory.build(leap_year_exceptions=())
        overruled_year = FAKE.random_element(
            elements=calendar.leap_year_overrules
        )
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.is_leap_year(overruled_year)

    def test_is_leap_year_with_exceptions(self):
        calendar = self.calendar_factory.build(
            leap_year_overrules=(),
        )
        exception_year = FAKE.random_element(
            elements=calendar.leap_year_exceptions
        )
        cdt = ConvertibleDate(calendar=calendar)
        assert cdt.is_leap_year(exception_year) is False

    #
    # ConvertibleDateTime.is_valid_ast_ymd
    #
    def test_is_valid_ast_ymd_with_no_months(self):
        monthless_calendar, days_in_year = self.random_monthless_calendar()
        negative_day_of_year = FAKE.random_int(min=-9999, max=0)
        day_of_year = FAKE.random_int(min=1, max=days_in_year)
        too_large_day_of_year = FAKE.random_int(
            min=days_in_year + 1, max=days_in_year + 9999
        )
        monthless_ast_ymd = (FAKE.random_int(), None, day_of_year)
        negative_ast_ymd = (FAKE.random_int(), None, negative_day_of_year)
        too_large_ast_ymd = (FAKE.random_int(), None, too_large_day_of_year)
        monthless_cdt = ConvertibleDate(calendar=monthless_calendar)
        assert monthless_cdt.is_valid_ast_ymd(monthless_ast_ymd) is True
        assert monthless_cdt.is_valid_ast_ymd(negative_ast_ymd) is False
        assert monthless_cdt.is_valid_ast_ymd(too_large_ast_ymd) is False

    # ConvertibleDateTime.days_in_months tested in test_gregorian.py
    # ConvertibleDateTime.days_in_year tested in test_gregorian.py
    # ConvertibleDateTime.months_in_year tested in test_gregorian.py

    #
    # ConvertibleDateTime.is_valid_ordinal_date
    #
    def test_is_valid_ordinal_date_with_no_months(self):
        monthless_calendar, days_in_year = self.random_monthless_calendar()
        monthless_calendar.days_in_common_year_months = (days_in_year,)
        valid_day_of_year = FAKE.random_int(min=1, max=days_in_year)
        valid_ordinal_date = (FAKE.random_int(), valid_day_of_year)
        too_small_day_of_year = FAKE.random_int(min=-9999, max=0)
        too_big_day_of_year = FAKE.random_int(
            min=days_in_year + 1, max=days_in_year + 9999
        )
        too_small_ordinal_date = (FAKE.random_int(), too_small_day_of_year)
        too_big_ordinal_date = (FAKE.random_int(), too_big_day_of_year)
        cdt = ConvertibleDate(calendar=monthless_calendar)
        assert cdt.is_valid_ordinal_date(too_small_ordinal_date) is False
        assert cdt.is_valid_ordinal_date(valid_ordinal_date) is True
        assert cdt.is_valid_ordinal_date(too_big_ordinal_date) is False

    #
    # ConvertibleDateTime.gen_years_in_eras
    #
    def test_gen_years_in_eras(self):
        calendar = self.calendar_factory.build()
        cdt = ConvertibleDate(calendar=calendar)
        for values in cdt.gen_years_before_era():
            fetched_hr_era_range = values["hr_range"]
            fetched_ast_era_range = values["ast_range"]
            era_idx = values["index"]
            fetched_years_in_era = values["years_in"]
            fetched_years_before_era = values["years_before"]

            expected_years_before_era = self.years_before_era(
                calendar, era_idx
            )
            expected_hr_era_range = calendar.era_ranges[era_idx]
            expected_years_in_era = (
                abs(
                    float(expected_hr_era_range[1])
                    - float(expected_hr_era_range[0])
                )
                + 1
            )
            expected_ast_era_range = (
                expected_years_before_era + 1,
                expected_years_before_era + expected_years_in_era,
            )
            if expected_hr_era_range[0] == "-inf":
                expected_ast_era_range = (float("-inf"), 0)
            assert fetched_hr_era_range == expected_hr_era_range
            assert fetched_years_before_era == expected_years_before_era
            assert fetched_years_in_era == expected_years_in_era
            assert fetched_ast_era_range == expected_ast_era_range

    def test_gen_years_in_eras_start(self):
        calendar = self.calendar_factory.build()
        cdt = ConvertibleDate(calendar=calendar)
        num_ranges = len(calendar.era_ranges)
        start = FAKE.random_int(min=0, max=num_ranges - 2)
        skipped_eras = calendar.eras[:start]
        skipped_hr_era_ranges = calendar.era_ranges[:start]

        fetched_eras = list()
        fetched_hr_era_ranges = list()
        fetched_ast_era_ranges = list()
        for era_info in cdt.gen_years_before_era(start=start):
            era_idx = era_info["index"]
            hr_era_range = era_info["hr_range"]
            ast_era_range = era_info["ast_range"]
            years_in_era = era_info["years_in"]
            expected_years_before_era = self.years_before_era(
                calendar, era_idx
            )

            fetched_years_before = era_info["years_before"]
            fetched_eras.append(calendar.eras[era_idx])
            fetched_hr_era_ranges.append(hr_era_range)
            fetched_ast_era_ranges.append(ast_era_range)
            fetched_years_in_era = (
                abs(float(hr_era_range[1]) - float(hr_era_range[0])) + 1
            )
            assert years_in_era == fetched_years_in_era
            assert fetched_years_before == expected_years_before_era
        assert skipped_eras not in fetched_eras
        assert skipped_hr_era_ranges not in fetched_hr_era_ranges

    #
    # Weeks
    #
    @patch("src.customdate.ConvertibleDate.days_in_week", return_value=0)
    def test_day_of_week_with_no_weeks(self, _):
        weekless_calendar = self.calendar_factory.build(
            weekday_names=(),
            weekday_start=(),
            weekends=(),
            epoch_weekday=(),
        )
        _ordinal = FAKE.random_int()
        cdt = ConvertibleDate(calendar=weekless_calendar)
        assert cdt.day_of_week(_ordinal) is None

    def test_days_in_week(self):
        weekless_calendar = self.calendar_factory.build(
            weekday_names=(),
            weekday_start=(),
            weekends=(),
            epoch_weekday=(),
        )
        cdt = ConvertibleDate(calendar=weekless_calendar)
        assert cdt.days_in_week() == 0
