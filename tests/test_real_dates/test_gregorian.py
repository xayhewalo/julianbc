import convertdate
import pytest

from .utils import RealCalendarTestCase
from collections import deque
from convertdate import gregorian, ordinal, utils
from src.customdate import DateUnit
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
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    @patch(
        "src.customdate.ConvertibleDate.net_elapsed_special_years",
        return_value=[0, 0],
    )
    def test_ordinal_date_to_ordinal_for_bce_year(self, *_):
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
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_bce_year(self, *_):
        bce_ordinal_n_ordinal_date = self.random_bce_ordinal_and_ordinal_date()
        bce_ordinal, bce_ordinal_date = bce_ordinal_n_ordinal_date
        assert self.gregorian_cd.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-365) == (0, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-366) == (-1, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-730) == (-1, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1095) == (-2, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1096) == (-3, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1460) == (-3, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1461) == (-4, 366)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1826) == (-4, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-1827) == (-5, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(-2191) == (-5, 1)
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
        assert self.gregorian_cd.ordinal_to_ordinal_date(1462) == (5, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(1461) == (4, 366)
        assert self.gregorian_cd.ordinal_to_ordinal_date(1096) == (4, 1)
        assert self.gregorian_cd.ordinal_to_ordinal_date(1095) == (3, 365)
        assert self.gregorian_cd.ordinal_to_ordinal_date(731) == (3, 1)
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
    # don't patch _start_and_sign, loops can temporarily move into diff era
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
    # don't patch _start_and_sign, loops can temporarily move into diff era
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

    #
    # Cycle methods
    #
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_completed_cycles_for_ce_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(completed_cycles)
        end_year = self.make_cycle_end_year(completed_cycles)
        cycle_year = FAKE.random_int(min=start_year, max=end_year)
        assert self.gregorian_cd.completed_cycles(1) == 0
        assert self.gregorian_cd.completed_cycles(400) == 0
        assert self.gregorian_cd.completed_cycles(401) == 1
        assert (
            self.gregorian_cd.completed_cycles(cycle_year) == completed_cycles
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_completed_cycles_for_bce_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        end_year = self.make_cycle_end_year(completed_cycles, proleptic=True)
        cycle_year = FAKE.random_int(min=end_year, max=start_year)
        assert self.gregorian_cd.completed_cycles(0) == 0
        assert self.gregorian_cd.completed_cycles(-399) == 0
        assert self.gregorian_cd.completed_cycles(-400) == 1
        assert (
            self.gregorian_cd.completed_cycles(cycle_year) == completed_cycles
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_cycle_index_for_ce_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        ad_start_year = self.make_cycle_start_year(completed_cycles)
        ad_year = ad_start_year + cycle_index
        assert self.gregorian_cd.cycle_index(1) == 0
        assert self.gregorian_cd.cycle_index(100) == 99
        assert self.gregorian_cd.cycle_index(200) == 199
        assert self.gregorian_cd.cycle_index(300) == 299
        assert self.gregorian_cd.cycle_index(400) == 399
        assert self.gregorian_cd.cycle_index(401) == 0
        assert (
            self.gregorian_cd.cycle_index(ad_year, completed_cycles, 1, 1)
            == cycle_index
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_cycle_index_for_bce_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        bce_start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        bce_year = bce_start_year - cycle_index
        assert self.gregorian_cd.cycle_index(-400) == 0
        assert self.gregorian_cd.cycle_index(-399) == 399
        assert self.gregorian_cd.cycle_index(-300) == 300
        assert self.gregorian_cd.cycle_index(-200) == 200
        assert self.gregorian_cd.cycle_index(-100) == 100
        assert self.gregorian_cd.cycle_index(0) == 0
        assert (
            self.gregorian_cd.cycle_index(bce_year, completed_cycles, 0, -1)
            == cycle_index
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
        assert self.gregorian_cd.shift_ast_ymd(ymd, zero_interval) == ymd
        # fmt: off
        assert self.gregorian_cd.shift_ast_ymd(
            (ast_year, 7, 27), plus_years
        ) == (ast_year + plus_delta, 7, 27)
        assert self.gregorian_cd.shift_ast_ymd(
            (ast_year, 1, 28), plus_months
        ) == (ast_year, 1 + plus_delta, 28)
        # fmt: on
        assert self.gregorian_cd.shift_ast_ymd(
            (ast_year, 3, 15), [[3, DateUnit.YEAR], [2, DateUnit.MONTH]]
        ) == (ast_year + 3, 5, 15)
        assert self.gregorian_cd.shift_ast_ymd(
            (ast_year, 9, 25), [[1, DateUnit.YEAR], [-4, DateUnit.MONTH]]
        ) == (ast_year + 1, 5, 25)

    def test_shift_ast_ymd_to_invalid_day(self):
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.gregorian_cd.shift_ast_ymd(
            (common_year, 1, 30), [[1, DateUnit.MONTH]]
        ) == (common_year, 2, 28)
        assert self.gregorian_cd.shift_ast_ymd(
            (leap_year, 1, 31), [[1, DateUnit.MONTH]]
        ) == (leap_year, 2, 29)
        assert self.gregorian_cd.shift_ast_ymd(
            (2, 3, 31), [[-1, DateUnit.MONTH]]
        ) == (2, 2, 28)
        assert self.gregorian_cd.shift_ast_ymd(
            (4, 5, 31), [[-1, DateUnit.MONTH]]
        ) == (4, 4, 30)

    def test_shift_ast_year(self):
        delta = FAKE.random_int()
        year = self.random_year()
        expected_year = year + delta
        assert self.gregorian_cd.shift_ast_year(year, delta) == expected_year

    def test_shift_month(self):
        year, month, _ = self.random_ymd()
        assert self.gregorian_cd.shift_month(year, month, -24) == (
            year - 2,
            month,
        )
        assert self.gregorian_cd.shift_month(year, month, -12) == (
            year - 1,
            month,
        )
        assert self.gregorian_cd.shift_month(year, month, 0) == (year, month)
        assert self.gregorian_cd.shift_month(year, month, 12) == (
            year + 1,
            month,
        )
        assert self.gregorian_cd.shift_month(year, month, 24) == (
            year + 2,
            month,
        )
        assert self.gregorian_cd.shift_month(year, 2, 3) == (year, 5)
        assert self.gregorian_cd.shift_month(year, 12, 1) == (year + 1, 1)
        assert self.gregorian_cd.shift_month(year, 8, 7) == (year + 1, 3)
        assert self.gregorian_cd.shift_month(year, 3, 14) == (year + 1, 5)
        assert self.gregorian_cd.shift_month(year, 6, 29) == (year + 2, 11)
        assert self.gregorian_cd.shift_month(year, 10, -1) == (year, 9)
        assert self.gregorian_cd.shift_month(year, 1, -1) == (year - 1, 12)
        assert self.gregorian_cd.shift_month(year, 2, -3) == (year - 1, 11)
        assert self.gregorian_cd.shift_month(year, 5, -7) == (year - 1, 10)
        assert self.gregorian_cd.shift_month(year, 7, -15) == (year - 1, 4)
        assert self.gregorian_cd.shift_month(year, 12, -28) == (year - 2, 8)

    #
    # Next DateUnit
    #

    # ConvertibleDate.next_ast_ymd tested in test_customdate
    # ConvertibleDate.next_era tested in test_customdate
    # ConvertibleDate.next_ast_year tested in test_customdate

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_month_moving_forward(self, _):
        assert self.gregorian_cd.next_month(1241, 5, 5, True) == (1241, 10, 1)
        assert self.gregorian_cd.next_month(635, 7, 4, True) == (635, 8, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_month_moving_backward(self, _):
        assert self.gregorian_cd.next_month(401, 5, 1, False) == (401, 4, 1)
        assert self.gregorian_cd.next_month(345, 11, 6, False) == (345, 6, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_day_moving_forward(self, _):
        assert self.gregorian_cd.next_day((231, 9, 9), 4, True) == (231, 9, 12)
        assert self.gregorian_cd.next_day((21, 12, 31), 1, True) == (22, 1, 1)
        assert self.gregorian_cd.next_day((43, 2, 28), 10, True) == (43, 3, 10)
        assert self.gregorian_cd.next_day((4, 2, 29), 4, True) == (4, 3, 4)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_day_moving_backward(self, _):
        assert self.gregorian_cd.next_day((23, 5, 2), 2, False) == (23, 4, 30)
        assert self.gregorian_cd.next_day((84, 10, 9), 4, False) == (84, 10, 8)
        assert self.gregorian_cd.next_day((12, 3, 1), 1, False) == (12, 2, 29)
        assert self.gregorian_cd.next_day((15, 3, 4), 5, False) == (15, 2, 25)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test__overflow_month_moving_forward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.gregorian_cd._overflow_month(year, month) == (year, month)
        assert self.gregorian_cd._overflow_month(common_year, 13, True) == (
            common_year + 1,
            1,
        )
        assert self.gregorian_cd._overflow_month(leap_year, 13, True) == (
            leap_year + 1,
            1,
        )

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test__overflow_month_moving_backward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.gregorian_cd._overflow_month(year, month) == (year, month)
        assert self.gregorian_cd._overflow_month(common_year, 0, False) == (
            common_year - 1,
            12,
        )
        assert self.gregorian_cd._overflow_month(leap_year, 0, False) == (
            leap_year - 1,
            12,
        )

    # test ConvertibleDate._get_delta() in test_customdate.py

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
    # ConvertibleDate.era
    #
    def test_era(self):
        bce_year = self.random_bce_year()
        ce_year = self.random_ce_year()
        assert self.gregorian_cd.era(bce_year) == "BCE"
        assert self.gregorian_cd.era(ce_year) == "CE"

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        # all_cycle_ordinals reverses to early when patched...so don't patch
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
