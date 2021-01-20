import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
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

    @staticmethod
    def random_common_year() -> int:
        # don't check with convertdate, it's leap method is wrong
        return (FAKE.random_int(min=-9999) * 4) - 1

    @staticmethod
    def random_leap_year() -> int:
        # don't check with convertdate, it's leap method is wrong
        return FAKE.random_int(min=-9999) * 4

    #
    # ConvertibleDateTime.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cdt.convert_ast_ymd((1, 1, 1), self.coptic_cdt)
            == (284, 8, 29)
        )
        assert (
            self.julian_cdt.convert_ast_ymd((-283, 5, 6), self.coptic_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cdt.convert_ast_ymd(coptic_ymd, self.coptic_cdt)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cdt.convert_ast_ymd((1, 1, 1), self.indian_cdt)
            == (78, 3, 24)
        )
        assert (
            self.julian_cdt.convert_ast_ymd((-77, 10, 9), self.indian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cdt.convert_ast_ymd(indian_ymd, self.indian_cdt)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.julian_cdt.convert_ast_ymd((1, 1, 1), self.gregorian_cdt)
            == (1, 1, 3)
        )
        assert (
            self.julian_cdt.convert_ast_ymd((0, 12, 30), self.gregorian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cdt.convert_ast_ymd(gregorian_ymd, self.gregorian_cdt)
            == julian_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        l_hijri_ymd = convertdate.islamic.from_gregorian(gyear, gmonth, gday)
        # fmt: off
        assert (
            self.julian_cdt.convert_ast_ymd((1, 1, 1), self.l_hijri_cdt)
            == (622, 7, 16)
        )
        assert (
            self.julian_cdt.convert_ast_ymd((-640, 5, 16), self.l_hijri_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.julian_cdt.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cdt)
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
        assert self.julian_cdt.ordinal_to_ordinal_date(791) == (3, 61)
        assert self.julian_cdt.ordinal_to_ordinal_date(730) == (2, 365)
        assert self.julian_cdt.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.julian_cdt.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.julian_cdt.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_bc_year(self, *_):
        assert self.julian_cdt.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.julian_cdt.ordinal_to_ordinal_date(-365) == (0, 1)
        assert self.julian_cdt.ordinal_to_ordinal_date(-366) == (-1, 365)
        assert self.julian_cdt.ordinal_to_ordinal_date(-466) == (-1, 265)
        assert self.julian_cdt.ordinal_to_ordinal_date(-731) == (-2, 365)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.julian_cdt.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.julian_cdt.ordinal_to_ordinal_date(-100) == (0, 266)
        assert self.julian_cdt.ordinal_to_ordinal_date(-200) == (0, 166)
        assert self.julian_cdt.ordinal_to_ordinal_date(-300) == (0, 66)
        assert self.julian_cdt.ordinal_to_ordinal_date(-365) == (0, 1)

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
    def test_ordinal_date_to_ordinal_for_bc_year(self, *_):
        assert self.julian_cdt.ordinal_date_to_ordinal((0, 366)) == 0
        assert self.julian_cdt.ordinal_date_to_ordinal((0, 1)) == -365
        assert self.julian_cdt.ordinal_date_to_ordinal((-1, 365)) == -366
        assert self.julian_cdt.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.julian_cdt.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.julian_cdt.ordinal_date_to_ordinal((-2, 165)) == -931

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
    def test_ordinal_date_to_ordinal_for_ad_year(self, *_):
        assert self.julian_cdt.ordinal_date_to_ordinal((1, 1)) == 1
        assert self.julian_cdt.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.julian_cdt.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.julian_cdt.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.julian_cdt.ordinal_date_to_ordinal((3, 102)) == 832

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
            self.julian_cdt.ordinal_to_ordinal_date(
                self.julian_cdt.ordinal_date_to_ordinal(bc_ordinal_date)
            )
            == bc_ordinal_date
        )
        assert (
            self.julian_cdt.ordinal_date_to_ordinal(
                self.julian_cdt.ordinal_to_ordinal_date(bc_ordinal)
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
            self.julian_cdt.ordinal_to_ordinal_date(
                self.julian_cdt.ordinal_date_to_ordinal(ad_ordinal_date)
            )
            == ad_ordinal_date
        )
        assert (
            self.julian_cdt.ordinal_date_to_ordinal(
                self.julian_cdt.ordinal_to_ordinal_date(ad_ordinal)
            )
            == ad_ordinal
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        with pytest.raises(ValueError):
            self.julian_cdt.ordinal_date_to_ordinal((1, 0))

    #
    # ConvertibleDateTime.ast_ymd_to_ordinal_date
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
        julian_cdt = self.julian_cdt
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
        julian_cdt = self.julian_cdt
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
            self.julian_cdt.ast_ymd_to_ordinal_date(self.random_ymd())

    #
    # ConvertibleDateTime.ordinal_date_to_ast_ymd
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
        julian_cdt = self.julian_cdt
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
        julian_cdt = self.julian_cdt
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
            self.julian_cdt.ordinal_date_to_ast_ymd(
                self.julian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.julian_cdt.ast_ymd_to_ordinal_date(
                self.julian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
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
            self.julian_cdt.ordinal_date_to_ast_ymd(
                self.julian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.julian_cdt.ast_ymd_to_ordinal_date(
                self.julian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.julian_cdt.ordinal_date_to_ast_ymd((1, 0))

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        ast_bc_year = self.random_bce_year()
        hr_bc_year = abs(ast_bc_year - 1)
        hr_ad_year = self.random_ce_year()
        assert self.julian_cdt.hr_to_ast(1, 1) == 1
        assert self.julian_cdt.hr_to_ast(1, 0) == 0
        assert self.julian_cdt.hr_to_ast(2, 0) == -1
        assert self.julian_cdt.hr_to_ast(hr_bc_year, 0) == ast_bc_year
        assert self.julian_cdt.hr_to_ast(hr_ad_year, 1) == hr_ad_year

    def test_ast_to_hr(self):
        ast_bc_year = self.random_bce_year()
        hr_bc_year = abs(ast_bc_year - 1)
        ast_ad_year = self.random_ce_year()
        assert self.julian_cdt.ast_to_hr(1) == (1, 1)
        assert self.julian_cdt.ast_to_hr(0) == (1, 0)
        assert self.julian_cdt.ast_to_hr(-1) == (2, 0)
        assert self.julian_cdt.ast_to_hr(ast_bc_year) == (hr_bc_year, 0)
        assert self.julian_cdt.ast_to_hr(ast_ad_year) == (ast_ad_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        hr_ce_year = ast_ce_year
        assert (
            self.julian_cdt.hr_to_ast(*self.julian_cdt.ast_to_hr(ast_bce_year))
            == ast_bce_year
        )
        assert (
            self.julian_cdt.hr_to_ast(*self.julian_cdt.ast_to_hr(ast_ce_year))
            == ast_ce_year
        )
        assert self.julian_cdt.ast_to_hr(
            self.julian_cdt.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.julian_cdt.ast_to_hr(
            self.julian_cdt.hr_to_ast(hr_ce_year, 1)
        ) == (hr_ce_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ad_ast_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.julian_cdt.ast_to_hr(ad_ast_year)

    def test_parse_hr_date(self):
        ad_ymd = self.random_ce_ymd()
        ad_ast_year, ad_month, ad_day = ad_ymd
        ad_hr_year = ad_ast_year

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)

        ad_hr_date = self.julian_cdt.date_sep.join(
            [str(ad_hr_year), str(ad_month), str(ad_day), "AD"]
        )
        bc_hr_date = self.julian_cdt.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.julian_cdt.parse_hr_date(ad_hr_date) == ad_ymd
        assert self.julian_cdt.parse_hr_date(bc_hr_date) == bc_ymd

    def test_format_hr_date(self):
        bc_ast_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ast_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.julian_cdt.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )

        ad_ast_ymd = self.random_ce_ymd()
        ad_ast_year, ad_month, ad_day = ad_ast_ymd
        ad_hr_date = self.julian_cdt.date_sep.join(
            [str(ad_ast_year), str(ad_month), str(ad_day), "AD"]
        )
        assert self.julian_cdt.format_hr_date(bc_ast_ymd) == bc_hr_date
        assert self.julian_cdt.format_hr_date(ad_ast_ymd) == ad_hr_date

    #
    # Eras
    #
    def test_era(self):
        bc_year = self.random_bce_year()
        ad_year = self.random_ce_year()
        assert self.julian_cdt.era(bc_year) == "BC"
        assert self.julian_cdt.era(ad_year) == "AD"

    def test_is_descending_era(self):
        bc_year = self.random_bce_year()
        ad_year = self.random_ce_year()
        assert self.julian_cdt.is_descending_era(bc_year)
        assert self.julian_cdt.is_descending_era(ad_year) is False

    #
    # ConvertibleDateTime.is_leap_year
    #
    def test_is_leap_year(self):
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.julian_cdt.is_leap_year(common_bce_year) is False
        assert self.julian_cdt.is_leap_year(common_ce_year) is False
        assert self.julian_cdt.is_leap_year(leap_bce_year)
        assert self.julian_cdt.is_leap_year(leap_ce_year)

    #
    # ConvertibleDateTime.is_valid_ast_ymd
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.julian_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.julian_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        assert not self.julian_cdt.is_valid_ast_ymd((year, bad_month, day))
        assert not self.julian_cdt.is_valid_ast_ymd((year, bad_month, bad_day))

    #
    # ConvertibleDateTime.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        julian_cdt = self.julian_cdt
        assert not julian_cdt.is_valid_ordinal_date((1, 366))
        assert julian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not julian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        julian_cdt = self.julian_cdt
        assert not julian_cdt.is_valid_ordinal_date((1, 367))
        assert julian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not julian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDateTime.gen_years_before_era, not applicable

    #
    # ConvertibleDateTime.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.julian_cdt.days_in_months(common_year)
            # fmt: off
            == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.julian_cdt.days_in_months(leap_year)
            # fmt: off
            == [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    #
    # ConvertibleDateTime.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.julian_cdt.days_in_year(common_year) == 365

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.julian_cdt.days_in_year(leap_year) == 366

    #
    # ConvertibleDateTime.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.julian_cdt.months_in_year(common_year) == 12

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.julian_cdt.months_in_year(leap_year) == 12

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
        assert self.julian_cdt.day_of_week(1) == 5  # 1/1/1 is a Saturday
        assert self.julian_cdt.day_of_week(2) == 6
        assert self.julian_cdt.day_of_week(3) == 0
        assert self.julian_cdt.day_of_week(4) == 1
        assert self.julian_cdt.day_of_week(5) == 2
        assert self.julian_cdt.day_of_week(6) == 3
        assert self.julian_cdt.day_of_week(7) == 4
        assert self.julian_cdt.day_of_week(8) == 5
        assert (
            self.julian_cdt.day_of_week(bc_ordinal)
            == (bc_julian_day + 0.5) % 7
        )
        assert (
            self.julian_cdt.day_of_week(ad_ordinal)
            == (ad_julian_day + 0.5) % 7
        )
