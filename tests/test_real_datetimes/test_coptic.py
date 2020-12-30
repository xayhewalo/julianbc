import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
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

    #
    # ConvertibleDateTime.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.coptic_cdt.convert_ast_ymd((1, 1, 1), self.l_hijri_cdt)
            == (338, 11, 22)
        )
        assert (
            self.coptic_cdt.convert_ast_ymd((-348, 9, 29), self.l_hijri_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cdt.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cdt)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert(
            self.coptic_cdt.convert_ast_ymd((1, 1, 1), self.indian_cdt)
            == (-206, 7, 28)
        )
        assert (
            self.coptic_cdt.convert_ast_ymd((207, 6, 7), self.indian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cdt.convert_ast_ymd(indian_ymd, self.indian_cdt)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.coptic_cdt.convert_ast_ymd((1, 1, 1), self.gregorian_cdt)
            == (-283, 5, 8)
        )
        assert (
            self.coptic_cdt.convert_ast_ymd((284, 8, 29), self.gregorian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cdt.convert_ast_ymd(gregorian_ymd, self.gregorian_cdt)
            == coptic_ymd
        )

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        coptic_ymd = convertdate.coptic.from_gregorian(gyear, gmonth, gday)
        # fmt: off
        assert (
            self.coptic_cdt.convert_ast_ymd((1, 1, 1), self.julian_cdt)
            == (-283, 5, 6)
        )
        assert (
            self.coptic_cdt.convert_ast_ymd((284, 8, 29), self.julian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.coptic_cdt.convert_ast_ymd(julian_ymd, self.julian_cdt)
            == coptic_ymd
        )

    #
    # Ordinals
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_date_to_ordinal_for_bc_year(self, *_):
        assert self.coptic_cdt.ordinal_date_to_ordinal((0, 365)) == 0
        assert self.coptic_cdt.ordinal_date_to_ordinal((0, 1)) == -364
        assert self.coptic_cdt.ordinal_date_to_ordinal((-1, 366)) == -365
        assert self.coptic_cdt.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.coptic_cdt.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.coptic_cdt.ordinal_date_to_ordinal((-2, 300)) == -796

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=False,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_date_to_ordinal_for_am_year(self, *_):
        assert self.coptic_cdt.ordinal_date_to_ordinal((4, 187)) == 1283
        assert self.coptic_cdt.ordinal_date_to_ordinal((4, 1)) == 1097
        assert self.coptic_cdt.ordinal_date_to_ordinal((3, 366)) == 1096
        assert self.coptic_cdt.ordinal_date_to_ordinal((3, 1)) == 731
        assert self.coptic_cdt.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.coptic_cdt.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.coptic_cdt.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.coptic_cdt.ordinal_date_to_ordinal((1, 1)) == 1

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        year, month, day = self.random_common_ymd()
        year, month, day = convertdate.coptic.to_gregorian(year, month, day)
        day_of_year = self.coptic_dc.from_gregorian(year, month, day)
        with pytest.raises(ValueError):
            self.l_hijri_cdt.ordinal_date_to_ordinal((year, day_of_year))

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_for_am_year(self, *_):
        assert self.coptic_cdt.ordinal_to_ordinal_date(829) == (3, 99)
        assert self.coptic_cdt.ordinal_to_ordinal_date(731) == (3, 1)
        assert self.coptic_cdt.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.coptic_cdt.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.coptic_cdt.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_bc_year(self, *_):
        assert self.coptic_cdt.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-365) == (-1, 366)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-791) == (-2, 305)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.coptic_cdt.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-90) == (0, 275)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-170) == (0, 195)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-266) == (0, 99)
        assert self.coptic_cdt.ordinal_to_ordinal_date(-364) == (0, 1)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(0, -1),
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_bce_year(self, *_):
        bce_ordinal = FAKE.random_int(min=-9999, max=0)
        bce_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=365),
        )
        assert (
            self.coptic_cdt.ordinal_to_ordinal_date(
                self.coptic_cdt.ordinal_date_to_ordinal(bce_ordinal_date)
            )
            == bce_ordinal_date
        )
        assert (
            self.coptic_cdt.ordinal_date_to_ordinal(
                self.coptic_cdt.ordinal_to_ordinal_date(bce_ordinal)
            )
            == bce_ordinal
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=False,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_am_year(self, *_):
        am_ordinal = FAKE.random_int()
        am_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=365)
        assert (
            self.coptic_cdt.ordinal_to_ordinal_date(
                self.coptic_cdt.ordinal_date_to_ordinal(am_ordinal_date)
            )
            == am_ordinal_date
        )
        assert (
            self.coptic_cdt.ordinal_date_to_ordinal(
                self.coptic_cdt.ordinal_to_ordinal_date(am_ordinal)
            )
            == am_ordinal
        )

    #
    # ConvertibleDateTime.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        coptic_cdt = self.coptic_cdt
        assert coptic_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((1000, 13, 5)) == (1000, 365)
        assert coptic_cdt.ast_ymd_to_ordinal_date((40, 8, 18)) == (40, 228)
        assert coptic_cdt.ast_ymd_to_ordinal_date((0, 13, 5)) == (0, 365)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-120, 1, 1)) == (-120, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-200, 3, 29)) == (-200, 89)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        coptic_cdt = self.coptic_cdt
        assert coptic_cdt.ast_ymd_to_ordinal_date((3, 1, 1)) == (3, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((15, 3, 30)) == (15, 90)
        assert coptic_cdt.ast_ymd_to_ordinal_date((39, 11, 13)) == (39, 313)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-1, 13, 6)) == (-1, 366)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-13, 1, 1)) == (-13, 1)
        assert coptic_cdt.ast_ymd_to_ordinal_date((-101, 5, 22)) == (-101, 142)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.coptic_cdt.ast_ymd_to_ordinal_date(self.random_ymd())

    #
    # ConvertibleDateTime.ordinal_date_to_ast_ymd
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        coptic_cdt = self.coptic_cdt
        assert coptic_cdt.ordinal_date_to_ast_ymd((4, 1)) == (4, 1, 1)
        assert coptic_cdt.ordinal_date_to_ast_ymd((20, 270)) == (20, 9, 30)
        assert coptic_cdt.ordinal_date_to_ast_ymd((400, 43)) == (400, 2, 13)
        assert coptic_cdt.ordinal_date_to_ast_ymd((0, 365)) == (0, 13, 5)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-44, 299)) == (-44, 10, 29)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-80, 115)) == (-80, 4, 25)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        coptic_cdt = self.coptic_cdt
        assert coptic_cdt.ordinal_date_to_ast_ymd((3, 1)) == (3, 1, 1)
        assert coptic_cdt.ordinal_date_to_ast_ymd((27, 75)) == (27, 3, 15)
        assert coptic_cdt.ordinal_date_to_ast_ymd((2019, 366)) == (2019, 13, 6)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-1, 366)) == (-1, 13, 6)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-5, 147)) == (-5, 5, 27)
        assert coptic_cdt.ordinal_date_to_ast_ymd((-21, 300)) == (-21, 10, 30)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = common_year, FAKE.random_int(min=1, max=365)
        ast_ymd = common_year, month, day
        assert (
            self.coptic_cdt.ordinal_date_to_ast_ymd(
                self.coptic_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.coptic_cdt.ast_ymd_to_ordinal_date(
                self.coptic_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = leap_year, FAKE.random_int(min=1, max=366)
        ast_ymd = leap_year, month, day
        assert (
            self.coptic_cdt.ordinal_date_to_ast_ymd(
                self.coptic_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.coptic_cdt.ast_ymd_to_ordinal_date(
                self.coptic_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.coptic_cdt.ordinal_date_to_ast_ymd((1, 1))

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        bc_ast_year = self.random_bce_year()
        bc_hr_year = abs(bc_ast_year - 1)
        am_ast_year = am_hr_year = self.random_ce_year()
        assert self.coptic_cdt.hr_to_ast(1, 1) == 1
        assert self.coptic_cdt.hr_to_ast(1, 0) == 0
        assert self.coptic_cdt.hr_to_ast(2, 0) == -1
        assert self.coptic_cdt.hr_to_ast(bc_hr_year, 0) == bc_ast_year
        assert self.coptic_cdt.hr_to_ast(am_hr_year, 1) == am_ast_year

    def test_ast_to_hr(self):
        bc_ast_year = self.random_bce_year()
        bc_hr_year = abs(bc_ast_year - 1)
        am_ast_year = am_hr_year = self.random_ce_year()
        assert self.coptic_cdt.ast_to_hr(1) == (1, 1)
        assert self.coptic_cdt.ast_to_hr(0) == (1, 0)
        assert self.coptic_cdt.ast_to_hr(-1) == (2, 0)
        assert self.coptic_cdt.ast_to_hr(bc_ast_year) == (bc_hr_year, 0)
        assert self.coptic_cdt.ast_to_hr(am_ast_year) == (am_hr_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_am_year = self.random_ce_year()
        hr_am_year = ast_am_year
        assert (
            self.coptic_cdt.hr_to_ast(*self.coptic_cdt.ast_to_hr(ast_bce_year))
            == ast_bce_year
        )
        assert (
            self.coptic_cdt.hr_to_ast(*self.coptic_cdt.ast_to_hr(ast_am_year))
            == ast_am_year
        )
        assert self.coptic_cdt.ast_to_hr(
            self.coptic_cdt.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.coptic_cdt.ast_to_hr(
            self.coptic_cdt.hr_to_ast(hr_am_year, 1)
        ) == (hr_am_year, 1)

    @patch("src.datetimes.ConvertibleDateTime.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ah_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.coptic_cdt.ast_to_hr(ast_ah_year)

    def test_parse_hr_date(self):
        am_ymd = self.random_ce_ymd()
        am_ast_year, am_month, am_day = am_ymd
        am_hr_year = am_ast_year
        am_hr_date = self.coptic_cdt.date_sep.join(
            [str(am_hr_year), str(am_month), str(am_day), "AM"]
        )

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.coptic_cdt.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.coptic_cdt.parse_hr_date(am_hr_date) == am_ymd
        assert self.coptic_cdt.parse_hr_date(bc_hr_date) == bc_ymd

    def test_format_hr_date(self):
        am_ymd = self.random_ce_ymd()
        am_ast_year, am_month, am_day = am_ymd
        am_hr_year = am_ast_year
        am_hr_date = self.coptic_cdt.date_sep.join(
            [str(am_hr_year), str(am_month), str(am_day), "AM"]
        )

        bc_ymd = self.random_bce_ymd()
        bc_ast_year, bc_month, bc_day = bc_ymd
        bc_hr_year = abs(bc_ast_year - 1)
        bc_hr_date = self.coptic_cdt.date_sep.join(
            [str(bc_hr_year), str(bc_month), str(bc_day), "BC"]
        )
        assert self.coptic_cdt.format_hr_date(bc_ymd) == bc_hr_date
        assert self.coptic_cdt.format_hr_date(am_ymd) == am_hr_date

    #
    # Eras
    #
    def test_era(self):
        bc_year = self.random_bce_year()
        am_year = self.random_ce_year()
        assert self.coptic_cdt.era(bc_year) == "BC"
        assert self.coptic_cdt.era(am_year) == "AM"

    def test_is_descending_era(self):
        bc_year = self.random_bce_year()
        am_year = self.random_ce_year()
        assert self.coptic_cdt.is_descending_era(bc_year)
        assert self.coptic_cdt.is_descending_era(am_year) is False

    #
    # ConvertibleDateTime.is_leap_year
    #
    def test_is_leap_year(self):
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.coptic_cdt.is_leap_year(1) is False
        assert self.coptic_cdt.is_leap_year(8) is False
        assert self.coptic_cdt.is_leap_year(common_bce_year) is False
        assert self.coptic_cdt.is_leap_year(common_ce_year) is False
        assert self.coptic_cdt.is_leap_year(3) is True
        assert self.coptic_cdt.is_leap_year(7) is True
        assert self.coptic_cdt.is_leap_year(leap_bce_year) is True
        assert self.coptic_cdt.is_leap_year(leap_ce_year) is True

    #
    # ConvertibleDateTime.is_valid_ast_ymd
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.coptic_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=366)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.coptic_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=13)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=14)
        bad_day = FAKE.random_int(min=31)
        assert not self.coptic_cdt.is_valid_ast_ymd((year, bad_month, day))
        assert not self.coptic_cdt.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDateTime.is_valid_ordinal_date
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        coptic_cdt = self.coptic_cdt
        assert not coptic_cdt.is_valid_ordinal_date((1, 366))
        assert coptic_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not coptic_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        coptic_cdt = self.coptic_cdt
        assert not coptic_cdt.is_valid_ordinal_date((1, 366))
        assert coptic_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not coptic_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDateTime.gen_years_before_era, not applicable

    #
    # ConvertibleDateTime.days_in_months
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_leap_year", return_value=False
    )
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.coptic_cdt.days_in_months(common_year)
            # fmt: off
            == [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 5]
            # fmt: on
        )

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_months_for_leap(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.coptic_cdt.days_in_months(leap_year)
            # fmt: off
            == [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 6]
            # fmt: on
        )

    #
    # ConvertibleDateTime.days_in_year
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_leap_year", return_value=False
    )
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.coptic_cdt.days_in_year(common_year) == 365

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.coptic_cdt.days_in_year(leap_year) == 366

    #
    # ConvertibleDateTime.months_in_year
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_leap_year", return_value=False
    )
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.coptic_cdt.months_in_year(common_year) == 13

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.coptic_cdt.months_in_year(leap_year) == 13

    #
    # Weeks
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_week", return_value=7)
    def test_day_of_week(self, _):
        bc_year, bc_month, bc_day = self.random_bce_ymd()
        bc_julian_day = convertdate.coptic.to_jd(bc_year, bc_month, bc_day)
        bc_ordinal = self.coptic_dc.from_jd(bc_julian_day) + 1

        am_year, am_month, am_day = self.random_ce_ymd()
        am_julian_day = convertdate.coptic.to_jd(am_year, am_month, am_day)
        am_ordinal = self.coptic_dc.from_jd(am_julian_day) + 1
        assert self.coptic_cdt.day_of_week(1) == 5  # 1/1/1 is the sixth day
        assert self.coptic_cdt.day_of_week(2) == 6
        assert self.coptic_cdt.day_of_week(3) == 0
        assert self.coptic_cdt.day_of_week(4) == 1
        assert self.coptic_cdt.day_of_week(5) == 2
        assert self.coptic_cdt.day_of_week(6) == 3
        assert self.coptic_cdt.day_of_week(7) == 4
        assert self.coptic_cdt.day_of_week(8) == 5
        assert (
            self.coptic_cdt.day_of_week(bc_ordinal)
            == (convertdate.utils.jwday(bc_julian_day) + 1) % 7
        )
        assert (
            self.coptic_cdt.day_of_week(am_ordinal)
            == (convertdate.utils.jwday(am_julian_day) + 1) % 7
        )

    def test_days_in_week(self):
        assert self.coptic_cdt.days_in_week() == 7
