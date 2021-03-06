import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
from collections import deque
from src.customdate import DateUnit
from unittest.mock import patch


class CopticTest(RealCalendarTestCase):
    """
    Can the database represent the Coptic Calendar?
    Year are astronomical unless labeled otherwise
    """

    #
    # Helper functions
    #
    def setUp(self):
        super(CopticTest, self).setUp()
        self.main_calendar = self.coptic
        self.to_gregorian_ymd = convertdate.coptic.to_gregorian
        self.common_ordinals = (2, 3, 1)
        self.cycle_length = 4
        self.all_cycle_ordinals = deque([2, 3, 4, 1])
        self.leap_years_in_normal_cycle = 1
        self.common_years_in_normal_cycle = 3
        self.days_in_leap_years = 366
        self.days_in_common_year = 365

    @staticmethod
    def random_common_year() -> int:
        year = FAKE.random_int(min=-9999) * 4
        assert convertdate.coptic.is_leap(year) is False
        return year

    @staticmethod
    def random_leap_year() -> int:
        year = (FAKE.random_int(min=-9999) * 4) - 1
        assert convertdate.coptic.is_leap(year)
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
    # ConvertibleDate.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.coptic_cd.convert_ast_ymd((1, 1, 1), self.l_hijri_cd)
            == (338, 11, 22)
        )
        assert (
            self.coptic_cd.convert_ast_ymd((-348, 9, 29), self.l_hijri_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cd.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cd)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert(
            self.coptic_cd.convert_ast_ymd((1, 1, 1), self.indian_cd)
            == (-206, 7, 28)
        )
        assert (
            self.coptic_cd.convert_ast_ymd((207, 6, 7), self.indian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cd.convert_ast_ymd(indian_ymd, self.indian_cd)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.coptic_cd.convert_ast_ymd((1, 1, 1), self.gregorian_cd)
            == (-283, 5, 8)
        )
        assert (
            self.coptic_cd.convert_ast_ymd((284, 8, 29), self.gregorian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cd.convert_ast_ymd(gregorian_ymd, self.gregorian_cd)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        coptic_ymd = convertdate.coptic.from_gregorian(gyear, gmonth, gday)
        # fmt: off
        assert (
            self.coptic_cd.convert_ast_ymd((1, 1, 1), self.julian_cd)
            == (-283, 5, 6)
        )
        assert (
            self.coptic_cd.convert_ast_ymd((284, 8, 29), self.julian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cd.convert_ast_ymd(julian_ymd, self.julian_cd)
            == coptic_ymd
        )

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
    def test_ordinal_date_to_ordinal_for_bc_year(self, *_):
        # patching reverses all_cycle_ordinals for some reason...so don't patch
        assert self.coptic_cd.ordinal_date_to_ordinal((0, 365)) == 0
        assert self.coptic_cd.ordinal_date_to_ordinal((0, 1)) == -364
        assert self.coptic_cd.ordinal_date_to_ordinal((-1, 366)) == -365
        assert self.coptic_cd.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.coptic_cd.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.coptic_cd.ordinal_date_to_ordinal((-2, 300)) == -796
        assert self.coptic_cd.ordinal_date_to_ordinal((-2, 1)) == -1095
        assert self.coptic_cd.ordinal_date_to_ordinal((-3, 365)) == -1096
        assert self.coptic_cd.ordinal_date_to_ordinal((-3, 1)) == -1460
        assert self.coptic_cd.ordinal_date_to_ordinal((-4, 365)) == -1461
        assert self.coptic_cd.ordinal_date_to_ordinal((-4, 82)) == -1744

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
    def test_ordinal_date_to_ordinal_for_am_year(self, *_):
        # patching reverses all_cycle_ordinals for some reason...so don't patch
        assert self.coptic_cd.ordinal_date_to_ordinal((5, 225)) == 1686
        assert self.coptic_cd.ordinal_date_to_ordinal((5, 1)) == 1462
        assert self.coptic_cd.ordinal_date_to_ordinal((4, 365)) == 1461
        assert self.coptic_cd.ordinal_date_to_ordinal((4, 187)) == 1283
        assert self.coptic_cd.ordinal_date_to_ordinal((4, 1)) == 1097
        assert self.coptic_cd.ordinal_date_to_ordinal((3, 366)) == 1096
        assert self.coptic_cd.ordinal_date_to_ordinal((3, 1)) == 731
        assert self.coptic_cd.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.coptic_cd.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.coptic_cd.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.coptic_cd.ordinal_date_to_ordinal((1, 1)) == 1

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        year, month, day = self.random_common_ymd()
        year, month, day = convertdate.coptic.to_gregorian(year, month, day)
        day_of_year = self.coptic_dc.from_gregorian(year, month, day)
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
    def test_ordinal_to_ordinal_date_for_am_year(self, *_):
        assert self.coptic_cd.ordinal_to_ordinal_date(1569) == (5, 108)
        assert self.coptic_cd.ordinal_to_ordinal_date(1462) == (5, 1)
        assert self.coptic_cd.ordinal_to_ordinal_date(1461) == (4, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(1097) == (4, 1)
        assert self.coptic_cd.ordinal_to_ordinal_date(829) == (3, 99)
        assert self.coptic_cd.ordinal_to_ordinal_date(731) == (3, 1)
        assert self.coptic_cd.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.coptic_cd.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_bc_year(self, *_):
        assert self.coptic_cd.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(-365) == (-1, 366)
        assert self.coptic_cd.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(-791) == (-2, 305)
        assert self.coptic_cd.ordinal_to_ordinal_date(-1096) == (-3, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(-1461) == (-4, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(-1826) == (-5, 366)
        assert self.coptic_cd.ordinal_to_ordinal_date(-1896) == (-5, 296)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.coptic_cd.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.coptic_cd.ordinal_to_ordinal_date(-90) == (0, 275)
        assert self.coptic_cd.ordinal_to_ordinal_date(-170) == (0, 195)
        assert self.coptic_cd.ordinal_to_ordinal_date(-266) == (0, 99)
        assert self.coptic_cd.ordinal_to_ordinal_date(-364) == (0, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_is_reversible_for_bce_year(self, *_):
        bce_ordinal = FAKE.random_int(min=-9999, max=0)
        bce_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=365),
        )
        assert (
            self.coptic_cd.ordinal_to_ordinal_date(
                self.coptic_cd.ordinal_date_to_ordinal(bce_ordinal_date)
            )
            == bce_ordinal_date
        )
        assert (
            self.coptic_cd.ordinal_date_to_ordinal(
                self.coptic_cd.ordinal_to_ordinal_date(bce_ordinal)
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
    def test_ordinal_to_ordinal_date_is_reversible_for_am_year(self, *_):
        am_ordinal = FAKE.random_int()
        am_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=365)
        assert (
            self.coptic_cd.ordinal_to_ordinal_date(
                self.coptic_cd.ordinal_date_to_ordinal(am_ordinal_date)
            )
            == am_ordinal_date
        )
        assert (
            self.coptic_cd.ordinal_date_to_ordinal(
                self.coptic_cd.ordinal_to_ordinal_date(am_ordinal)
            )
            == am_ordinal
        )

    #
    # Cycle methods
    #
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_completed_cycles_for_am_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(completed_cycles)
        end_year = self.make_cycle_end_year(completed_cycles)
        cycle_year = FAKE.random_int(min=start_year, max=end_year)
        assert self.coptic_cd.completed_cycles(1) == 0
        assert self.coptic_cd.completed_cycles(4) == 0
        assert self.coptic_cd.completed_cycles(5) == 1
        assert self.coptic_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_completed_cycles_for_bc_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        end_year = self.make_cycle_end_year(completed_cycles, proleptic=True)
        cycle_year = FAKE.random_int(min=end_year, max=start_year)
        assert self.coptic_cd.completed_cycles(0) == 0
        assert self.coptic_cd.completed_cycles(-3) == 0
        assert self.coptic_cd.completed_cycles(-4) == 1
        assert self.coptic_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_cycle_index_for_am_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        am_start_year = self.make_cycle_start_year(completed_cycles)
        am_year = am_start_year + cycle_index
        assert self.coptic_cd.cycle_index(1) == 0
        assert self.coptic_cd.cycle_index(2) == 1
        assert self.coptic_cd.cycle_index(3) == 2
        assert self.coptic_cd.cycle_index(4) == 3
        assert self.coptic_cd.cycle_index(5) == 0
        assert (
            self.coptic_cd.cycle_index(am_year, completed_cycles, 1, 1)
            == cycle_index
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_cycle_index_for_bc_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        bc_start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        bc_year = bc_start_year - cycle_index
        assert self.coptic_cd.cycle_index(-4) == 0
        assert self.coptic_cd.cycle_index(-3) == 3
        assert self.coptic_cd.cycle_index(-2) == 2
        assert self.coptic_cd.cycle_index(-1) == 1
        assert self.coptic_cd.cycle_index(0) == 0
        assert (
            self.coptic_cd.cycle_index(bc_year, completed_cycles, 0, -1)
            == cycle_index
        )

    def test_all_cycle_ordinals(self):
        assert self.coptic_cd.all_cycle_ordinals == self.all_cycle_ordinals
        with pytest.raises(AttributeError):
            self.coptic_cd.all_cycle_ordinals = FAKE.pylist()

    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    def test_days_in_normal_cycle(self, p_common_years_in_normal_cycle):
        cyinc = self.common_years_in_normal_cycle
        p_common_years_in_normal_cycle.__get__ = lambda *_: cyinc

        days_in_normal_cycle = self.coptic_dc.from_gregorian(
            *convertdate.coptic.to_gregorian(5, 1, 1)
        )
        assert self.coptic_cd.days_in_normal_cycle == days_in_normal_cycle
        with pytest.raises(AttributeError):
            self.coptic_cd.days_in_normal_cycle = FAKE.random_int()

    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    def test_common_year_cycle_ordinals(self, patch_all_cycle_ordinals):
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ords = tuple(self.common_ordinals)
        assert self.coptic_cd.common_year_cycle_ordinals == common_ords
        with pytest.raises(AttributeError):
            self.coptic_cd.common_year_cycle_ordinals = FAKE.pytuple()

    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    def test_common_years_in_normal_cycle(self, p_common_year_cycle_ordinals):
        p_common_year_cycle_ordinals.__get__ = lambda *_: self.common_ordinals
        cyinc = self.common_years_in_normal_cycle
        assert self.coptic_cd.common_years_in_normal_cycle == cyinc
        with pytest.raises(AttributeError):
            self.coptic_cd.common_years_in_normal_cycle = FAKE.random_int()

    def test_special_years(self):
        ast_year = FAKE.random_int(min=-9999)
        assert self.coptic_cd.net_elapsed_special_years(ast_year) == (0, 0)

    #
    # ConvertibleDate.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        coptic_cdt = self.coptic_cd
        assert coptic_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((1000, 13, 5)) == (1000, 365)
        assert coptic_cdt.ast_ymd_to_ordinal_date((40, 8, 18)) == (40, 228)
        assert coptic_cdt.ast_ymd_to_ordinal_date((0, 13, 5)) == (0, 365)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-120, 1, 1)) == (-120, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-200, 3, 29)) == (-200, 89)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        coptic_cdt = self.coptic_cd
        assert coptic_cdt.ast_ymd_to_ordinal_date((3, 1, 1)) == (3, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((15, 3, 30)) == (15, 90)
        assert coptic_cdt.ast_ymd_to_ordinal_date((39, 11, 13)) == (39, 313)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-1, 13, 6)) == (-1, 366)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-13, 1, 1)) == (-13, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-101, 5, 22)) == (-101, 142)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.coptic_cd.ast_ymd_to_ordinal_date(self.random_ymd())

    #
    # ConvertibleDate.ordinal_date_to_ast_ymd
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        coptic_cdt = self.coptic_cd
        assert coptic_cdt.ordinal_date_to_ast_ymd((4, 1)) == (4, 1, 1)
        assert coptic_cdt.ordinal_date_to_ast_ymd((20, 270)) == (20, 9, 30)
        assert coptic_cdt.ordinal_date_to_ast_ymd((400, 43)) == (400, 2, 13)
        assert coptic_cdt.ordinal_date_to_ast_ymd((0, 365)) == (0, 13, 5)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-44, 299)) == (-44, 10, 29)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-80, 115)) == (-80, 4, 25)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        coptic_cdt = self.coptic_cd
        assert coptic_cdt.ordinal_date_to_ast_ymd((3, 1)) == (3, 1, 1)
        assert coptic_cdt.ordinal_date_to_ast_ymd((27, 75)) == (27, 3, 15)
        assert coptic_cdt.ordinal_date_to_ast_ymd((2019, 366)) == (2019, 13, 6)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-1, 366)) == (-1, 13, 6)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-5, 147)) == (-5, 5, 27)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-21, 300)) == (-21, 10, 30)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = common_year, FAKE.random_int(min=1, max=365)
        ast_ymd = common_year, month, day
        assert (
            self.coptic_cd.ordinal_date_to_ast_ymd(
                self.coptic_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.coptic_cd.ast_ymd_to_ordinal_date(
                self.coptic_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = leap_year, FAKE.random_int(min=1, max=366)
        ast_ymd = leap_year, month, day
        assert (
            self.coptic_cd.ordinal_date_to_ast_ymd(
                self.coptic_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.coptic_cd.ast_ymd_to_ordinal_date(
                self.coptic_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.coptic_cd.ordinal_date_to_ast_ymd((1, 1))

    #
    # Shift year, month, day
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    def test_shift_ast_ymd_by_multiple_intervals(self, _):
        plus_delta = FAKE.random_int(min=1, max=12)
        plus_years = [[plus_delta, DateUnit.YEAR]]
        plus_months = [[plus_delta, DateUnit.MONTH]]
        ymd = self.random_ymd()
        ast_year, _, _ = ymd
        assert self.coptic_cd.shift_ast_ymd(ymd, [[0, DateUnit.YEAR]]) == ymd
        # fmt: off
        assert self.coptic_cd.shift_ast_ymd(
            (ast_year, 6, 27), plus_years
        ) == (ast_year + plus_delta, 6, 27)
        assert self.coptic_cd.shift_ast_ymd(
            (ast_year, 1, 5), plus_months
        ) == (ast_year, 1 + plus_delta, 5)
        # fmt: on
        assert self.coptic_cd.shift_ast_ymd(
            (ast_year, 3, 15), [[2, DateUnit.YEAR], [4, DateUnit.MONTH]]
        ) == (ast_year + 2, 7, 15)
        assert self.coptic_cd.shift_ast_ymd(
            (ast_year, 9, 25), [[3, DateUnit.YEAR], [-2, DateUnit.MONTH]]
        ) == (ast_year + 3, 7, 25)

    def test_shift_ast_ymd_to_invalid_day(self):
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.coptic_cd.shift_ast_ymd(
            (common_year, 12, 30), [[1, DateUnit.MONTH]]
        ) == (common_year, 13, 5)
        assert self.coptic_cd.shift_ast_ymd(
            (leap_year, 12, 30), [[1, DateUnit.MONTH]]
        ) == (leap_year, 13, 6)
        assert self.coptic_cd.shift_ast_ymd(
            (2, 1, 6), [[-1, DateUnit.MONTH]]
        ) == (1, 13, 5)
        assert self.coptic_cd.shift_ast_ymd(
            (4, 1, 7), [[-1, DateUnit.MONTH]]
        ) == (3, 13, 6)

    def test_shift_ast_year(self):
        delta = FAKE.random_int()
        year = self.random_year()
        expected_year = year + delta
        assert self.coptic_cd.shift_ast_year(year, delta) == expected_year

    def test_shift_month(self):
        year, month, _ = self.random_ymd()
        assert self.coptic_cd.shift_month(year, month, -26) == (
            year - 2,
            month,
        )
        assert self.coptic_cd.shift_month(year, month, -13) == (
            year - 1,
            month,
        )
        assert self.coptic_cd.shift_month(year, month, 0) == (year, month)
        assert self.coptic_cd.shift_month(year, month, 13) == (year + 1, month)
        assert self.coptic_cd.shift_month(year, month, 26) == (year + 2, month)
        assert self.coptic_cd.shift_month(year, 2, 3) == (year, 5)
        assert self.coptic_cd.shift_month(year, 13, 1) == (year + 1, 1)
        assert self.coptic_cd.shift_month(year, 8, 7) == (year + 1, 2)
        assert self.coptic_cd.shift_month(year, 3, 14) == (year + 1, 4)
        assert self.coptic_cd.shift_month(year, 6, 29) == (year + 2, 9)
        assert self.coptic_cd.shift_month(year, 10, -1) == (year, 9)
        assert self.coptic_cd.shift_month(year, 1, -1) == (year - 1, 13)
        assert self.coptic_cd.shift_month(year, 2, -3) == (year - 1, 12)
        assert self.coptic_cd.shift_month(year, 5, -7) == (year - 1, 11)
        assert self.coptic_cd.shift_month(year, 7, -15) == (year - 1, 5)
        assert self.coptic_cd.shift_month(year, 12, -28) == (year - 2, 10)

    #
    # Next DateUnit
    #

    # ConvertibleDate.next_ast_ymd tested in test_customdate
    # ConvertibleDate.next_era tested in test_customdate
    # ConvertibleDate.next_ast_year tested in test_customdate

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_month_moving_forward(self, _):
        assert self.coptic_cd.next_month(1000, 5, 2, True) == (1000, 6, 1)
        assert self.coptic_cd.next_month(231, 1, 3, True) == (231, 3, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_month_moving_backward(self, _):
        assert self.coptic_cd.next_month(124, 7, 3, False) == (124, 6, 1)
        assert self.coptic_cd.next_month(435, 11, 4, False) == (435, 8, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_day_moving_forward(self, _):
        assert self.coptic_cd.next_day((123, 9, 15), 5, True) == (123, 9, 20)
        assert self.coptic_cd.next_day((332, 4, 13), 3, True) == (332, 4, 15)
        assert self.coptic_cd.next_day((100, 13, 5), 5, True) == (101, 1, 5)
        assert self.coptic_cd.next_day((99, 13, 4), 2, True) == (99, 13, 6)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_day_moving_backward(self, _):
        assert self.coptic_cd.next_day((243, 3, 2), 2, False) == (243, 2, 30)
        assert self.coptic_cd.next_day((384, 10, 10), 4, False) == (384, 10, 8)
        assert self.coptic_cd.next_day((12, 1, 1), 3, False) == (11, 13, 6)
        assert self.coptic_cd.next_day((15, 1, 4), 5, False) == (14, 13, 5)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test__overflow_month_moving_forward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.coptic_cd._overflow_month(year, month) == (year, month)
        assert self.coptic_cd._overflow_month(common_year, 14, True) == (
            common_year + 1,
            1,
        )
        assert self.coptic_cd._overflow_month(leap_year, 14, True) == (
            leap_year + 1,
            1,
        )

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test__overflow_month_moving_backward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.coptic_cd._overflow_month(year, month) == (year, month)
        assert self.coptic_cd._overflow_month(common_year, 0, False) == (
            common_year - 1,
            13,
        )
        assert self.coptic_cd._overflow_month(leap_year, 0, False) == (
            leap_year - 1,
            13,
        )

    # test ConvertibleDate._get_delta() in test_customdate.py

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        bc_ast_year = self.random_bce_year()
        bc_hr_year = abs(bc_ast_year - 1)
        am_ast_year = am_hr_year = self.random_ce_year()
        assert self.coptic_cd.hr_to_ast(1, 1) == 1
        assert self.coptic_cd.hr_to_ast(1, 0) == 0
        assert self.coptic_cd.hr_to_ast(2, 0) == -1
        assert self.coptic_cd.hr_to_ast(bc_hr_year, 0) == bc_ast_year
        assert self.coptic_cd.hr_to_ast(am_hr_year, 1) == am_ast_year

    def test_ast_to_hr(self):
        bc_ast_year = self.random_bce_year()
        bc_hr_year = abs(bc_ast_year - 1)
        am_ast_year = am_hr_year = self.random_ce_year()
        assert self.coptic_cd.ast_to_hr(1) == (1, 1)
        assert self.coptic_cd.ast_to_hr(0) == (1, 0)
        assert self.coptic_cd.ast_to_hr(-1) == (2, 0)
        assert self.coptic_cd.ast_to_hr(bc_ast_year) == (bc_hr_year, 0)
        assert self.coptic_cd.ast_to_hr(am_ast_year) == (am_hr_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_am_year = self.random_ce_year()
        hr_am_year = ast_am_year
        assert (
            self.coptic_cd.hr_to_ast(*self.coptic_cd.ast_to_hr(ast_bce_year))
            == ast_bce_year
        )
        assert (
            self.coptic_cd.hr_to_ast(*self.coptic_cd.ast_to_hr(ast_am_year))
            == ast_am_year
        )
        assert self.coptic_cd.ast_to_hr(
            self.coptic_cd.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.coptic_cd.ast_to_hr(
            self.coptic_cd.hr_to_ast(hr_am_year, 1)
        ) == (hr_am_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ah_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.coptic_cd.ast_to_hr(ast_ah_year)

    def test_parse_hr_date(self):
        am_ymd = self.random_ce_ymd()
        am_ast_year, am_month, am_day = am_ymd
        am_hr_year = am_ast_year
        am_hr_date = self.coptic_cd.date_sep.join(
            [str(am_hr_year), str(am_month), str(am_day), "AM"]
        )

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.coptic_cd.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.coptic_cd.parse_hr_date(am_hr_date) == am_ymd
        assert self.coptic_cd.parse_hr_date(bc_hr_date) == bc_ymd

    def test_format_hr_date(self):
        am_ymd = self.random_ce_ymd()
        am_ast_year, am_month, am_day = am_ymd
        am_hr_year = am_ast_year
        am_hr_date = self.coptic_cd.date_sep.join(
            [str(am_hr_year), str(am_month), str(am_day), "AM"]
        )

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.coptic_cd.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.coptic_cd.format_hr_date(bc_ymd) == bc_hr_date
        assert self.coptic_cd.format_hr_date(am_ymd) == am_hr_date

    #
    # ConvertibleDate.era
    #
    def test_era(self):
        bc_year = self.random_bce_year()
        am_year = self.random_ce_year()
        assert self.coptic_cd.era(bc_year) == "BC"
        assert self.coptic_cd.era(am_year) == "AM"

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        # all_cycle_ordinals reverses to early when patched...so don't patch
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.coptic_cd.is_leap_year(1) is False
        assert self.coptic_cd.is_leap_year(8) is False
        assert self.coptic_cd.is_leap_year(common_bce_year) is False
        assert self.coptic_cd.is_leap_year(common_ce_year) is False
        assert self.coptic_cd.is_leap_year(3) is True
        assert self.coptic_cd.is_leap_year(7) is True
        assert self.coptic_cd.is_leap_year(leap_bce_year) is True
        assert self.coptic_cd.is_leap_year(leap_ce_year) is True

    #
    # ConvertibleDate.is_valid_ast_ymd
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.coptic_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.coptic_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=14)
        bad_day = FAKE.random_int(min=31)
        assert not self.coptic_cd.is_valid_ast_ymd((year, bad_month, day))
        assert not self.coptic_cd.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDate.is_valid_month
    #
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=13)
    def test_is_valid_month(self, _):
        year, month, _ = self.random_ymd()
        negative_month = FAKE.random_int(min=-9999, max=-1)
        too_big_month = FAKE.random_int(min=14)
        assert self.coptic_cd.is_valid_month(year, month)
        assert self.coptic_cd.is_valid_month(year, negative_month) is False
        assert self.coptic_cd.is_valid_month(year, too_big_month) is False

    #
    # ConvertibleDate.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        coptic_cdt = self.coptic_cd
        assert not coptic_cdt.is_valid_ordinal_date((1, 366))
        assert coptic_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not coptic_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        coptic_cdt = self.coptic_cd
        assert not coptic_cdt.is_valid_ordinal_date((1, 367))
        assert coptic_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not coptic_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDate.gen_years_before_era, not applicable

    #
    # ConvertibleDate.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.coptic_cd.days_in_months(common_year)
            # fmt: off
            == [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.coptic_cd.days_in_months(leap_year)
            # fmt: off
            == [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6]
            # fmt: on
        )

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_days_in_month_for_common_month(self, _):
        common_year, month, _ = self.random_common_ymd()
        assert self.coptic_cd.days_in_month(
            common_year, month
        ) == convertdate.coptic.month_length(common_year, month)

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_days_in_month_for_leap_month(self, _):
        leap_year, month, _ = self.random_leap_ymd()
        assert self.coptic_cd.days_in_month(
            leap_year, month
        ) == convertdate.coptic.month_length(leap_year, month)

    #
    # ConvertibleDate.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.coptic_cd.days_in_year(common_year) == 365

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.coptic_cd.days_in_year(leap_year) == 366

    #
    # ConvertibleDate.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.coptic_cd.months_in_year(common_year) == 13

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.coptic_cd.months_in_year(leap_year) == 13

    #
    # Weeks
    #
    @patch("src.db.ConvertibleCalendar.days_in_weeks", return_value=7)
    def test_day_of_week(self, _):
        bc_year, bc_month, bc_day = self.random_bce_ymd()
        bc_julian_day = convertdate.coptic.to_jd(bc_year, bc_month, bc_day)
        bc_ordinal = self.coptic_dc.from_jd(bc_julian_day) + 1

        am_year, am_month, am_day = self.random_ce_ymd()
        am_julian_day = convertdate.coptic.to_jd(am_year, am_month, am_day)
        am_ordinal = self.coptic_dc.from_jd(am_julian_day) + 1
        assert self.coptic_cd.day_of_week(1) == 5  # 1/1/1 is the sixth day
        assert self.coptic_cd.day_of_week(2) == 6
        assert self.coptic_cd.day_of_week(3) == 0
        assert self.coptic_cd.day_of_week(4) == 1
        assert self.coptic_cd.day_of_week(5) == 2
        assert self.coptic_cd.day_of_week(6) == 3
        assert self.coptic_cd.day_of_week(7) == 4
        assert self.coptic_cd.day_of_week(8) == 5
        assert (
            self.coptic_cd.day_of_week(bc_ordinal)
            == (convertdate.utils.jwday(bc_julian_day) + 1) % 7
        )
        assert (
            self.coptic_cd.day_of_week(am_ordinal)
            == (convertdate.utils.jwday(am_julian_day) + 1) % 7
        )
