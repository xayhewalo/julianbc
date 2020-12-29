import convertdate
import pytest

from calendar import isleap
from .utils import RealCalendarTestCase, FAKE
from unittest.mock import patch


class IndianCivilTest(RealCalendarTestCase):
    """
    Can the database represent the Indian Civil Calendar
    Years are astronomical unless labeled otherwise
    """

    def setUp(self):
        super(IndianCivilTest, self).setUp()
        self.main_calendar = self.indian
        self.to_gregorian_ymd = convertdate.indian_civil.to_gregorian

    def random_common_year(self) -> int:
        hr_year = FAKE.random_int(min=-9999)
        while isleap(hr_year + 78):  # convert to gregorian year
            hr_year = FAKE.random_int(min=-9999)
        return hr_year + 1

    def random_leap_year(self) -> int:
        hr_year = FAKE.random_int(min=-9999)
        while not isleap(hr_year + 78):  # convert to gregorian year
            hr_year = FAKE.random_int(min=-9999)
        return hr_year + 1

    #
    # ConvertibleDateTime.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cdt.convert_ast_ymd((1, 1, 1), self.coptic_cdt)
            == (207, 6, 7)
        )
        assert (
            self.indian_cdt.convert_ast_ymd((-206, 7, 28), self.coptic_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cdt.convert_ast_ymd(coptic_ymd, self.coptic_cdt)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cdt.convert_ast_ymd((1, 1, 1), self.l_hijri_cdt)
            == (545, 4, 28)
        )
        assert (
            self.indian_cdt.convert_ast_ymd((-561, 12, 20), self.l_hijri_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cdt.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cdt)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cdt.convert_ast_ymd((1, 1, 1), self.gregorian_cdt)
            == (-77, 10, 11)
        )
        assert (
            self.indian_cdt.convert_ast_ymd((78, 3, 22), self.gregorian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cdt.convert_ast_ymd(gregorian_ymd, self.gregorian_cdt)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        indian_ymd = self.make_indian_ast_ymd((gyear, gmonth, gday))
        # fmt: off
        assert (
            self.indian_cdt.convert_ast_ymd((1, 1, 1), self.julian_cdt)
            == (-77, 10, 9)
        )
        assert (
            self.indian_cdt.convert_ast_ymd((78, 3, 24), self.julian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cdt.convert_ast_ymd(julian_ymd, self.julian_cdt)
            == indian_ymd
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
    def test_ordinal_date_to_ordinal_for_be_year(self, *_):
        assert self.indian_cdt.ordinal_date_to_ordinal((0, 365)) == 0
        assert self.indian_cdt.ordinal_date_to_ordinal((0, 1)) == -364
        assert self.indian_cdt.ordinal_date_to_ordinal((-1, 366)) == -365
        assert self.indian_cdt.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.indian_cdt.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.indian_cdt.ordinal_date_to_ordinal((-2, 164)) == -932

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=False,
    )
    def test_ordinal_date_to_ordinal_for_se_year(self, *_):
        assert self.indian_cdt.ordinal_date_to_ordinal((1, 1)) == 1
        assert self.indian_cdt.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.indian_cdt.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.indian_cdt.ordinal_date_to_ordinal((2, 101)) == 466
        assert self.indian_cdt.ordinal_date_to_ordinal((3, 366)) == 1096

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        year, month, day = self.random_common_ymd()
        gyear, gmonth, gday = convertdate.indian_civil.to_gregorian(
            year, month, day
        )
        day_of_year = self.indian_dc.from_gregorian(gyear, gmonth, gday)
        with pytest.raises(ValueError):
            self.indian_cdt.ordinal_date_to_ordinal((year, day_of_year))

    def test_ordinal_to_ordinal_date(self):
        assert self.indian_cdt.ordinal_to_ordinal_date(760) == (3, 30)
        assert self.indian_cdt.ordinal_to_ordinal_date(731) == (3, 1)
        assert self.indian_cdt.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.indian_cdt.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.indian_cdt.ordinal_to_ordinal_date(1) == (1, 1)
        assert self.indian_cdt.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.indian_cdt.ordinal_to_ordinal_date(-364) == (0, 1)
        assert self.indian_cdt.ordinal_to_ordinal_date(-365) == (-1, 366)
        assert self.indian_cdt.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.indian_cdt.ordinal_to_ordinal_date(-808) == (-2, 288)

    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self):
        assert self.indian_cdt.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.indian_cdt.ordinal_to_ordinal_date(-60) == (0, 305)
        assert self.indian_cdt.ordinal_to_ordinal_date(-100) == (0, 265)
        assert self.indian_cdt.ordinal_to_ordinal_date(-200) == (0, 165)
        assert self.indian_cdt.ordinal_to_ordinal_date(-300) == (0, 65)
        assert self.indian_cdt.ordinal_to_ordinal_date(-364) == (0, 1)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=True,
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_be_year(self, *_):
        be_ordinal = FAKE.random_int(min=-9999, max=0)
        be_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=365),
        )
        assert (
            self.indian_cdt.ordinal_to_ordinal_date(
                self.indian_cdt.ordinal_date_to_ordinal(be_ordinal_date)
            )
            == be_ordinal_date
        )
        assert (
            self.indian_cdt.ordinal_date_to_ordinal(
                self.indian_cdt.ordinal_to_ordinal_date(be_ordinal)
            )
            == be_ordinal
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=False,
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_se_year(self, *_):
        se_ordinal = FAKE.random_int()
        se_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=365)
        assert (
            self.indian_cdt.ordinal_to_ordinal_date(
                self.indian_cdt.ordinal_date_to_ordinal(se_ordinal_date)
            )
            == se_ordinal_date
        )
        assert (
            self.indian_cdt.ordinal_date_to_ordinal(
                self.indian_cdt.ordinal_to_ordinal_date(se_ordinal)
            )
            == se_ordinal
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
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        indian_cdt = self.indian_cdt
        assert indian_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((2, 12, 30)) == (2, 365)
        assert indian_cdt.ast_ymd_to_ordinal_date((178, 5, 4)) == (178, 127)
        assert indian_cdt.ast_ymd_to_ordinal_date((0, 12, 30)) == (0, 365)
        assert indian_cdt.ast_ymd_to_ordinal_date((-2, 1, 1)) == (-2, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((-66, 8, 7)) == (-66, 222)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        indian_cdt = self.indian_cdt
        assert indian_cdt.ast_ymd_to_ordinal_date((3, 1, 1)) == (3, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((7, 12, 30)) == (7, 366)
        assert indian_cdt.ast_ymd_to_ordinal_date((15, 10, 17)) == (15, 293)
        assert indian_cdt.ast_ymd_to_ordinal_date((-1, 1, 1)) == (-1, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((-73, 12, 30)) == (-73, 366)
        assert indian_cdt.ast_ymd_to_ordinal_date((-38, 7, 22)) == (-38, 208)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.indian_cdt.ast_ymd_to_ordinal_date(self.random_ymd())

    #
    # ConvertibleDateTime.ordinal_date_to_ast_ymd
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        indian_cdt = self.indian_cdt
        assert indian_cdt.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((13, 107)) == (13, 4, 15)
        assert indian_cdt.ordinal_date_to_ast_ymd((55, 365)) == (55, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((0, 365)) == (0, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-25, 335)) == (-25, 11, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-111, 1)) == (-111, 1, 1)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        indian_cdt = self.indian_cdt
        assert indian_cdt.ordinal_date_to_ast_ymd((3, 1)) == (3, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((323, 31)) == (323, 1, 31)
        assert indian_cdt.ordinal_date_to_ast_ymd((43, 366)) == (43, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-1, 366)) == (-1, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-5, 1)) == (-5, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((-37, 82)) == (-37, 3, 20)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = common_year, FAKE.random_int(min=1, max=365)
        ast_ymd = common_year, month, day
        assert (
            self.indian_cdt.ordinal_date_to_ast_ymd(
                self.indian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.indian_cdt.ast_ymd_to_ordinal_date(
                self.indian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = leap_year, FAKE.random_int(min=1, max=366)
        ast_ymd = leap_year, month, day
        assert (
            self.indian_cdt.ordinal_date_to_ast_ymd(
                self.indian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.indian_cdt.ast_ymd_to_ordinal_date(
                self.indian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.indian_cdt.ordinal_date_to_ast_ymd((1, 0))

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = ast_se_year - 1
        assert self.indian_cdt.hr_to_ast(0, 1) == 1
        assert self.indian_cdt.hr_to_ast(1, 0) == 0
        assert self.indian_cdt.hr_to_ast(2, 0) == -1
        assert self.indian_cdt.hr_to_ast(hr_be_year, 0) == ast_be_year
        assert self.indian_cdt.hr_to_ast(hr_se_year, 1) == ast_se_year

    def test_ast_to_hr(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = abs(ast_se_year - 1)
        assert self.indian_cdt.ast_to_hr(1) == (0, 1)
        assert self.indian_cdt.ast_to_hr(0) == (1, 0)
        assert self.indian_cdt.ast_to_hr(-1) == (2, 0)
        assert self.indian_cdt.ast_to_hr(ast_be_year) == (hr_be_year, 0)
        assert self.indian_cdt.ast_to_hr(ast_se_year) == (hr_se_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = ast_se_year - 1
        assert (
            self.indian_cdt.hr_to_ast(*self.indian_cdt.ast_to_hr(ast_be_year))
            == ast_be_year
        )
        assert (
            self.indian_cdt.hr_to_ast(*self.indian_cdt.ast_to_hr(ast_se_year))
            == ast_se_year
        )
        assert self.indian_cdt.ast_to_hr(
            self.indian_cdt.hr_to_ast(hr_be_year, 0)
        ) == (hr_be_year, 0)
        assert self.indian_cdt.ast_to_hr(
            self.indian_cdt.hr_to_ast(hr_se_year, 1)
        ) == (hr_se_year, 1)

    @patch("src.datetimes.ConvertibleDateTime.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ah_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.l_hijri_cdt.ast_to_hr(ast_ah_year)

    def test_parse_hr_date(self):
        se_ymd = self.random_ce_ymd()
        se_ast_year, se_month, se_day = se_ymd
        se_hr_year = se_ast_year - 1

        be_ymd = self.random_bce_ymd()
        be_ast_year, be_month, be_day = be_ymd
        be_hr_year = abs(be_ast_year - 1)

        se_hr_date = self.indian_cdt.date_sep.join(
            [str(se_hr_year), str(se_month), str(se_day), "एस ई"]
        )
        be_hr_date = self.indian_cdt.date_sep.join(
            [str(be_hr_year), str(be_month), str(be_day), "बी ई"]
        )
        assert self.indian_cdt.parse_hr_date(se_hr_date) == se_ymd
        assert self.indian_cdt.parse_hr_date(be_hr_date) == be_ymd

    def test_format_hr_date(self):
        be_ast_ymd = self.random_bce_ymd()
        be_ast_year, be_month, be_day = be_ast_ymd
        be_hr_year = abs(be_ast_year - 1)
        be_hr_date = self.indian_cdt.date_sep.join(
            [str(be_hr_year), str(be_month), str(be_day), "बी ई"]
        )

        se_ast_ymd = self.random_ce_ymd()
        se_ast_year, se_month, se_day = se_ast_ymd
        se_hr_year = se_ast_year - 1
        se_hr_date = self.indian_cdt.date_sep.join(
            [str(se_hr_year), str(se_month), str(se_day), "एस ई"]
        )
        assert self.indian_cdt.format_hr_date(be_ast_ymd) == be_hr_date
        assert self.indian_cdt.format_hr_date(se_ast_ymd) == se_hr_date

    #
    # Eras
    #
    def test_era(self):
        be_year = self.random_bce_year()
        se_year = self.random_ce_year()
        assert self.indian_cdt.era(be_year) == "बी ई"
        assert self.indian_cdt.era(se_year) == "एस ई"

    def test_is_descending_era(self):
        be_year = self.random_bce_year()
        se_year = self.random_ce_year()
        assert self.indian_cdt.is_descending_era(be_year)
        assert self.indian_cdt.is_descending_era(se_year) is False

    #
    # ConvertibleDateTime.is_leap_year
    #
    def test_is_leap_year(self):
        common_be_year = self.random_common_bce_year()
        common_se_year = self.random_common_ce_year()
        leap_be_year = self.random_leap_bce_year()
        leap_se_year = self.random_leap_ce_year()
        assert self.indian_cdt.is_leap_year(0) is False
        assert self.indian_cdt.is_leap_year(common_be_year) is False
        assert self.indian_cdt.is_leap_year(common_se_year) is False
        assert self.indian_cdt.is_leap_year(3)
        assert self.indian_cdt.is_leap_year(leap_be_year)
        assert self.indian_cdt.is_leap_year(leap_se_year)

    #
    # ConvertibleDateTime.is_valid_ast_ymd
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.indian_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=366)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.indian_cdt.is_valid_ast_ymd((year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        indian_cdt = self.indian_cdt
        assert not indian_cdt.is_valid_ast_ymd((year, bad_month, day))
        assert not indian_cdt.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDateTime.is_valid_ordinal_date
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        indian_cdt = self.indian_cdt
        assert not indian_cdt.is_valid_ordinal_date((1, 366))
        assert indian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not indian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        indian_cdt = self.indian_cdt
        assert not indian_cdt.is_valid_ordinal_date((1, 367))
        assert indian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not indian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

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
            self.indian_cdt.days_in_months(common_year)
            # fmt: off
            == [30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30]
            # fmt: on
        )

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.indian_cdt.days_in_months(leap_year)
            # fmt: off
            == [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30]
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
        assert self.indian_cdt.days_in_year(common_year) == 365

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.indian_cdt.days_in_year(leap_year) == 366

    #
    # ConvertibleDateTime.months_in_year
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_leap_year", return_value=False
    )
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.indian_cdt.months_in_year(common_year) == 12

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.indian_cdt.months_in_year(leap_year) == 12

    #
    # Weeks
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_week", return_value=7)
    def test_day_of_week(self, _):
        be_year, be_month, be_day = self.random_bce_ymd()
        be_julian_day = convertdate.indian_civil.to_jd(
            be_year, be_month, be_day
        )
        be_ordinal = self.indian_dc.from_jd(be_julian_day) + 1

        se_year, se_month, se_day = self.random_ce_ymd()
        se_julian_day = convertdate.indian_civil.to_jd(
            se_year, se_month, se_day
        )
        se_ordinal = self.indian_dc.from_jd(se_julian_day) + 1
        assert self.indian_cdt.day_of_week(1) == 2  # 0/1/1 is the third day
        assert self.indian_cdt.day_of_week(2) == 3
        assert self.indian_cdt.day_of_week(3) == 4
        assert self.indian_cdt.day_of_week(4) == 5
        assert self.indian_cdt.day_of_week(5) == 6
        assert self.indian_cdt.day_of_week(6) == 0
        assert self.indian_cdt.day_of_week(7) == 1
        assert self.indian_cdt.day_of_week(8) == 2
        assert (
            self.indian_cdt.day_of_week(be_ordinal)
            == (be_julian_day + 1.5) % 7
        )
        assert (
            self.indian_cdt.day_of_week(se_ordinal)
            == (se_julian_day + 1.5) % 7
        )

    def test_days_in_week(self):
        assert self.indian_cdt.days_in_week() == 7
