import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
from collections import deque
from src.customdate import DateUnit
from unittest.mock import patch


class LunarHijriTest(RealCalendarTestCase):
    """
    Can the database represent the Lunar Hijri Calendar? (Microsoft Kuwait)
    Years are astronomical unless labeled otherwise
    """

    #
    # Helper functions
    #
    def setUp(self):
        super(LunarHijriTest, self).setUp()
        self.main_calendar = self.l_hijri
        self.to_gregorian_ymd = convertdate.islamic.to_gregorian
        self.common_ordinals = list(
            set(range(1, 31)) ^ set(self.l_hijri.leap_year_cycle_ordinals)
        )
        self.common_ordinals.sort()
        self.cycle_length = 30
        self.all_cycle_ordinals = deque(range(1, 31))
        self.leap_years_in_normal_cycle = 11
        self.common_years_in_normal_cycle = 19
        self.days_in_leap_years = 355
        self.days_in_common_year = 354

    def random_common_year(self) -> int:
        year = FAKE.random_int(min=-9999)
        while (year % 30) in self.l_hijri.leap_year_cycle_ordinals:
            year = FAKE.random_int()
        assert not convertdate.islamic.leap(year), f"{year} is a leap year"
        return year

    def random_leap_year(self) -> int:
        year = FAKE.random_int(min=-9999)
        while (year % 30) not in self.l_hijri.leap_year_cycle_ordinals:
            year = FAKE.random_int()
        assert convertdate.islamic.leap(year), f"{year} is a common year "
        return year

    def ordinal_conversion_patches(self, *args):
        patch_days_common_year = args[0]
        patch_days_in_leap_year = args[1]
        patch_common_years_in_normal_cycle = args[2]
        patch_leap_years_in_normal_cycle = args[3]
        patch_common_year_cycle_ordinals = args[4]
        patch_all_cycle_ordinals = args[5]
        patch_leap_year_cycle_length = args[6]

        patch_leap_year_cycle_length.__get__ = lambda *_: self.cycle_length
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ordinals = self.common_ordinals
        patch_common_year_cycle_ordinals.__get__ = lambda *_: common_ordinals
        lyinc = self.leap_years_in_normal_cycle
        patch_leap_years_in_normal_cycle.__get__ = lambda *_: lyinc
        cyinc = self.common_years_in_normal_cycle
        patch_common_years_in_normal_cycle.__get__ = lambda *_: cyinc
        patch_days_in_leap_year.__get__ = lambda *_: self.days_in_leap_years
        patch_days_common_year.__get__ = lambda *_: self.days_in_common_year

    #
    # Shift year, month, day
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    def test_shift_ast_ymd_by_multiple_intervals(self, _):
        plus_delta = FAKE.random_int(min=1, max=11)
        plus_years = [[plus_delta, DateUnit.YEAR]]
        plus_months = [[plus_delta, DateUnit.MONTH]]
        ymd = self.random_ymd()
        ast_year, _, _ = ymd
        zero_interval = [[0, DateUnit.YEAR]]
        assert self.l_hijri_cd.shift_ast_ymd(ymd, zero_interval) == ymd
        # fmt: off
        assert self.l_hijri_cd.shift_ast_ymd(
            (ast_year, 9, 4), plus_years
        ) == (ast_year + plus_delta, 9, 4)
        assert self.l_hijri_cd.shift_ast_ymd(
            (ast_year, 1, 29), plus_months
        ) == (ast_year, 1 + plus_delta, 29)
        # fmt: on
        assert self.l_hijri_cd.shift_ast_ymd(
            (ast_year, 2, 20), [[22, DateUnit.YEAR], [7, DateUnit.MONTH]]
        ) == (ast_year + 22, 9, 20)
        assert self.l_hijri_cd.shift_ast_ymd(
            (ast_year, 3, 25), [[7, DateUnit.YEAR], [-2, DateUnit.MONTH]]
        ) == (ast_year + 7, 1, 25)

    def test_shift_ast_ymd_to_invalid_day(self):
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.l_hijri_cd.shift_ast_ymd(
            (common_year, 11, 30), [[1, DateUnit.MONTH]]
        ) == (common_year, 12, 29)
        assert self.l_hijri_cd.shift_ast_ymd(
            (leap_year, 12, 30), [[2, DateUnit.MONTH]]
        ) == (leap_year + 1, 2, 29)
        assert self.l_hijri_cd.shift_ast_ymd(
            (leap_year, 12, 30), [[-2, DateUnit.MONTH]]
        ) == (leap_year, 10, 29)
        assert self.l_hijri_cd.shift_ast_ymd(
            (common_year, 5, 30), [[-3, DateUnit.MONTH]]
        ) == (common_year, 2, 29)

    def test_shift_ast_year(self):
        delta = FAKE.random_int()
        year = self.random_year()
        expected_year = year + delta
        assert self.l_hijri_cd.shift_ast_year(year, delta) == expected_year

    def test_shift_month(self):
        year, month, _ = self.random_ymd()
        assert self.l_hijri_cd.shift_month(year, month, -24) == (
            year - 2,
            month,
        )
        assert self.l_hijri_cd.shift_month(year, month, -12) == (
            year - 1,
            month,
        )
        assert self.l_hijri_cd.shift_month(year, month, 0) == (year, month)
        assert self.l_hijri_cd.shift_month(year, month, 12) == (
            year + 1,
            month,
        )
        assert self.l_hijri_cd.shift_month(year, month, 24) == (
            year + 2,
            month,
        )
        assert self.l_hijri_cd.shift_month(year, 2, 3) == (year, 5)
        assert self.l_hijri_cd.shift_month(year, 12, 1) == (year + 1, 1)
        assert self.l_hijri_cd.shift_month(year, 8, 7) == (year + 1, 3)
        assert self.l_hijri_cd.shift_month(year, 3, 14) == (year + 1, 5)
        assert self.l_hijri_cd.shift_month(year, 6, 29) == (year + 2, 11)
        assert self.l_hijri_cd.shift_month(year, 10, -1) == (year, 9)
        assert self.l_hijri_cd.shift_month(year, 1, -1) == (year - 1, 12)
        assert self.l_hijri_cd.shift_month(year, 2, -3) == (year - 1, 11)
        assert self.l_hijri_cd.shift_month(year, 5, -7) == (year - 1, 10)
        assert self.l_hijri_cd.shift_month(year, 7, -15) == (year - 1, 4)
        assert self.l_hijri_cd.shift_month(year, 12, -28) == (year - 2, 8)

    #
    # ConvertibleDate.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.l_hijri_cd.convert_ast_ymd((338, 11, 22), self.coptic_cd)
            == (1, 1, 1)
        )
        assert(
            self.l_hijri_cd.convert_ast_ymd((1, 1, 1), self.coptic_cd)
            == (-348, 9, 29)
        )
        # fmt: on
        assert (
            self.l_hijri_cd.convert_ast_ymd(coptic_ymd, self.coptic_cd)
            == l_hijri_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.l_hijri_cd.convert_ast_ymd((1, 1, 1), self.indian_cd)
            == (-561, 12, 20)
        )
        assert (
            self.l_hijri_cd.convert_ast_ymd((545, 4, 28), self.indian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.l_hijri_cd.convert_ast_ymd(indian_ymd, self.indian_cd)
            == l_hijri_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.l_hijri_cd.convert_ast_ymd((622, 7, 19), self.gregorian_cd)
            == (1, 1, 1)
        )
        assert (
            self.l_hijri_cd.convert_ast_ymd((1, 1, 1), self.gregorian_cd)
            == (-640, 5, 18)
        )
        # fmt: on
        assert (
            self.l_hijri_cd.convert_ast_ymd(gregorian_ymd, self.gregorian_cd)
            == l_hijri_ymd
        )

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        l_hijri_ymd = convertdate.islamic.from_gregorian(gyear, gmonth, gday)
        # fmt: off
        assert (
            self.l_hijri_cd.convert_ast_ymd((1, 1, 1), self.julian_cd)
            == (-640, 5, 16)
        )
        assert (
            self.l_hijri_cd.convert_ast_ymd((622, 7, 16), self.julian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.l_hijri_cd.convert_ast_ymd(julian_ymd, self.julian_cd)
            == l_hijri_ymd
        )

    #
    # Ordinals
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.is_descending_era",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    @patch(
        "src.customdate.ConvertibleDate.net_elapsed_special_years",
        return_value=[0, 0],
    )
    @patch("src.db.ConvertibleCalendar.leap_year_cycle_length")
    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    @patch("src.db.ConvertibleCalendar.leap_years_in_normal_cycle")
    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    @patch("src.db.ConvertibleCalendar.days_in_leap_year")
    @patch("src.db.ConvertibleCalendar.days_in_common_year")
    def test_ordinal_date_to_ordinal_for_bh_year(self, *args):
        self.ordinal_conversion_patches(*args)
        # don't test full cycle because that will be verbose
        assert self.l_hijri_cd.ordinal_date_to_ordinal((0, 354)) == 0
        assert self.l_hijri_cd.ordinal_date_to_ordinal((0, 1)) == -353
        assert self.l_hijri_cd.ordinal_date_to_ordinal((-1, 355)) == -354
        assert self.l_hijri_cd.ordinal_date_to_ordinal((-1, 1)) == -708
        assert self.l_hijri_cd.ordinal_date_to_ordinal((-2, 354)) == -709
        assert self.l_hijri_cd.ordinal_date_to_ordinal((-2, 195)) == -868

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.is_descending_era",
        return_value=False,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    @patch(
        "src.customdate.ConvertibleDate.net_elapsed_special_years",
        return_value=[0, 0],
    )
    @patch("src.db.ConvertibleCalendar.leap_year_cycle_length")
    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    @patch("src.db.ConvertibleCalendar.leap_years_in_normal_cycle")
    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    @patch("src.db.ConvertibleCalendar.days_in_leap_year")
    @patch("src.db.ConvertibleCalendar.days_in_common_year")
    def test_ordinal_date_to_ordinal_for_ah_year(self, *args):
        self.ordinal_conversion_patches(*args)
        # don't test full cycle because that will be verbose
        assert self.l_hijri_cd.ordinal_date_to_ordinal((3, 214)) == 923
        assert self.l_hijri_cd.ordinal_date_to_ordinal((2, 355)) == 709
        assert self.l_hijri_cd.ordinal_date_to_ordinal((2, 1)) == 355
        assert self.l_hijri_cd.ordinal_date_to_ordinal((1, 354)) == 354
        assert self.l_hijri_cd.ordinal_date_to_ordinal((1, 1)) == 1

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        year, month, day = self.random_common_ymd()
        year, month, day = convertdate.islamic.to_gregorian(year, month, day)
        day_of_year = self.l_hijri_dc.from_gregorian(year, month, day)
        with pytest.raises(ValueError):
            self.l_hijri_cd.ordinal_date_to_ordinal((year, day_of_year))

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_for_ah_year(self, *_):
        # don't test full cycle because that will be verbose
        assert self.l_hijri_cd.ordinal_to_ordinal_date(836) == (3, 127)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(709) == (2, 355)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(355) == (2, 1)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(354) == (1, 354)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_bh_year(self, *_):
        # don't test full cycle because that will be verbose
        assert self.l_hijri_cd.ordinal_to_ordinal_date(0) == (0, 354)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-354) == (-1, 355)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-709) == (-2, 354)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-768) == (-2, 295)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.l_hijri_cd.ordinal_to_ordinal_date(0) == (0, 354)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-135) == (0, 219)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-199) == (0, 155)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-257) == (0, 97)
        assert self.l_hijri_cd.ordinal_to_ordinal_date(-353) == (0, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.is_descending_era",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_is_reversible_for_bh_year(self, *_):
        bh_ordinal = FAKE.random_int(min=-9999, max=0)
        bh_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=354),
        )
        assert (
            self.l_hijri_cd.ordinal_to_ordinal_date(
                self.l_hijri_cd.ordinal_date_to_ordinal(bh_ordinal_date)
            )
            == bh_ordinal_date
        )
        assert (
            self.l_hijri_cd.ordinal_date_to_ordinal(
                self.l_hijri_cd.ordinal_to_ordinal_date(bh_ordinal)
            )
            == bh_ordinal
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.is_descending_era",
        return_value=False,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_ah_year(self, *_):
        ah_ordinal = FAKE.random_int()
        ah_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=354)
        assert (
            self.l_hijri_cd.ordinal_to_ordinal_date(
                self.l_hijri_cd.ordinal_date_to_ordinal(ah_ordinal_date)
            )
            == ah_ordinal_date
        )
        assert (
            self.l_hijri_cd.ordinal_date_to_ordinal(
                self.l_hijri_cd.ordinal_to_ordinal_date(ah_ordinal)
            )
            == ah_ordinal
        )

    #
    # Cycle methods
    #
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_completed_cycles_for_ah_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(completed_cycles)
        end_year = self.make_cycle_end_year(completed_cycles)
        cycle_year = FAKE.random_int(min=start_year, max=end_year)
        assert self.l_hijri_cd.completed_cycles(1) == 0
        assert self.l_hijri_cd.completed_cycles(30) == 0
        assert self.l_hijri_cd.completed_cycles(31) == 1
        assert self.l_hijri_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_completed_cycles_for_bh_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        end_year = self.make_cycle_end_year(completed_cycles, proleptic=True)
        cycle_year = FAKE.random_int(min=end_year, max=start_year)
        assert self.l_hijri_cd.completed_cycles(0) == 0
        assert self.l_hijri_cd.completed_cycles(-29) == 0
        assert self.l_hijri_cd.completed_cycles(-30) == 1
        assert self.l_hijri_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_cycle_index_for_ah_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        ah_start_year = self.make_cycle_start_year(completed_cycles)
        ah_year = ah_start_year + cycle_index
        assert self.l_hijri_cd.cycle_index(1) == 0
        assert self.l_hijri_cd.cycle_index(10) == 9
        assert self.l_hijri_cd.cycle_index(20) == 19
        assert self.l_hijri_cd.cycle_index(30) == 29
        assert self.l_hijri_cd.cycle_index(31) == 0
        assert (
            self.l_hijri_cd.cycle_index(ah_year, completed_cycles, 1, 1)
            == cycle_index
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_cycle_index_for_bh_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        bh_start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        bh_year = bh_start_year - cycle_index
        assert self.l_hijri_cd.cycle_index(-30) == 0
        assert self.l_hijri_cd.cycle_index(-29) == 29
        assert self.l_hijri_cd.cycle_index(-20) == 20
        assert self.l_hijri_cd.cycle_index(-10) == 10
        assert self.l_hijri_cd.cycle_index(0) == 0
        assert (
            self.l_hijri_cd.cycle_index(bh_year, completed_cycles, 0, -1)
            == cycle_index
        )

    def test_all_cycle_ordinals(self):
        assert self.l_hijri_cd.all_cycle_ordinals == self.all_cycle_ordinals
        with pytest.raises(AttributeError):
            self.l_hijri_cd.all_cycle_ordinals = FAKE.pylist()

    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    def test_days_in_normal_cycle(self, p_common_years_in_normal_cycle):
        cyinc = self.common_years_in_normal_cycle
        p_common_years_in_normal_cycle.__get__ = lambda *_: cyinc

        days_in_normal_cycle = self.l_hijri_dc.from_gregorian(
            *convertdate.islamic.to_gregorian(31, 1, 1)
        )
        assert self.l_hijri_cd.days_in_normal_cycle == days_in_normal_cycle
        with pytest.raises(AttributeError):
            self.l_hijri_cd.days_in_normal_cycle = FAKE.random_int()

    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    def test_common_year_cycle_ordinals(self, patch_all_cycle_ordinals):
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ords = tuple(self.common_ordinals)
        assert self.l_hijri_cd.common_year_cycle_ordinals == common_ords
        with pytest.raises(AttributeError):
            self.l_hijri_cd.common_year_cycle_ordinals = FAKE.pytuple()

    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    def test_common_years_in_normal_cycle(self, p_common_year_cycle_ordinals):
        p_common_year_cycle_ordinals.__get__ = lambda *_: self.common_ordinals
        cyinc = self.common_years_in_normal_cycle
        assert self.l_hijri_cd.common_years_in_normal_cycle == cyinc
        with pytest.raises(AttributeError):
            self.l_hijri_cd.common_years_in_normal_cycle = FAKE.random_int()

    def test_special_years(self):
        ast_year = FAKE.random_int(min=-9999)
        assert self.l_hijri_cd.net_elapsed_special_years(ast_year) == (0, 0)

    #
    # ConvertibleDate.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        l_hijri_cdt = self.l_hijri_cd
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((143, 10, 22)) == (143, 288)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((101, 12, 29)) == (101, 354)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((0, 12, 29)) == (0, 354)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((0, 1, 1)) == (0, 1)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((-100, 2, 15)) == (-100, 45)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        l_hijri_cdt = self.l_hijri_cd
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((2, 1, 1)) == (2, 1)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((1445, 8, 9)) == (1445, 216)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((13, 12, 30)) == (13, 355)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((-6, 4, 18)) == (-6, 107)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((-59, 6, 1)) == (-59, 149)
        assert l_hijri_cdt.ast_ymd_to_ordinal_date((-91, 12, 30)) == (-91, 355)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.l_hijri_cd.ast_ymd_to_ordinal_date(self.random_ymd())

    #
    # ConvertibleDate.ordinal_date_to_ast_ymd
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        l_hijri_cdt = self.l_hijri_cd
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((9, 91)) == (9, 4, 2)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((88, 354)) == (88, 12, 29)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((0, 12)) == (0, 1, 12)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((-8, 39)) == (-8, 2, 9)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((-10, 354)) == (-10, 12, 29)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        l_hijri_cdt = self.l_hijri_cd
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((5, 1)) == (5, 1, 1)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((29, 31)) == (29, 2, 1)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((10, 355)) == (10, 12, 30)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((-1, 355)) == (-1, 12, 30)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((-6, 68)) == (-6, 3, 9)
        assert l_hijri_cdt.ordinal_date_to_ast_ymd((-12, 325)) == (-12, 11, 30)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = common_year, FAKE.random_int(min=1, max=354)
        ast_ymd = common_year, month, day
        assert (
            self.l_hijri_cd.ordinal_date_to_ast_ymd(
                self.l_hijri_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.l_hijri_cd.ast_ymd_to_ordinal_date(
                self.l_hijri_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = leap_year, FAKE.random_int(min=1, max=355)
        ast_ymd = leap_year, month, day
        assert (
            self.l_hijri_cd.ordinal_date_to_ast_ymd(
                self.l_hijri_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.l_hijri_cd.ast_ymd_to_ordinal_date(
                self.l_hijri_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.l_hijri_cd.ordinal_date_to_ast_ymd((1, 0))

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        hr_bh_year = abs(self.random_bce_year()) + 1
        ast_bh_year = -hr_bh_year + 1
        hr_ah_year = self.random_ce_year()
        assert self.l_hijri_cd.hr_to_ast(1, 1) == 1
        assert self.l_hijri_cd.hr_to_ast(1, 0) == 0
        assert self.l_hijri_cd.hr_to_ast(2, 0) == -1
        assert self.l_hijri_cd.hr_to_ast(hr_bh_year, 0) == ast_bh_year
        assert self.l_hijri_cd.hr_to_ast(hr_ah_year, 1) == hr_ah_year

    def test_ast_to_hr(self):
        ast_bh_year = self.random_bce_year()
        hr_bh_year = abs(ast_bh_year - 1)
        ast_ah_year = self.random_ce_year()
        assert self.l_hijri_cd.ast_to_hr(1) == (1, 1)
        assert self.l_hijri_cd.ast_to_hr(0) == (1, 0)
        assert self.l_hijri_cd.ast_to_hr(-1) == (2, 0)
        assert self.l_hijri_cd.ast_to_hr(ast_bh_year) == (hr_bh_year, 0)
        assert self.l_hijri_cd.ast_to_hr(ast_ah_year) == (ast_ah_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        hr_ce_year = ast_ce_year
        assert (
            self.l_hijri_cd.hr_to_ast(*self.l_hijri_cd.ast_to_hr(ast_bce_year))
            == ast_bce_year
        )
        assert (
            self.l_hijri_cd.hr_to_ast(*self.l_hijri_cd.ast_to_hr(ast_ce_year))
            == ast_ce_year
        )
        assert self.l_hijri_cd.ast_to_hr(
            self.l_hijri_cd.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.l_hijri_cd.ast_to_hr(
            self.l_hijri_cd.hr_to_ast(hr_ce_year, 1)
        ) == (hr_ce_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ah_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.l_hijri_cd.ast_to_hr(ast_ah_year)

    def test_parse_hr_date(self):
        ah_ymd = self.random_ce_ymd()
        ah_ast_year, ah_month, ah_day = ah_ymd
        ah_hr_year = ah_ast_year

        bh_ymd = self.random_bce_ymd()
        bh_ast_year, bh_month, bh_day = bh_ymd
        bh_hr_year = abs(bh_ast_year - 1)

        ah_hr_date = self.l_hijri_cd.date_sep.join(
            [str(ah_hr_year), str(ah_month), str(ah_day), "AH"]
        )
        bh_hr_date = self.l_hijri_cd.date_sep.join(
            [str(bh_hr_year), str(bh_month), str(bh_day), "BH"]
        )
        assert self.l_hijri_cd.parse_hr_date(ah_hr_date) == ah_ymd
        assert self.l_hijri_cd.parse_hr_date(bh_hr_date) == bh_ymd

    def test_format_hr_date(self):
        bce_ast_ymd = self.random_bce_ymd()
        bce_ast_year, bce_month, bce_day = bce_ast_ymd
        bce_hr_year = abs(bce_ast_year - 1)
        bce_hr_date = self.l_hijri_cd.date_sep.join(
            [str(bce_hr_year), str(bce_month), str(bce_day), "BH"]
        )

        ce_ast_ymd = self.random_ce_ymd()
        ce_ast_year, ce_month, ce_day = ce_ast_ymd
        ce_hr_date = self.l_hijri_cd.date_sep.join(
            [str(ce_ast_year), str(ce_month), str(ce_day), "AH"]
        )
        assert self.l_hijri_cd.format_hr_date(bce_ast_ymd) == bce_hr_date
        assert self.l_hijri_cd.format_hr_date(ce_ast_ymd) == ce_hr_date

    #
    # Eras
    #
    def test_era(self):
        bh_year = self.random_bce_year()
        ah_year = self.random_ce_year()
        assert self.l_hijri_cd.era(bh_year) == "BH"
        assert self.l_hijri_cd.era(ah_year) == "AH"

    def test_is_descending_era(self):
        bh_year = self.random_bce_year()
        sh_year = self.random_ce_year()
        assert self.l_hijri_cd.is_descending_era(bh_year)
        assert self.l_hijri_cd.is_descending_era(sh_year) is False

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        # all_cycle_ordinals reverses to early when patched...so don't patch
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.l_hijri_cd.is_leap_year(common_bce_year) is False
        assert self.l_hijri_cd.is_leap_year(common_ce_year) is False
        assert self.l_hijri_cd.is_leap_year(leap_bce_year)
        assert self.l_hijri_cd.is_leap_year(leap_ce_year)

    #
    # ConvertibleDate.is_valid_ast_ymd
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=354)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.l_hijri_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=355)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.l_hijri_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=31)
        assert not self.l_hijri_cd.is_valid_ast_ymd((year, bad_month, day))
        assert not self.l_hijri_cd.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDate.is_valid_month
    #
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_month(self, _):
        year, month, _ = self.random_ymd()
        negative_month = FAKE.random_int(min=-9999, max=-1)
        too_big_month = FAKE.random_int(min=13)
        assert self.l_hijri_cd.is_valid_month(year, month)
        assert self.l_hijri_cd.is_valid_month(year, negative_month) is False
        assert self.l_hijri_cd.is_valid_month(year, too_big_month) is False

    #
    # ConvertibleDate.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=354)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=354)
        bad_day_of_year = FAKE.random_int(min=355)
        l_hijri_cdt = self.l_hijri_cd
        assert not l_hijri_cdt.is_valid_ordinal_date((1, 355))
        assert l_hijri_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not l_hijri_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=355)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=355)
        bad_day_of_year = FAKE.random_int(min=356)
        l_hijri_cdt = self.l_hijri_cd
        assert not l_hijri_cdt.is_valid_ordinal_date((1, 356))
        assert l_hijri_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not l_hijri_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDate.gen_years_before_era, not applicable

    #
    # ConvertibleDate.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.l_hijri_cd.days_in_months(common_year)
            # fmt: off
            == [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.l_hijri_cd.days_in_months(leap_year)
            # fmt: off
            == [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30]
            # fmt: on
        )

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29),
    )
    def test_days_in_month_for_common_month(self, _):
        common_year, month, _ = self.random_common_ymd()
        assert self.l_hijri_cd.days_in_month(
            common_year, month
        ) == convertdate.islamic.month_length(common_year, month)

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30),
    )
    def test_days_in_month_for_leap_month(self, _):
        leap_year, month, _ = self.random_leap_ymd()
        assert self.l_hijri_cd.days_in_month(
            leap_year, month
        ) == convertdate.islamic.month_length(leap_year, month)

    #
    # ConvertibleDate.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.l_hijri_cd.days_in_year(common_year) == 354

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.l_hijri_cd.days_in_year(leap_year) == 355

    #
    # ConvertibleDate.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.l_hijri_cd.months_in_year(common_year) == 12

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.l_hijri_cd.months_in_year(leap_year) == 12

    #
    # Weeks
    #
    @patch("src.db.ConvertibleCalendar.days_in_weeks", return_value=7)
    def test_day_of_week(self, _):
        bh_year, bh_month, bh_day = self.random_bce_ymd()
        bh_julian_day = convertdate.islamic.to_jd(bh_year, bh_month, bh_day)
        bh_ordinal = self.l_hijri_dc.from_jd(bh_julian_day) + 1

        ah_year, ah_month, ah_day = self.random_ce_ymd()
        ah_julian_day = convertdate.islamic.to_jd(ah_year, ah_month, ah_day)
        ah_ordinal = self.l_hijri_dc.from_jd(ah_julian_day) + 1
        assert self.l_hijri_cd.day_of_week(1) == 5  # 1/1/1 is the sixth day
        assert self.l_hijri_cd.day_of_week(2) == 6
        assert self.l_hijri_cd.day_of_week(3) == 0
        assert self.l_hijri_cd.day_of_week(4) == 1
        assert self.l_hijri_cd.day_of_week(5) == 2
        assert self.l_hijri_cd.day_of_week(6) == 3
        assert self.l_hijri_cd.day_of_week(7) == 4
        assert self.l_hijri_cd.day_of_week(8) == 5
        assert (
            self.l_hijri_cd.day_of_week(bh_ordinal)
            == (convertdate.utils.jwday(bh_julian_day) + 1) % 7
        )
        assert (
            self.l_hijri_cd.day_of_week(ah_ordinal)
            == (convertdate.utils.jwday(ah_julian_day) + 1) % 7
        )
