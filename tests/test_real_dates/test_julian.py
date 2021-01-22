import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
from collections import deque
from unittest.mock import patch


class JulianTest(RealCalendarTestCase):
    """
    Can the database represent the Julian Calendar? (Proleptic before 4CE)
    Years are astronomical unless labeled otherwise
    """

    def setUp(self):
        super(JulianTest, self).setUp()
        self.main_calendar = self.julian
        self.to_gregorian_ymd = convertdate.julian.to_gregorian
        self.common_ordinals = (1, 2, 3)
        self.cycle_length = 4
        self.all_cycle_ordinals = deque([1, 2, 3, 4])
        self.leap_years_in_normal_cycle = 1
        self.common_years_in_normal_cycle = 3
        self.days_in_leap_years = 366
        self.days_in_common_year = 365

    @staticmethod
    def random_common_year() -> int:
        # don't check with convertdate, it's leap method is wrong
        return (FAKE.random_int(min=-9999) * 4) - 1

    @staticmethod
    def random_leap_year() -> int:
        # don't check with convertdate, it's leap method is wrong
        return FAKE.random_int(min=-9999) * 4

    @staticmethod
    def ordinal_conversion_patches(*args):
        patch_days_common_year = args[0]
        patch_days_in_leap_year = args[1]
        patch_common_years_in_normal_cycle = args[2]
        patch_leap_years_in_normal_cycle = args[3]
        patch_common_year_cycle_ordinals = args[4]
        patch_all_cycle_ordinals = args[5]
        patch_leap_year_cycle_length = args[6]

        patch_leap_year_cycle_length.__get__ = lambda *_: 4
        patch_all_cycle_ordinals.__get__ = lambda *_: deque([1, 2, 3, 4])
        patch_common_year_cycle_ordinals.__get__ = lambda *_: (1, 2, 3)
        patch_leap_years_in_normal_cycle.__get__ = lambda *_: 1
        patch_common_years_in_normal_cycle.__get__ = lambda *_: 3
        patch_days_in_leap_year.__get__ = lambda *_: 366
        patch_days_common_year.__get__ = lambda *_: 365

    #
    # ConvertibleDate.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cd.convert_ast_ymd((1, 1, 1), self.coptic_cd)
            == (284, 8, 29)
        )
        assert (
            self.julian_cd.convert_ast_ymd((-283, 5, 6), self.coptic_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cd.convert_ast_ymd(coptic_ymd, self.coptic_cd)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cd.convert_ast_ymd((1, 1, 1), self.indian_cd)
            == (78, 3, 24)
        )
        assert (
            self.julian_cd.convert_ast_ymd((-77, 10, 9), self.indian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cd.convert_ast_ymd(indian_ymd, self.indian_cd)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cd.convert_ast_ymd((1, 1, 1), self.gregorian_cd)
            == (1, 1, 3)
        )
        assert (
            self.julian_cd.convert_ast_ymd((0, 12, 30), self.gregorian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cd.convert_ast_ymd(gregorian_ymd, self.gregorian_cd)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        l_hijri_ymd = convertdate.islamic.from_gregorian(gyear, gmonth, gday)
        # fmt: off
        assert (
            self.julian_cd.convert_ast_ymd((1, 1, 1), self.l_hijri_cd)
            == (622, 7, 16)
        )
        assert (
            self.julian_cd.convert_ast_ymd((-640, 5, 16), self.l_hijri_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cd.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cd)
            == julian_ymd
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
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_for_ad_year(self, *_):
        assert self.julian_cd.ordinal_to_ordinal_date(1662) == (5, 201)
        assert self.julian_cd.ordinal_to_ordinal_date(1462) == (5, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(1461) == (4, 366)
        assert self.julian_cd.ordinal_to_ordinal_date(1096) == (4, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(1095) == (3, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(791) == (3, 61)
        assert self.julian_cd.ordinal_to_ordinal_date(730) == (2, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_bc_year(self, *_):
        assert self.julian_cd.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.julian_cd.ordinal_to_ordinal_date(-365) == (0, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(-366) == (-1, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(-466) == (-1, 265)
        assert self.julian_cd.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(-1095) == (-2, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(-1096) == (-3, 365)
        assert self.julian_cd.ordinal_to_ordinal_date(-1460) == (-3, 1)
        assert self.julian_cd.ordinal_to_ordinal_date(-1461) == (-4, 366)
        assert self.julian_cd.ordinal_to_ordinal_date(-1791) == (-4, 36)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.julian_cd.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.julian_cd.ordinal_to_ordinal_date(-100) == (0, 266)
        assert self.julian_cd.ordinal_to_ordinal_date(-200) == (0, 166)
        assert self.julian_cd.ordinal_to_ordinal_date(-300) == (0, 66)
        assert self.julian_cd.ordinal_to_ordinal_date(-365) == (0, 1)

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
        "src.customdate.ConvertibleDate.net_special_years",
        return_value=[0, 0],
    )
    @patch("src.db.ConvertibleCalendar.leap_year_cycle_length")
    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    @patch("src.db.ConvertibleCalendar.leap_years_in_normal_cycle")
    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    @patch("src.db.ConvertibleCalendar.days_in_leap_year")
    @patch("src.db.ConvertibleCalendar.days_in_common_year")
    def test_ordinal_date_to_ordinal_for_bc_year(self, *args):
        self.ordinal_conversion_patches(*args)

        assert self.julian_cd.ordinal_date_to_ordinal((0, 366)) == 0
        assert self.julian_cd.ordinal_date_to_ordinal((0, 1)) == -365
        assert self.julian_cd.ordinal_date_to_ordinal((-1, 365)) == -366
        assert self.julian_cd.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.julian_cd.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.julian_cd.ordinal_date_to_ordinal((-2, 165)) == -931
        assert self.julian_cd.ordinal_date_to_ordinal((-2, 1)) == -1095
        assert self.julian_cd.ordinal_date_to_ordinal((-3, 365)) == -1096
        assert self.julian_cd.ordinal_date_to_ordinal((-3, 1)) == -1460
        assert self.julian_cd.ordinal_date_to_ordinal((-4, 366)) == -1461
        assert self.julian_cd.ordinal_date_to_ordinal((-4, 145)) == -1682

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
        "src.customdate.ConvertibleDate.net_special_years",
        return_value=[0, 0],
    )
    @patch("src.db.ConvertibleCalendar.leap_year_cycle_length")
    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    @patch("src.db.ConvertibleCalendar.leap_years_in_normal_cycle")
    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    @patch("src.db.ConvertibleCalendar.days_in_leap_year")
    @patch("src.db.ConvertibleCalendar.days_in_common_year")
    def test_ordinal_date_to_ordinal_for_ad_year(self, *args):
        self.ordinal_conversion_patches(*args)

        assert self.julian_cd.ordinal_date_to_ordinal((1, 1)) == 1
        assert self.julian_cd.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.julian_cd.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.julian_cd.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.julian_cd.ordinal_date_to_ordinal((3, 1)) == 731
        assert self.julian_cd.ordinal_date_to_ordinal((3, 102)) == 832
        assert self.julian_cd.ordinal_date_to_ordinal((3, 365)) == 1095
        assert self.julian_cd.ordinal_date_to_ordinal((4, 1)) == 1096
        assert self.julian_cd.ordinal_date_to_ordinal((4, 366)) == 1461
        assert self.julian_cd.ordinal_date_to_ordinal((5, 1)) == 1462
        assert self.julian_cd.ordinal_date_to_ordinal((5, 99)) == 1560

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
    def test_ordinal_date_to_ordinal_is_reversible_for_bc_year(self, *_):
        bc_ordinal = FAKE.random_int(min=-9999, max=0)
        bc_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=365),
        )
        assert (
            self.julian_cd.ordinal_to_ordinal_date(
                self.julian_cd.ordinal_date_to_ordinal(bc_ordinal_date)
            )
            == bc_ordinal_date
        )
        assert (
            self.julian_cd.ordinal_date_to_ordinal(
                self.julian_cd.ordinal_to_ordinal_date(bc_ordinal)
            )
            == bc_ordinal
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
    def test_ordinal_date_to_ordinal_is_reversible_for_ad_year(self, *_):
        ad_ordinal = FAKE.random_int()
        ad_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=365)
        assert (
            self.julian_cd.ordinal_to_ordinal_date(
                self.julian_cd.ordinal_date_to_ordinal(ad_ordinal_date)
            )
            == ad_ordinal_date
        )
        assert (
            self.julian_cd.ordinal_date_to_ordinal(
                self.julian_cd.ordinal_to_ordinal_date(ad_ordinal)
            )
            == ad_ordinal
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        with pytest.raises(ValueError):
            self.julian_cd.ordinal_date_to_ordinal((1, 0))

    def test_all_cycle_ordinals(self):
        assert self.julian_cd.all_cycle_ordinals == self.all_cycle_ordinals
        with pytest.raises(AttributeError):
            self.julian_cd.all_cycle_ordinals = FAKE.pylist()

    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    def test_days_in_normal_cycle(self, p_common_years_in_normal_cycle):
        cyinc = self.common_years_in_normal_cycle
        p_common_years_in_normal_cycle.__get__ = lambda *_: cyinc

        days_in_normal_cycle = self.julian_dc.from_gregorian(
            *convertdate.julian.to_gregorian(5, 1, 1)
        )
        assert self.julian_cd.days_in_normal_cycle == days_in_normal_cycle
        with pytest.raises(AttributeError):
            self.julian_cd.days_in_normal_cycle = FAKE.random_int()

    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    def test_common_year_cycle_ordinals(self, patch_all_cycle_ordinals):
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ords = tuple(self.common_ordinals)
        assert self.julian_cd.common_year_cycle_ordinals == common_ords
        with pytest.raises(AttributeError):
            self.julian_cd.common_year_cycle_ordinals = FAKE.pytuple()

    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    def test_common_years_in_normal_cycle(self, p_common_year_cycle_ordinals):
        p_common_year_cycle_ordinals.__get__ = lambda *_: self.common_ordinals
        cyinc = self.common_years_in_normal_cycle
        assert self.julian_cd.common_years_in_normal_cycle == cyinc
        with pytest.raises(AttributeError):
            self.julian_cd.common_years_in_normal_cycle = FAKE.random_int()

    def test_special_years(self):
        assert self.julian_cd.net_special_years(FAKE.random_int()) == (0, 0)

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
        julian_cdt = self.julian_cd
        assert julian_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert julian_cdt.ast_ymd_to_ordinal_date((5, 12, 31)) == (5, 365)
        assert julian_cdt.ast_ymd_to_ordinal_date((69, 7, 19)) == (69, 200)
        assert julian_cdt.ast_ymd_to_ordinal_date((-1, 12, 31)) == (-1, 365)
        assert julian_cdt.ast_ymd_to_ordinal_date((-17, 1, 1)) == (-17, 1)
        assert julian_cdt.ast_ymd_to_ordinal_date((-39, 10, 30)) == (-39, 303)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        julian_cdt = self.julian_cd
        assert julian_cdt.ast_ymd_to_ordinal_date((4, 1, 1)) == (4, 1)
        assert julian_cdt.ast_ymd_to_ordinal_date((80, 12, 31)) == (80, 366)
        assert julian_cdt.ast_ymd_to_ordinal_date((400, 8, 10)) == (400, 223)
        assert julian_cdt.ast_ymd_to_ordinal_date((0, 12, 31)) == (0, 366)
        assert julian_cdt.ast_ymd_to_ordinal_date((-8, 1, 1)) == (-8, 1)
        assert julian_cdt.ast_ymd_to_ordinal_date((-64, 4, 22)) == (-64, 113)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.julian_cd.ast_ymd_to_ordinal_date(self.random_ymd())

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
        julian_cdt = self.julian_cd
        assert julian_cdt.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert julian_cdt.ordinal_date_to_ast_ymd((5, 100)) == (5, 4, 10)
        assert julian_cdt.ordinal_date_to_ast_ymd((17, 365)) == (17, 12, 31)
        assert julian_cdt.ordinal_date_to_ast_ymd((-1, 365)) == (-1, 12, 31)
        assert julian_cdt.ordinal_date_to_ast_ymd((-19, 165)) == (-19, 6, 14)
        assert julian_cdt.ordinal_date_to_ast_ymd((-33, 1)) == (-33, 1, 1)

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
        julian_cdt = self.julian_cd
        assert julian_cdt.ordinal_date_to_ast_ymd((4, 1)) == (4, 1, 1)
        assert julian_cdt.ordinal_date_to_ast_ymd((8, 60)) == (8, 2, 29)
        assert julian_cdt.ordinal_date_to_ast_ymd((44, 366)) == (44, 12, 31)
        assert julian_cdt.ordinal_date_to_ast_ymd((0, 366)) == (0, 12, 31)
        assert julian_cdt.ordinal_date_to_ast_ymd((-8, 60)) == (-8, 2, 29)
        assert julian_cdt.ordinal_date_to_ast_ymd((-12, 1)) == (-12, 1, 1)

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
        ordinal_date = common_year, FAKE.random_int(min=1, max=365)
        ast_ymd = common_year, month, day
        assert (
            self.julian_cd.ordinal_date_to_ast_ymd(
                self.julian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.julian_cd.ast_ymd_to_ordinal_date(
                self.julian_cd.ordinal_date_to_ast_ymd(ordinal_date)
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
        ordinal_date = leap_year, FAKE.random_int(min=1, max=366)
        ast_ymd = leap_year, month, day
        assert (
            self.julian_cd.ordinal_date_to_ast_ymd(
                self.julian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.julian_cd.ast_ymd_to_ordinal_date(
                self.julian_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.julian_cd.ordinal_date_to_ast_ymd((1, 0))

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        ast_bc_year = self.random_bce_year()
        hr_bc_year = abs(ast_bc_year - 1)
        hr_ad_year = self.random_ce_year()
        assert self.julian_cd.hr_to_ast(1, 1) == 1
        assert self.julian_cd.hr_to_ast(1, 0) == 0
        assert self.julian_cd.hr_to_ast(2, 0) == -1
        assert self.julian_cd.hr_to_ast(hr_bc_year, 0) == ast_bc_year
        assert self.julian_cd.hr_to_ast(hr_ad_year, 1) == hr_ad_year

    def test_ast_to_hr(self):
        ast_bc_year = self.random_bce_year()
        hr_bc_year = abs(ast_bc_year - 1)
        ast_ad_year = self.random_ce_year()
        assert self.julian_cd.ast_to_hr(1) == (1, 1)
        assert self.julian_cd.ast_to_hr(0) == (1, 0)
        assert self.julian_cd.ast_to_hr(-1) == (2, 0)
        assert self.julian_cd.ast_to_hr(ast_bc_year) == (hr_bc_year, 0)
        assert self.julian_cd.ast_to_hr(ast_ad_year) == (ast_ad_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        hr_ce_year = ast_ce_year
        assert (
            self.julian_cd.hr_to_ast(*self.julian_cd.ast_to_hr(ast_bce_year))
            == ast_bce_year
        )
        assert (
            self.julian_cd.hr_to_ast(*self.julian_cd.ast_to_hr(ast_ce_year))
            == ast_ce_year
        )
        assert self.julian_cd.ast_to_hr(
            self.julian_cd.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.julian_cd.ast_to_hr(
            self.julian_cd.hr_to_ast(hr_ce_year, 1)
        ) == (hr_ce_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ad_ast_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.julian_cd.ast_to_hr(ad_ast_year)

    def test_parse_hr_date(self):
        ad_ymd = self.random_ce_ymd()
        ad_ast_year, ad_month, ad_day = ad_ymd
        ad_hr_year = ad_ast_year

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)

        ad_hr_date = self.julian_cd.date_sep.join(
            [str(ad_hr_year), str(ad_month), str(ad_day), "AD"]
        )
        bc_hr_date = self.julian_cd.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.julian_cd.parse_hr_date(ad_hr_date) == ad_ymd
        assert self.julian_cd.parse_hr_date(bc_hr_date) == bc_ymd

    def test_format_hr_date(self):
        bc_ast_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ast_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.julian_cd.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )

        ad_ast_ymd = self.random_ce_ymd()
        ad_ast_year, ad_month, ad_day = ad_ast_ymd
        ad_hr_date = self.julian_cd.date_sep.join(
            [str(ad_ast_year), str(ad_month), str(ad_day), "AD"]
        )
        assert self.julian_cd.format_hr_date(bc_ast_ymd) == bc_hr_date
        assert self.julian_cd.format_hr_date(ad_ast_ymd) == ad_hr_date

    #
    # Eras
    #
    def test_era(self):
        bc_year = self.random_bce_year()
        ad_year = self.random_ce_year()
        assert self.julian_cd.era(bc_year) == "BC"
        assert self.julian_cd.era(ad_year) == "AD"

    def test_is_descending_era(self):
        bc_year = self.random_bce_year()
        ad_year = self.random_ce_year()
        assert self.julian_cd.is_descending_era(bc_year)
        assert self.julian_cd.is_descending_era(ad_year) is False

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.julian_cd.is_leap_year(common_bce_year) is False
        assert self.julian_cd.is_leap_year(common_ce_year) is False
        assert self.julian_cd.is_leap_year(leap_bce_year)
        assert self.julian_cd.is_leap_year(leap_ce_year)

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
        year, month, day = self.random_common_ymd()
        assert self.julian_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.julian_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        assert not self.julian_cd.is_valid_ast_ymd((year, bad_month, day))
        assert not self.julian_cd.is_valid_ast_ymd((year, bad_month, bad_day))

    #
    # ConvertibleDate.is_valid_month
    #
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_month(self, _):
        year, month, _ = self.random_ymd()
        negative_month = FAKE.random_int(min=-9999, max=-1)
        too_big_month = FAKE.random_int(min=13)
        assert self.julian_cd.is_valid_month(year, month)
        assert self.julian_cd.is_valid_month(year, negative_month) is False
        assert self.julian_cd.is_valid_month(year, too_big_month) is False

    #
    # ConvertibleDate.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        julian_cdt = self.julian_cd
        assert not julian_cdt.is_valid_ordinal_date((1, 366))
        assert julian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not julian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        julian_cdt = self.julian_cd
        assert not julian_cdt.is_valid_ordinal_date((1, 367))
        assert julian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not julian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDate.gen_years_before_era, not applicable

    #
    # ConvertibleDate.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.julian_cd.days_in_months(common_year)
            # fmt: off
            == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.julian_cd.days_in_months(leap_year)
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
        assert self.julian_cd.days_in_month(
            common_year, month
        ) == convertdate.julian.month_length(common_year, month)

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_days_in_month_for_leap_month(self, _):
        leap_year, month, _ = self.random_leap_ymd()
        assert self.julian_cd.days_in_month(
            leap_year, month
        ) == convertdate.julian.month_length(leap_year, month)

    #
    # ConvertibleDate.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.julian_cd.days_in_year(common_year) == 365

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.julian_cd.days_in_year(leap_year) == 366

    #
    # ConvertibleDate.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.julian_cd.months_in_year(common_year) == 12

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.julian_cd.months_in_year(leap_year) == 12

    #
    # Weeks
    #
    @patch("src.db.ConvertibleCalendar.days_in_weeks", return_value=7)
    def test_day_of_week(self, _):
        bc_year, bc_month, bc_day = self.random_bce_ymd()
        bc_julian_day = convertdate.julian.to_jd(bc_year, bc_month, bc_day)
        bc_ordinal = self.julian_dc.from_jd(bc_julian_day) + 1

        ad_year, ad_month, ad_day = self.random_ce_ymd()
        ad_julian_day = convertdate.julian.to_jd(ad_year, ad_month, ad_day)
        ad_ordinal = self.julian_dc.from_jd(ad_julian_day) + 1
        assert self.julian_cd.day_of_week(1) == 5  # 1/1/1 is a Saturday
        assert self.julian_cd.day_of_week(2) == 6
        assert self.julian_cd.day_of_week(3) == 0
        assert self.julian_cd.day_of_week(4) == 1
        assert self.julian_cd.day_of_week(5) == 2
        assert self.julian_cd.day_of_week(6) == 3
        assert self.julian_cd.day_of_week(7) == 4
        assert self.julian_cd.day_of_week(8) == 5
        assert (
            self.julian_cd.day_of_week(bc_ordinal) == (bc_julian_day + 0.5) % 7
        )
        assert (
            self.julian_cd.day_of_week(ad_ordinal) == (ad_julian_day + 0.5) % 7
        )
