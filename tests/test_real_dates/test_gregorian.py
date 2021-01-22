import convertdate
import pytest

from .utils import RealCalendarTestCase
from collections import deque
from convertdate import gregorian, ordinal, utils
from tests.utils import FAKE
from unittest.mock import patch


class GregorianTest(RealCalendarTestCase):
    """
    Can the database represent the Gregorian calendar?
    Years are astronomical unless labeled otherwise
    """

    #
    # Helper functions
    #
    def setUp(self):
        super(GregorianTest, self).setUp()
        self.main_calendar = self.gregorian
        self.common_ordinals = list(
            set(range(1, 401)) ^ set(self.gregorian.leap_year_cycle_ordinals)
        )
        self.common_ordinals.sort()
        self.cycle_length = 400
        self.all_cycle_ordinals = deque(range(1, 401))
        self.leap_years_in_normal_cycle = 97
        self.common_years_in_normal_cycle = 303
        self.days_in_leap_years = 366
        self.days_in_common_year = 365

    def random_common_year(self) -> int:
        return self.random_gregorian_common_year()

    def random_leap_year(self) -> int:
        return self.random_gregorian_leap_year()

    def random_common_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_common_ymd()

    def random_common_bce_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_common_bce_ymd()

    def random_common_ce_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_common_ce_ymd()

    def random_leap_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_leap_ymd()

    def random_leap_bce_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_leap_bce_ymd()

    def random_leap_ce_ymd(self) -> tuple[int, int, int]:
        return self.random_gregorian_leap_ce_ymd()

    def random_ce_ordinal_and_ordinal_date(self) -> tuple[int, tuple]:
        year, month, day = self.random_ce_ymd()
        ce_ordinal = self.gregorian_dc.from_gregorian(year, month, day) + 1
        ce_ordinal_date = ordinal.from_gregorian(year, month, day)
        return ce_ordinal, ce_ordinal_date

    def random_bce_ordinal_and_ordinal_date(self) -> tuple[int, tuple]:
        year, month, day = self.random_bce_ymd()
        bce_ordinal = self.gregorian_dc.from_gregorian(year, month, day) + 1
        bce_ordinal_date = ordinal.from_gregorian(year, month, day)
        return bce_ordinal, bce_ordinal_date

    def random_common_bce_ordinal_and_ordinal_date(self) -> tuple[int, tuple]:
        year, month, day = self.random_common_bce_ymd()
        bce_ordinal = self.gregorian_dc.from_gregorian(year, month, day) + 1
        bce_ordinal_date = ordinal.from_gregorian(year, month, day)
        return bce_ordinal, bce_ordinal_date

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
    # ConvertibleDate.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ast_ymd = self.random_ymd()
        coptic_ast_ymd = convertdate.coptic.from_gregorian(*gregorian_ast_ymd)
        # fmt: off
        assert (
            self.gregorian_cd.convert_ast_ymd((1, 1, 1), self.coptic_cd)
            == (284, 8, 29)
        )
        # fmt: on
        assert (
            self.gregorian_cd.convert_ast_ymd(coptic_ast_ymd, self.coptic_cd)
            == gregorian_ast_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ast_ymd = self.random_convertible_gregorian_ymd()
        indian_ast_ymd = self.make_indian_ast_ymd(gregorian_ast_ymd)
        # fmt: off
        assert (
            self.gregorian_cd.convert_ast_ymd((1, 1, 1), self.indian_cd)
            == (78, 3, 22)
        )
        assert (
            self.gregorian_cd.convert_ast_ymd((3, 2, 1), self.indian_cd)
            == (80, 4, 21)
        )
        # fmt: on
        assert (
            self.gregorian_cd.convert_ast_ymd(indian_ast_ymd, self.indian_cd)
            == gregorian_ast_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        year, month, day = self.random_ymd()
        l_hijri_ast_ymd = convertdate.islamic.from_gregorian(year, month, day)
        l_hijri_cdt = self.l_hijri_cd
        # fmt: off
        assert (
            self.gregorian_cd.convert_ast_ymd((1, 1, 1), l_hijri_cdt)
            == (622, 7, 19)
        )
        assert (
            self.gregorian_cd.convert_ast_ymd((-640, 5, 18), l_hijri_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert self.gregorian_cd.convert_ast_ymd(
            l_hijri_ast_ymd, l_hijri_cdt
        ) == (year, month, day)

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        year, month, day = self.random_convertible_gregorian_ymd()
        julian_ast_ymd = convertdate.julian.from_gregorian(year, month, day)
        # fmt: off
        assert (
            self.gregorian_cd.convert_ast_ymd((1, 1, 1), self.julian_cd)
            == (0, 12, 30)
        )
        assert (
            self.gregorian_cd.convert_ast_ymd((1, 1, 3), self.julian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert self.gregorian_cd.convert_ast_ymd(
            julian_ast_ymd, self.julian_cd
        ) == (year, month, day)

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
    def test_ordinal_date_to_ordinal_for_bce_year(self, *args):
        # patching reverses all_cycle_ordinals for some reason...so don't patch
        _ordinal, ordinal_date = self.random_bce_ordinal_and_ordinal_date()
        assert self.gregorian_cd.ordinal_date_to_ordinal((0, 366)) == 0
        assert self.gregorian_cd.ordinal_date_to_ordinal((0, 1)) == -365
        assert self.gregorian_cd.ordinal_date_to_ordinal((-1, 365)) == -366
        assert self.gregorian_cd.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.gregorian_cd.ordinal_date_to_ordinal((-2, 365)) == -731
        assert (
            self.gregorian_cd.ordinal_date_to_ordinal(ordinal_date) == _ordinal
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
    def test_ordinal_date_to_ordinal_for_ce_year(self, *args):
        self.ordinal_conversion_patches(*args)

        _ordinal, ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        assert self.gregorian_cd.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.gregorian_cd.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.gregorian_cd.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.gregorian_cd.ordinal_date_to_ordinal((1, 1)) == 1
        assert (
            self.gregorian_cd.ordinal_date_to_ordinal(ordinal_date) == _ordinal
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ordinal_raises(self, *_):
        year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(year, month, day)
        with pytest.raises(ValueError):
            self.gregorian_cd.ordinal_date_to_ordinal(ordinal_date)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_bce_year(self, *_):
        bce_ordinal_n_ordinal_date = self.random_bce_ordinal_and_ordinal_date()
        bce_ordinal, bce_ordinal_date = bce_ordinal_n_ordinal_date
        assert self.gregorian_cd.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-366) == (-1, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert (
            self.gregorian_cd.ordinal_to_ordinal_date(bce_ordinal)
            == bce_ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_for_ce_year(self, *_):
        ce_ordinal, ce_ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        assert self.gregorian_cd.ordinal_to_ordinal_date(730) == (2, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(1) == (1, 1)
        assert (
            self.gregorian_cd.ordinal_to_ordinal_date(ce_ordinal)
            == ce_ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        year = 0
        _, month, day = self.random_leap_bce_ymd()
        _ordinal = self.gregorian_dc.from_gregorian(year, month, day) + 1
        ordinal_date = ordinal.from_gregorian(year, month, day)
        assert self.gregorian_cd.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-365) == (0, 1)
        assert (
            self.gregorian_cd.ordinal_to_ordinal_date(_ordinal) == ordinal_date
        )

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
    def test_ordinal_to_ordinal_date_is_reversible_for_bce_year(self, *_):
        bce_ymd = self.random_bce_ymd()
        bce_ordinal = self.gregorian_dc.from_gregorian(*bce_ymd) + 1
        bce_ordinal_date = ordinal.from_gregorian(*bce_ymd)
        assert (
            self.gregorian_cd.ordinal_to_ordinal_date(
                self.gregorian_cd.ordinal_date_to_ordinal(bce_ordinal_date)
            )
            == bce_ordinal_date
        )
        assert (
            self.gregorian_cd.ordinal_date_to_ordinal(
                self.gregorian_cd.ordinal_to_ordinal_date(bce_ordinal)
            )
            == bce_ordinal
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
    def test_ordinal_to_ordinal_date_is_reversible_for_ce_year(self, *_):
        ce_ymd = self.random_ce_ymd()
        ce_ordinal = self.gregorian_dc.from_gregorian(*ce_ymd) + 1
        ce_ordinal_date = ordinal.from_gregorian(*ce_ymd)
        assert (
            self.gregorian_cd.ordinal_to_ordinal_date(
                self.gregorian_cd.ordinal_date_to_ordinal(ce_ordinal_date)
            )
            == ce_ordinal_date
        )
        assert (
            self.gregorian_cd.ordinal_date_to_ordinal(
                self.gregorian_cd.ordinal_to_ordinal_date(ce_ordinal)
            )
            == ce_ordinal
        )

    def test_all_cycle_ordinals(self):
        assert self.gregorian_cd.all_cycle_ordinals == deque(range(1, 401))
        with pytest.raises(AttributeError):
            self.gregorian_cd.all_cycle_ordinals = FAKE.pylist()

    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    def test_days_in_normal_cycle(self, p_common_years_in_normal_cycle):
        cyinc = self.common_years_in_normal_cycle
        p_common_years_in_normal_cycle.__get__ = lambda *_: cyinc
        # see datetime._DI400Y
        assert self.gregorian_cd.days_in_normal_cycle == 146097
        with pytest.raises(AttributeError):
            self.gregorian_cd.days_in_normal_cycle = FAKE.random_int()

    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    def test_common_year_cycle_ordinals(self, patch_all_cycle_ordinals):
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ords = tuple(self.common_ordinals)
        assert self.gregorian_cd.common_year_cycle_ordinals == common_ords
        with pytest.raises(AttributeError):
            self.gregorian_cd.common_year_cycle_ordinals = FAKE.pytuple()

    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    def test_common_years_in_normal_cycle(self, p_common_year_cycle_ordinals):
        p_common_year_cycle_ordinals.__get__ = lambda *_: self.common_ordinals
        cyinc = self.common_years_in_normal_cycle
        assert self.gregorian_cd.common_years_in_normal_cycle == cyinc
        with pytest.raises(AttributeError):
            self.gregorian_cd.common_years_in_normal_cycle = FAKE.random_int()

    def test_special_years(self):
        ast_year = FAKE.random_int(min=-9999)
        assert self.gregorian_cd.net_elapsed_special_years(ast_year) == (0, 0)

    #
    # ConvertibleDate.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.gregorian_cd.ast_ymd_to_ordinal_date(
            (year, month, day)
        ) == ordinal.from_gregorian(year, month, day)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.gregorian_cd.ast_ymd_to_ordinal_date(
            (year, month, day)
        ) == ordinal.from_gregorian(year, month, day)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.gregorian_cd.ast_ymd_to_ordinal_date(self.random_ymd())

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
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(common_year, month, day)
        ast_ymd = common_year, month, day
        assert self.gregorian_cd.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert (
            self.gregorian_cd.ordinal_date_to_ast_ymd(ordinal_date) == ast_ymd
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = ordinal.from_gregorian(leap_year, month, day)
        ast_ymd = (leap_year, month, day)
        assert (
            # fmt: off
            self.gregorian_cd.ordinal_date_to_ast_ymd((0, 366)) == (0, 12, 31)
            # fmt: on
        )
        assert (
            self.gregorian_cd.ordinal_date_to_ast_ymd(ordinal_date) == ast_ymd
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(common_year, month, day)
        ast_ymd = common_year, month, day
        assert (
            self.gregorian_cd.ordinal_date_to_ast_ymd(
                self.gregorian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.gregorian_cd.ast_ymd_to_ordinal_date(
                self.gregorian_cd.ordinal_date_to_ast_ymd(ordinal_date)
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
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = ordinal.from_gregorian(leap_year, month, day)
        ast_ymd = leap_year, month, day
        assert (
            self.gregorian_cd.ordinal_date_to_ast_ymd(
                self.gregorian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.gregorian_cd.ast_ymd_to_ordinal_date(
                self.gregorian_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, *_):
        ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        with pytest.raises(ValueError):
            self.gregorian_cd.ordinal_date_to_ast_ymd(ordinal_date)

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        hr_bce_year = abs(self.random_bce_year()) + 1
        ast_bce_year = -hr_bce_year + 1
        hr_ce_year = self.random_ce_year()
        assert self.gregorian_cd.hr_to_ast(1, 1) == 1
        assert self.gregorian_cd.hr_to_ast(1, 0) == 0
        assert self.gregorian_cd.hr_to_ast(2, 0) == -1
        assert self.gregorian_cd.hr_to_ast(hr_bce_year, 0) == ast_bce_year
        assert self.gregorian_cd.hr_to_ast(hr_ce_year, 1) == hr_ce_year

    def test_ast_to_hr(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        assert self.gregorian_cd.ast_to_hr(1) == (1, 1)
        assert self.gregorian_cd.ast_to_hr(0) == (1, 0)
        assert self.gregorian_cd.ast_to_hr(-1) == (2, 0)
        assert self.gregorian_cd.ast_to_hr(ast_bce_year) == (hr_bce_year, 0)
        assert self.gregorian_cd.ast_to_hr(ast_ce_year) == (ast_ce_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        hr_ce_year = ast_ce_year
        assert (
            self.gregorian_cd.hr_to_ast(
                *self.gregorian_cd.ast_to_hr(ast_bce_year)
            )
            == ast_bce_year
        )
        assert (
            self.gregorian_cd.hr_to_ast(
                *self.gregorian_cd.ast_to_hr(ast_ce_year)
            )
            == ast_ce_year
        )
        assert self.gregorian_cd.ast_to_hr(
            self.gregorian_cd.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.gregorian_cd.ast_to_hr(
            self.gregorian_cd.hr_to_ast(hr_ce_year, 1)
        ) == (hr_ce_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ce_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.gregorian_cd.ast_to_hr(ast_ce_year)

    def test_parse_hr_date(self):
        ce_ymd = self.random_ce_ymd()
        ce_ast_year, ce_month, ce_day = ce_ymd
        ce_hr_year = ce_ast_year

        bce_ymd = self.random_bce_ymd()
        bce_ast_year, bce_month, bce_day = bce_ymd
        bce_hr_year = abs(bce_ast_year - 1)

        ce_hr_date = self.gregorian_cd.date_sep.join(
            [str(ce_hr_year), str(ce_month), str(ce_day), "CE"]
        )
        bce_hr_date = self.gregorian_cd.date_sep.join(
            [str(bce_hr_year), str(bce_month), str(bce_day), "BCE"]
        )
        assert self.gregorian_cd.parse_hr_date(ce_hr_date) == ce_ymd
        assert self.gregorian_cd.parse_hr_date(bce_hr_date) == bce_ymd

    def test_format_hr_date(self):
        bce_ast_ymd = self.random_bce_ymd()
        bce_ast_year, bce_month, bce_day = bce_ast_ymd
        bce_hr_year = abs(bce_ast_year - 1)
        bce_hr_date = self.gregorian_cd.date_sep.join(
            [str(bce_hr_year), str(bce_month), str(bce_day), "BCE"]
        )

        ce_ast_ymd = self.random_ce_ymd()
        ce_ast_year, ce_month, ce_day = ce_ast_ymd
        ce_hr_date = self.gregorian_cd.date_sep.join(
            [str(ce_ast_year), str(ce_month), str(ce_day), "CE"]
        )
        assert self.gregorian_cd.format_hr_date(bce_ast_ymd) == bce_hr_date
        assert self.gregorian_cd.format_hr_date(ce_ast_ymd) == ce_hr_date

    #
    # Eras
    #
    def test_era(self):
        bce_year = self.random_bce_year()
        ce_year = self.random_ce_year()
        assert self.gregorian_cd.era(bce_year) == "BCE"
        assert self.gregorian_cd.era(ce_year) == "CE"

    def test_is_descending_era(self):
        bce_year = self.random_bce_year()
        ce_year = self.random_ce_year()
        assert self.gregorian_cd.is_descending_era(bce_year)
        assert self.gregorian_cd.is_descending_era(ce_year) is False

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.gregorian_cd.is_leap_year(common_bce_year) is False
        assert self.gregorian_cd.is_leap_year(common_ce_year) is False
        assert self.gregorian_cd.is_leap_year(leap_bce_year) is True
        assert self.gregorian_cd.is_leap_year(leap_ce_year) is True

    #
    # ConvertibleDate.is_valid_ast_ymd
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        ast_year, month, day = self.random_common_ymd()
        assert self.gregorian_cd.is_valid_ast_ymd((ast_year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        ast_year, month, day = self.random_leap_ymd()
        assert self.gregorian_cd.is_valid_ast_ymd((ast_year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        assert not self.gregorian_cd.is_valid_ast_ymd((year, bad_month, day))
        assert not self.gregorian_cd.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDate.is_valid_month
    #
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_month(self, _):
        year, month, _ = self.random_ymd()
        negative_month = FAKE.random_int(min=-9999, max=-1)
        too_big_month = FAKE.random_int(min=13)
        assert self.gregorian_cd.is_valid_month(year, month)
        assert self.gregorian_cd.is_valid_month(year, negative_month) is False
        assert self.gregorian_cd.is_valid_month(year, too_big_month) is False

    #
    # ConvertibleDate.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        valid_ordinal_date = ordinal.from_gregorian(*self.random_common_ymd())
        invalid_ordinal_date = (FAKE.random_int(), FAKE.random_int(min=366))
        assert self.gregorian_cd.is_valid_ordinal_date(valid_ordinal_date)
        assert not self.gregorian_cd.is_valid_ordinal_date(
            invalid_ordinal_date
        )

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        valid_ordinal_date = ordinal.from_gregorian(*self.random_leap_ymd())
        invalid_ordinal_date = (FAKE.random_int(), FAKE.random_int(min=367))
        assert self.gregorian_cd.is_valid_ordinal_date(valid_ordinal_date)
        assert not self.gregorian_cd.is_valid_ordinal_date(
            invalid_ordinal_date
        )

    # skip ConvertibleDate.gen_years_before_era, not applicable

    #
    # ConvertibleDate.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.gregorian_cd.days_in_months(common_year)
            # fmt: off
            == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.gregorian_cd.days_in_months(leap_year)
            # fmt: off
            == [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_days_in_month_for_common_month(self, _):
        common_year, month, _ = self.random_common_ymd()
        assert self.gregorian_cd.days_in_month(
            common_year, month
        ) == convertdate.gregorian.month_length(common_year, month)

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_days_in_month_for_leap_month(self, _):
        leap_year, month, _ = self.random_leap_ymd()
        assert self.gregorian_cd.days_in_month(
            leap_year, month
        ) == convertdate.gregorian.month_length(leap_year, month)

    #
    # ConvertibleDate.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.gregorian_cd.days_in_year(common_year) == 365

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.gregorian_cd.days_in_year(leap_year) == 366

    #
    # ConvertibleDate.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_ast_year = self.random_common_year()
        assert self.gregorian_cd.months_in_year(common_ast_year) == 12

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_ast_year = self.random_leap_year()
        assert self.gregorian_cd.months_in_year(leap_ast_year) == 12

    #
    # Weeks
    #
    @patch("src.db.ConvertibleCalendar.days_in_weeks", return_value=7)
    def test_day_of_week(self, _):
        daycount = self.gregorian_dc
        bce_year, bce_month, bce_day = self.random_bce_ymd()
        bce_julian_day = gregorian.to_jd(bce_year, bce_month, bce_day)
        bce_ordinal = daycount.from_gregorian(bce_year, bce_month, bce_day) + 1

        ce_year, ce_month, ce_day = self.random_ce_ymd()
        ce_julian_day = gregorian.to_jd(ce_year, ce_month, ce_day)
        ce_ordinal = daycount.from_gregorian(ce_year, ce_month, ce_day) + 1
        assert self.gregorian_cd.day_of_week(1) == 0  # 1/1/1/CE is a Monday
        assert self.gregorian_cd.day_of_week(2) == 1  # Tuesday
        assert self.gregorian_cd.day_of_week(3) == 2  # Wednesday
        assert self.gregorian_cd.day_of_week(4) == 3  # Thursday
        assert self.gregorian_cd.day_of_week(5) == 4  # Friday
        assert self.gregorian_cd.day_of_week(6) == 5  # Saturday
        assert self.gregorian_cd.day_of_week(7) == 6  # Sunday
        assert self.gregorian_cd.day_of_week(8) == 0  # Monday
        assert self.gregorian_cd.day_of_week(bce_ordinal) == utils.jwday(
            bce_julian_day
        )
        assert self.gregorian_cd.day_of_week(ce_ordinal) == utils.jwday(
            ce_julian_day
        )
