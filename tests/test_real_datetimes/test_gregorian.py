import convertdate
import pytest

from .utils import RealCalendarTestCase
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

    #
    # ConvertibleDateTime.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ast_ymd = self.random_ymd()
        coptic_ast_ymd = convertdate.coptic.from_gregorian(*gregorian_ast_ymd)
        # fmt: off
        assert (
            self.gregorian_cdt.convert_ast_ymd((1, 1, 1), self.coptic_cdt)
            == (284, 8, 29)
        )
        # fmt: on
        assert (
            self.gregorian_cdt.convert_ast_ymd(coptic_ast_ymd, self.coptic_cdt)
            == gregorian_ast_ymd
        )

    @pytest.mark.db
    def test_convert_indian_ast_ymd(self):
        gregorian_ast_ymd = self.random_convertible_gregorian_ymd()
        indian_ast_ymd = self.make_indian_ast_ymd(gregorian_ast_ymd)
        # fmt: off
        assert (
            self.gregorian_cdt.convert_ast_ymd((1, 1, 1), self.indian_cdt)
            == (78, 3, 22)
        )
        assert (
            self.gregorian_cdt.convert_ast_ymd((3, 2, 1), self.indian_cdt)
            == (80, 4, 21)
        )
        # fmt: on
        assert (
            self.gregorian_cdt.convert_ast_ymd(indian_ast_ymd, self.indian_cdt)
            == gregorian_ast_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        year, month, day = self.random_ymd()
        l_hijri_ast_ymd = convertdate.islamic.from_gregorian(year, month, day)
        l_hijri_cdt = self.l_hijri_cdt
        # fmt: off
        assert (
            self.gregorian_cdt.convert_ast_ymd((1, 1, 1), l_hijri_cdt)
            == (622, 7, 19)
        )
        assert (
            self.gregorian_cdt.convert_ast_ymd((-640, 5, 18), l_hijri_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert self.gregorian_cdt.convert_ast_ymd(
            l_hijri_ast_ymd, l_hijri_cdt
        ) == (year, month, day)

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        year, month, day = self.random_convertible_gregorian_ymd()
        julian_ast_ymd = convertdate.julian.from_gregorian(year, month, day)
        # fmt: off
        assert (
            self.gregorian_cdt.convert_ast_ymd((1, 1, 1), self.julian_cdt)
            == (0, 12, 30)
        )
        assert (
            self.gregorian_cdt.convert_ast_ymd((1, 1, 3), self.julian_cdt)
            == (1, 1, 1)
        )
        # fmt: on
        assert self.gregorian_cdt.convert_ast_ymd(
            julian_ast_ymd, self.julian_cdt
        ) == (year, month, day)

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
    def test_ordinal_date_to_ordinal_for_bce_year(self, *_):
        _ordinal, ordinal_date = self.random_bce_ordinal_and_ordinal_date()
        assert self.gregorian_cdt.ordinal_date_to_ordinal((0, 366)) == 0
        assert self.gregorian_cdt.ordinal_date_to_ordinal((0, 1)) == -365
        assert self.gregorian_cdt.ordinal_date_to_ordinal((-1, 365)) == -366
        assert self.gregorian_cdt.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.gregorian_cdt.ordinal_date_to_ordinal((-2, 365)) == -731
        assert (
            self.gregorian_cdt.ordinal_date_to_ordinal(ordinal_date)
            == _ordinal
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=False,
    )
    def test_ordinal_date_to_ordinal_for_ce_year(self, *_):
        _ordinal, ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        assert self.gregorian_cdt.ordinal_date_to_ordinal((2, 365)) == 730
        assert self.gregorian_cdt.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.gregorian_cdt.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.gregorian_cdt.ordinal_date_to_ordinal((1, 1)) == 1
        assert (
            self.gregorian_cdt.ordinal_date_to_ordinal(ordinal_date)
            == _ordinal
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ordinal_raises(self, *_):
        year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(year, month, day)
        with pytest.raises(ValueError):
            self.gregorian_cdt.ordinal_date_to_ordinal(ordinal_date)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    def test_ordinal_to_ordinal_date(self, _):
        bce_ordinal_n_ordinal_date = self.random_bce_ordinal_and_ordinal_date()
        bce_ordinal, bce_ordinal_date = bce_ordinal_n_ordinal_date
        ce_ordinal, ce_ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        assert self.gregorian_cdt.ordinal_to_ordinal_date(730) == (2, 365)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(1) == (1, 1)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(-366) == (-1, 365)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert (
            self.gregorian_cdt.ordinal_to_ordinal_date(bce_ordinal)
            == bce_ordinal_date
        )
        assert (
            self.gregorian_cdt.ordinal_to_ordinal_date(ce_ordinal)
            == ce_ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, _):
        year = 0
        _, month, day = self.random_leap_bce_ymd()
        _ordinal = self.gregorian_dc.from_gregorian(year, month, day) + 1
        ordinal_date = ordinal.from_gregorian(year, month, day)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(0) == (0, 366)
        assert self.gregorian_cdt.ordinal_to_ordinal_date(-365) == (0, 1)
        assert (
            self.gregorian_cdt.ordinal_to_ordinal_date(_ordinal)
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.is_descending_era",
        return_value=True,
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_bce_year(self, *_):
        bce_ymd = self.random_bce_ymd()
        bce_ordinal = self.gregorian_dc.from_gregorian(*bce_ymd) + 1
        bce_ordinal_date = ordinal.from_gregorian(*bce_ymd)
        assert (
            self.gregorian_cdt.ordinal_to_ordinal_date(
                self.gregorian_cdt.ordinal_date_to_ordinal(bce_ordinal_date)
            )
            == bce_ordinal_date
        )
        assert (
            self.gregorian_cdt.ordinal_date_to_ordinal(
                self.gregorian_cdt.ordinal_to_ordinal_date(bce_ordinal)
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
    def test_ordinal_to_ordinal_date_is_reversible_for_ce_year(self, *_):
        ce_ymd = self.random_ce_ymd()
        ce_ordinal = self.gregorian_dc.from_gregorian(*ce_ymd) + 1
        ce_ordinal_date = ordinal.from_gregorian(*ce_ymd)
        assert (
            self.gregorian_cdt.ordinal_to_ordinal_date(
                self.gregorian_cdt.ordinal_date_to_ordinal(ce_ordinal_date)
            )
            == ce_ordinal_date
        )
        assert (
            self.gregorian_cdt.ordinal_date_to_ordinal(
                self.gregorian_cdt.ordinal_to_ordinal_date(ce_ordinal)
            )
            == ce_ordinal
        )

    #
    # ConvertibleDateTime.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.gregorian_cdt.ast_ymd_to_ordinal_date(
            (year, month, day)
        ) == ordinal.from_gregorian(year, month, day)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.gregorian_cdt.ast_ymd_to_ordinal_date(
            (year, month, day)
        ) == ordinal.from_gregorian(year, month, day)

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.gregorian_cdt.ast_ymd_to_ordinal_date(self.random_ymd())

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
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(common_year, month, day)
        ast_ymd = common_year, month, day
        assert self.gregorian_cdt.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert (
            self.gregorian_cdt.ordinal_date_to_ast_ymd(ordinal_date) == ast_ymd
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = ordinal.from_gregorian(leap_year, month, day)
        ast_ymd = (leap_year, month, day)
        # fmt: off
        assert (
            self.gregorian_cdt.ordinal_date_to_ast_ymd((0, 366)) == (0, 12, 31)
        )
        # fmt: on
        assert (
            self.gregorian_cdt.ordinal_date_to_ast_ymd(ordinal_date) == ast_ymd
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = ordinal.from_gregorian(common_year, month, day)
        ast_ymd = common_year, month, day
        assert (
            self.gregorian_cdt.ordinal_date_to_ast_ymd(
                self.gregorian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.gregorian_cdt.ast_ymd_to_ordinal_date(
                self.gregorian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
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
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = ordinal.from_gregorian(leap_year, month, day)
        ast_ymd = leap_year, month, day
        assert (
            self.gregorian_cdt.ordinal_date_to_ast_ymd(
                self.gregorian_cdt.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.gregorian_cdt.ast_ymd_to_ordinal_date(
                self.gregorian_cdt.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.datetimes.ConvertibleDateTime.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, *_):
        ordinal_date = self.random_ce_ordinal_and_ordinal_date()
        with pytest.raises(ValueError):
            self.gregorian_cdt.ordinal_date_to_ast_ymd(ordinal_date)

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        hr_bce_year = abs(self.random_bce_year()) + 1
        ast_bce_year = -hr_bce_year + 1
        hr_ce_year = self.random_ce_year()
        assert self.gregorian_cdt.hr_to_ast(1, 1) == 1
        assert self.gregorian_cdt.hr_to_ast(1, 0) == 0
        assert self.gregorian_cdt.hr_to_ast(2, 0) == -1
        assert self.gregorian_cdt.hr_to_ast(hr_bce_year, 0) == ast_bce_year
        assert self.gregorian_cdt.hr_to_ast(hr_ce_year, 1) == hr_ce_year

    def test_ast_to_hr(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        assert self.gregorian_cdt.ast_to_hr(1) == (1, 1)
        assert self.gregorian_cdt.ast_to_hr(0) == (1, 0)
        assert self.gregorian_cdt.ast_to_hr(-1) == (2, 0)
        assert self.gregorian_cdt.ast_to_hr(ast_bce_year) == (hr_bce_year, 0)
        assert self.gregorian_cdt.ast_to_hr(ast_ce_year) == (ast_ce_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_bce_year = self.random_bce_year()
        hr_bce_year = abs(ast_bce_year - 1)
        ast_ce_year = self.random_ce_year()
        hr_ce_year = ast_ce_year
        assert (
            self.gregorian_cdt.hr_to_ast(
                *self.gregorian_cdt.ast_to_hr(ast_bce_year)
            )
            == ast_bce_year
        )
        assert (
            self.gregorian_cdt.hr_to_ast(
                *self.gregorian_cdt.ast_to_hr(ast_ce_year)
            )
            == ast_ce_year
        )
        assert self.gregorian_cdt.ast_to_hr(
            self.gregorian_cdt.hr_to_ast(hr_bce_year, 0)
        ) == (hr_bce_year, 0)
        assert self.gregorian_cdt.ast_to_hr(
            self.gregorian_cdt.hr_to_ast(hr_ce_year, 1)
        ) == (hr_ce_year, 1)

    @patch("src.datetimes.ConvertibleDateTime.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ce_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.gregorian_cdt.ast_to_hr(ast_ce_year)

    def test_parse_hr_date(self):
        ce_ymd = self.random_ce_ymd()
        ce_ast_year, ce_month, ce_day = ce_ymd
        ce_hr_year = ce_ast_year

        bce_ymd = self.random_bce_ymd()
        bce_ast_year, bce_month, bce_day = bce_ymd
        bce_hr_year = abs(bce_ast_year - 1)

        ce_hr_date = self.gregorian_cdt.date_sep.join(
            [str(ce_hr_year), str(ce_month), str(ce_day), "CE"]
        )
        bce_hr_date = self.gregorian_cdt.date_sep.join(
            [str(bce_hr_year), str(bce_month), str(bce_day), "BCE"]
        )
        assert self.gregorian_cdt.parse_hr_date(ce_hr_date) == ce_ymd
        assert self.gregorian_cdt.parse_hr_date(bce_hr_date) == bce_ymd

    def test_format_hr_date(self):
        bce_ast_ymd = self.random_bce_ymd()
        bce_ast_year, bce_month, bce_day = bce_ast_ymd
        bce_hr_year = abs(bce_ast_year - 1)
        bce_hr_date = self.gregorian_cdt.date_sep.join(
            [str(bce_hr_year), str(bce_month), str(bce_day), "BCE"]
        )

        ce_ast_ymd = self.random_ce_ymd()
        ce_ast_year, ce_month, ce_day = ce_ast_ymd
        ce_hr_date = self.gregorian_cdt.date_sep.join(
            [str(ce_ast_year), str(ce_month), str(ce_day), "CE"]
        )
        assert self.gregorian_cdt.format_hr_date(bce_ast_ymd) == bce_hr_date
        assert self.gregorian_cdt.format_hr_date(ce_ast_ymd) == ce_hr_date

    #
    # Eras
    #
    def test_era(self):
        bce_year = self.random_bce_year()
        ce_year = self.random_ce_year()
        assert self.gregorian_cdt.era(bce_year) == "BCE"
        assert self.gregorian_cdt.era(ce_year) == "CE"

    def test_is_descending_era(self):
        bce_year = self.random_bce_year()
        ce_year = self.random_ce_year()
        assert self.gregorian_cdt.is_descending_era(bce_year)
        assert self.gregorian_cdt.is_descending_era(ce_year) is False

    #
    # ConvertibleDateTime.is_leap_year
    #
    def test_is_leap_year(self):
        common_bce_year = self.random_common_bce_year()
        common_ce_year = self.random_common_ce_year()
        leap_bce_year = self.random_leap_bce_year()
        leap_ce_year = self.random_leap_ce_year()
        assert self.gregorian_cdt.is_leap_year(common_bce_year) is False
        assert self.gregorian_cdt.is_leap_year(common_ce_year) is False
        assert self.gregorian_cdt.is_leap_year(leap_bce_year) is True
        assert self.gregorian_cdt.is_leap_year(leap_ce_year) is True

    #
    # ConvertibleDateTime.is_valid_ast_ymd
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        ast_year, month, day = self.random_common_ymd()
        assert self.gregorian_cdt.is_valid_ast_ymd((ast_year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=366)
    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    @patch(
        "src.datetimes.ConvertibleDateTime.days_in_months",
        return_value=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        ast_year, month, day = self.random_leap_ymd()
        assert self.gregorian_cdt.is_valid_ast_ymd((ast_year, month, day))

    @patch("src.datetimes.ConvertibleDateTime.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        assert not self.gregorian_cdt.is_valid_ast_ymd((year, bad_month, day))
        assert not self.gregorian_cdt.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDateTime.is_valid_ordinal_date
    #
    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        valid_ordinal_date = ordinal.from_gregorian(*self.random_common_ymd())
        invalid_ordinal_date = (FAKE.random_int(), FAKE.random_int(min=366))
        assert self.gregorian_cdt.is_valid_ordinal_date(valid_ordinal_date)
        assert not self.gregorian_cdt.is_valid_ordinal_date(
            invalid_ordinal_date
        )

    @patch("src.datetimes.ConvertibleDateTime.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        valid_ordinal_date = ordinal.from_gregorian(*self.random_leap_ymd())
        invalid_ordinal_date = (FAKE.random_int(), FAKE.random_int(min=367))
        assert self.gregorian_cdt.is_valid_ordinal_date(valid_ordinal_date)
        assert not self.gregorian_cdt.is_valid_ordinal_date(
            invalid_ordinal_date
        )

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
            self.gregorian_cdt.days_in_months(common_year)
            # fmt: off
            == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # fmt: on
        )

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.gregorian_cdt.days_in_months(leap_year)
            # fmt: off
            == [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
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
        assert self.gregorian_cdt.days_in_year(common_year) == 365

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.gregorian_cdt.days_in_year(leap_year) == 366

    #
    # ConvertibleDateTime.months_in_year
    #
    @patch(
        "src.datetimes.ConvertibleDateTime.is_leap_year", return_value=False
    )
    def test_months_in_common_year(self, _):
        common_ast_year = self.random_common_year()
        assert self.gregorian_cdt.months_in_year(common_ast_year) == 12

    @patch("src.datetimes.ConvertibleDateTime.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_ast_year = self.random_leap_year()
        assert self.gregorian_cdt.months_in_year(leap_ast_year) == 12

    #
    # Weeks
    #
    """def test_shift_n_weekdays(self):  # todo uncomment when ready to test
        src_datetime = FAKE.date_time_ad()
        src_ordinal = src_datetime.toordinal()
        weeks_to_skip = FAKE.random_int(min=-52, max=52)
        new_datetime = src_datetime + timedelta(weeks=weeks_to_skip)
        new_weekday = new_datetime.weekday()
        assert self.gregorian_cdt.shift_n_weekdays(
            src_ordinal, new_weekday, weeks_to_skip
        ) == new_datetime.toordinal()
        assert self.gregorian_cdt.shift_n_weekdays(
            0, 3, 0  # Thursday before Sunday December 31st 1 BCE
        ) == -3"""

    @patch("src.datetimes.ConvertibleDateTime.days_in_week", return_value=7)
    def test_day_of_week(self, _):
        daycount = self.gregorian_dc
        bce_year, bce_month, bce_day = self.random_bce_ymd()
        bce_julian_day = gregorian.to_jd(bce_year, bce_month, bce_day)
        bce_ordinal = daycount.from_gregorian(bce_year, bce_month, bce_day) + 1

        ce_year, ce_month, ce_day = self.random_ce_ymd()
        ce_julian_day = gregorian.to_jd(ce_year, ce_month, ce_day)
        ce_ordinal = daycount.from_gregorian(ce_year, ce_month, ce_day) + 1
        assert self.gregorian_cdt.day_of_week(1) == 0  # 1/1/1/CE is a Monday
        assert self.gregorian_cdt.day_of_week(2) == 1  # Tuesday
        assert self.gregorian_cdt.day_of_week(3) == 2  # Wednesday
        assert self.gregorian_cdt.day_of_week(4) == 3  # Thursday
        assert self.gregorian_cdt.day_of_week(5) == 4  # Friday
        assert self.gregorian_cdt.day_of_week(6) == 5  # Saturday
        assert self.gregorian_cdt.day_of_week(7) == 6  # Sunday
        assert self.gregorian_cdt.day_of_week(8) == 0  # Monday
        assert self.gregorian_cdt.day_of_week(bce_ordinal) == utils.jwday(
            bce_julian_day
        )
        assert self.gregorian_cdt.day_of_week(ce_ordinal) == utils.jwday(
            ce_julian_day
        )

    def test_days_in_week(self):
        assert self.gregorian_cdt.days_in_week() == 7
