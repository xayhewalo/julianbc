import convertdate
import pytest

from .utils import RealCalendarTestCase, FAKE
from calendar import isleap
from collections import deque
from src.customdate import DateUnit
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
        # fmt: off
        self.common_ordinals = (
            78, 79, 81, 82, 83, 85, 86, 87, 89, 90, 91, 93, 94, 95, 97, 98, 99,
            100, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114, 115,
            117, 118, 119, 121, 122, 123, 125, 126, 127, 129, 130, 131, 133,
            134, 135, 137, 138, 139, 141, 142, 143, 145, 146, 147, 149, 150,
            151, 153, 154, 155, 157, 158, 159, 161, 162, 163, 165, 166, 167,
            169, 170, 171, 173, 174, 175, 177, 178, 179, 181, 182, 183, 185,
            186, 187, 189, 190, 191, 193, 194, 195, 197, 198, 199, 200, 201,
            202, 203, 205, 206, 207, 209, 210, 211, 213, 214, 215, 217, 218,
            219, 221, 222, 223, 225, 226, 227, 229, 230, 231, 233, 234, 235,
            237, 238, 239, 241, 242, 243, 245, 246, 247, 249, 250, 251, 253,
            254, 255, 257, 258, 259, 261, 262, 263, 265, 266, 267, 269, 270,
            271, 273, 274, 275, 277, 278, 279, 281, 282, 283, 285, 286, 287,
            289, 290, 291, 293, 294, 295, 297, 298, 299, 300, 301, 302, 303,
            305, 306, 307, 309, 310, 311, 313, 314, 315, 317, 318, 319, 321,
            322, 323, 325, 326, 327, 329, 330, 331, 333, 334, 335, 337, 338,
            339, 341, 342, 343, 345, 346, 347, 349, 350, 351, 353, 354, 355,
            357, 358, 359, 361, 362, 363, 365, 366, 367, 369, 370, 371, 373,
            374, 375, 377, 378, 379, 381, 382, 383, 385, 386, 387, 389, 390,
            391, 393, 394, 395, 397, 398, 399, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13,
            14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 33, 34, 35,
            37, 38, 39, 41, 42, 43, 45, 46, 47, 49, 50, 51, 53, 54, 55, 57, 58,
            59, 61, 62, 63, 65, 66, 67, 69, 70, 71, 73, 74, 75, 77,
        )
        # fmt: on
        self.cycle_length = 400
        self.all_cycle_ordinals = deque(range(1, 401))
        self.all_cycle_ordinals.rotate(self.indian.leap_year_offset)
        self.leap_years_in_normal_cycle = 97
        self.common_years_in_normal_cycle = 303
        self.days_in_leap_years = 366
        self.days_in_common_year = 365

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

    def ordinal_conversion_patches(self, *args):
        patch_days_common_year = args[0]
        patch_days_in_leap_year = args[1]
        patch_common_years_in_normal_cycle = args[2]
        patch_leap_years_in_normal_cycle = args[3]
        patch_common_year_cycle_ordinals = args[4]
        patch_all_cycle_ordinals = args[5]
        patch_leap_year_cycle_length = args[6]

        patch_leap_year_cycle_length.__get__ = lambda *_: 400
        _all_cycle_ordinals = deque(range(1, 401))
        _all_cycle_ordinals.rotate(self.indian.leap_year_offset)
        patch_all_cycle_ordinals.__get__ = lambda *_: _all_cycle_ordinals
        # fmt: off
        _common_ordinals = (
            78, 79, 81, 82, 83, 85, 86, 87, 89, 90, 91, 93, 94, 95, 97, 98, 99,
            100, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114, 115,
            117, 118, 119, 121, 122, 123, 125, 126, 127, 129, 130, 131, 133,
            134, 135, 137, 138, 139, 141, 142, 143, 145, 146, 147, 149, 150,
            151, 153, 154, 155, 157, 158, 159, 161, 162, 163, 165, 166, 167,
            169, 170, 171, 173, 174, 175, 177, 178, 179, 181, 182, 183, 185,
            186, 187, 189, 190, 191, 193, 194, 195, 197, 198, 199, 200, 201,
            202, 203, 205, 206, 207, 209, 210, 211, 213, 214, 215, 217, 218,
            219, 221, 222, 223, 225, 226, 227, 229, 230, 231, 233, 234, 235,
            237, 238, 239, 241, 242, 243, 245, 246, 247, 249, 250, 251, 253,
            254, 255, 257, 258, 259, 261, 262, 263, 265, 266, 267, 269, 270,
            271, 273, 274, 275, 277, 278, 279, 281, 282, 283, 285, 286, 287,
            289, 290, 291, 293, 294, 295, 297, 298, 299, 300, 301, 302, 303,
            305, 306, 307, 309, 310, 311, 313, 314, 315, 317, 318, 319, 321,
            322, 323, 325, 326, 327, 329, 330, 331, 333, 334, 335, 337, 338,
            339, 341, 342, 343, 345, 346, 347, 349, 350, 351, 353, 354, 355,
            357, 358, 359, 361, 362, 363, 365, 366, 367, 369, 370, 371, 373,
            374, 375, 377, 378, 379, 381, 382, 383, 385, 386, 387, 389, 390,
            391, 393, 394, 395, 397, 398, 399, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13,
            14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 33, 34, 35,
            37, 38, 39, 41, 42, 43, 45, 46, 47, 49, 50, 51, 53, 54, 55, 57, 58,
            59, 61, 62, 63, 65, 66, 67, 69, 70, 71, 73, 74, 75, 77,
        )
        # fmt: on
        patch_common_year_cycle_ordinals.__get__ = lambda *_: _common_ordinals
        patch_leap_years_in_normal_cycle.__get__ = lambda *_: 97
        patch_common_years_in_normal_cycle.__get__ = lambda *_: 303
        patch_days_in_leap_year.__get__ = lambda *_: 366
        patch_days_common_year.__get__ = lambda *_: 365

    #
    # ConvertibleDate.convert_ast_ymd
    #
    @pytest.mark.db
    def test_convert_coptic_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        coptic_ymd = convertdate.coptic.from_gregorian(*gregorian_ymd)
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cd.convert_ast_ymd((1, 1, 1), self.coptic_cd)
            == (207, 6, 7)
        )
        assert (
            self.indian_cd.convert_ast_ymd((-206, 7, 28), self.coptic_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cd.convert_ast_ymd(coptic_ymd, self.coptic_cd)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_lunar_hijri_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        l_hijri_ymd = convertdate.islamic.from_gregorian(*gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cd.convert_ast_ymd((1, 1, 1), self.l_hijri_cd)
            == (545, 4, 28)
        )
        assert (
            self.indian_cd.convert_ast_ymd((-561, 12, 20), self.l_hijri_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cd.convert_ast_ymd(l_hijri_ymd, self.l_hijri_cd)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_gregorian_ast_ymd(self):
        gregorian_ymd = self.random_convertible_gregorian_ymd()
        indian_ymd = self.make_indian_ast_ymd(gregorian_ymd)
        # fmt: off
        assert (
            self.indian_cd.convert_ast_ymd((1, 1, 1), self.gregorian_cd)
            == (-77, 10, 11)
        )
        assert (
            self.indian_cd.convert_ast_ymd((78, 3, 22), self.gregorian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cd.convert_ast_ymd(gregorian_ymd, self.gregorian_cd)
            == indian_ymd
        )

    @pytest.mark.db
    def test_convert_julian_ast_ymd(self):
        gyear, gmonth, gday = self.random_convertible_gregorian_ymd()
        julian_ymd = convertdate.julian.from_gregorian(gyear, gmonth, gday)
        indian_ymd = self.make_indian_ast_ymd((gyear, gmonth, gday))
        # fmt: off
        assert (
            self.indian_cd.convert_ast_ymd((1, 1, 1), self.julian_cd)
            == (-77, 10, 9)
        )
        assert (
            self.indian_cd.convert_ast_ymd((78, 3, 24), self.julian_cd)
            == (1, 1, 1)
        )
        # fmt: on
        assert (
            self.indian_cd.convert_ast_ymd(julian_ymd, self.julian_cd)
            == indian_ymd
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
    def test_ordinal_date_to_ordinal_for_be_year(self, *_):
        # patching more ordinal stuff rotates all_cycle_ordinals too early for
        # some reason...so don't patch
        assert self.indian_cd.ordinal_date_to_ordinal((0, 365)) == 0
        assert self.indian_cd.ordinal_date_to_ordinal((0, 1)) == -364
        assert self.indian_cd.ordinal_date_to_ordinal((-1, 366)) == -365
        assert self.indian_cd.ordinal_date_to_ordinal((-1, 1)) == -730
        assert self.indian_cd.ordinal_date_to_ordinal((-2, 365)) == -731
        assert self.indian_cd.ordinal_date_to_ordinal((-2, 164)) == -932
        assert self.indian_cd.ordinal_date_to_ordinal((-400, 365)) == -146097
        assert self.indian_cd.ordinal_date_to_ordinal((-400, 1)) == -146461
        assert self.indian_cd.ordinal_date_to_ordinal((-401, 366)) == -146462
        assert self.indian_cd.ordinal_date_to_ordinal((-401, 266)) == -146562

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
    def test_ordinal_date_to_ordinal_for_se_year(self, *args):
        self.ordinal_conversion_patches(*args)

        assert self.indian_cd.ordinal_date_to_ordinal((1, 1)) == 1
        assert self.indian_cd.ordinal_date_to_ordinal((1, 365)) == 365
        assert self.indian_cd.ordinal_date_to_ordinal((2, 1)) == 366
        assert self.indian_cd.ordinal_date_to_ordinal((2, 101)) == 466
        assert self.indian_cd.ordinal_date_to_ordinal((3, 366)) == 1096
        assert self.indian_cd.ordinal_date_to_ordinal((400, 365)) == 146097
        assert self.indian_cd.ordinal_date_to_ordinal((401, 1)) == 146098
        assert self.indian_cd.ordinal_date_to_ordinal((401, 303)) == 146400

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_ordinal_raises(self, _):
        year, month, day = self.random_common_ymd()
        gyear, gmonth, gday = convertdate.indian_civil.to_gregorian(
            year, month, day
        )
        day_of_year = self.indian_dc.from_gregorian(gyear, gmonth, gday)
        with pytest.raises(ValueError):
            self.indian_cd.ordinal_date_to_ordinal((year, day_of_year))

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_for_se_year(self, *_):
        assert self.indian_cd.ordinal_to_ordinal_date(146199) == (401, 102)
        assert self.indian_cd.ordinal_to_ordinal_date(146098) == (401, 1)
        assert self.indian_cd.ordinal_to_ordinal_date(146097) == (400, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(760) == (3, 30)
        assert self.indian_cd.ordinal_to_ordinal_date(731) == (3, 1)
        assert self.indian_cd.ordinal_to_ordinal_date(366) == (2, 1)
        assert self.indian_cd.ordinal_to_ordinal_date(365) == (1, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(1) == (1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_be_year(self, *_):
        assert self.indian_cd.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(-364) == (0, 1)
        assert self.indian_cd.ordinal_to_ordinal_date(-365) == (-1, 366)
        assert self.indian_cd.ordinal_to_ordinal_date(-731) == (-2, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(-808) == (-2, 288)
        assert self.indian_cd.ordinal_to_ordinal_date(-146097) == (-400, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(-146461) == (-400, 1)
        assert self.indian_cd.ordinal_to_ordinal_date(-146462) == (-401, 366)
        assert self.indian_cd.ordinal_to_ordinal_date(-146762) == (-401, 66)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_for_last_proleptic_year(self, *_):
        assert self.indian_cd.ordinal_to_ordinal_date(0) == (0, 365)
        assert self.indian_cd.ordinal_to_ordinal_date(-60) == (0, 305)
        assert self.indian_cd.ordinal_to_ordinal_date(-100) == (0, 265)
        assert self.indian_cd.ordinal_to_ordinal_date(-200) == (0, 165)
        assert self.indian_cd.ordinal_to_ordinal_date(-300) == (0, 65)
        assert self.indian_cd.ordinal_to_ordinal_date(-364) == (0, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    # don't patch _start_and_sign, loops can temporarily move into diff era
    def test_ordinal_to_ordinal_date_is_reversible_for_be_year(self, *_):
        be_ordinal = FAKE.random_int(min=-9999, max=0)
        be_ordinal_date = (
            FAKE.random_int(min=-9999, max=0),
            FAKE.random_int(min=1, max=365),
        )
        assert (
            self.indian_cd.ordinal_to_ordinal_date(
                self.indian_cd.ordinal_date_to_ordinal(be_ordinal_date)
            )
            == be_ordinal_date
        )
        assert (
            self.indian_cd.ordinal_date_to_ordinal(
                self.indian_cd.ordinal_to_ordinal_date(be_ordinal)
            )
            == be_ordinal
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_ordinal_to_ordinal_date_is_reversible_for_se_year(self, *_):
        se_ordinal = FAKE.random_int()
        se_ordinal_date = FAKE.random_int(), FAKE.random_int(min=1, max=365)
        assert (
            self.indian_cd.ordinal_to_ordinal_date(
                self.indian_cd.ordinal_date_to_ordinal(se_ordinal_date)
            )
            == se_ordinal_date
        )
        assert (
            self.indian_cd.ordinal_date_to_ordinal(
                self.indian_cd.ordinal_to_ordinal_date(se_ordinal)
            )
            == se_ordinal
        )

    #
    # Cycle methods
    #
    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_completed_cycles_for_se_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(completed_cycles)
        end_year = self.make_cycle_end_year(completed_cycles)
        cycle_year = FAKE.random_int(min=start_year, max=end_year)
        assert self.indian_cd.completed_cycles(1) == 0
        assert self.indian_cd.completed_cycles(400) == 0
        assert self.indian_cd.completed_cycles(401) == 1
        assert self.indian_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_completed_cycles_for_be_year(self, _):
        completed_cycles = FAKE.random_int()
        start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        end_year = self.make_cycle_end_year(completed_cycles, proleptic=True)
        cycle_year = FAKE.random_int(min=end_year, max=start_year)
        assert self.indian_cd.completed_cycles(0) == 0
        assert self.indian_cd.completed_cycles(-399) == 0
        assert self.indian_cd.completed_cycles(-400) == 1
        assert self.indian_cd.completed_cycles(cycle_year) == completed_cycles

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(1, 1),
    )
    def test_cycle_index_for_se_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        se_start_year = self.make_cycle_start_year(completed_cycles)
        se_year = se_start_year + cycle_index
        assert self.indian_cd.cycle_index(1) == 0
        assert self.indian_cd.cycle_index(100) == 99
        assert self.indian_cd.cycle_index(200) == 199
        assert self.indian_cd.cycle_index(300) == 299
        assert self.indian_cd.cycle_index(400) == 399
        assert self.indian_cd.cycle_index(401) == 0
        assert (
            self.indian_cd.cycle_index(se_year, completed_cycles, 1, 1)
            == cycle_index
        )

    @patch(
        "src.customdate.ConvertibleDate._start_and_sign",
        return_value=(0, -1),
    )
    def test_cycle_index_for_be_year(self, _):
        completed_cycles = FAKE.random_int()
        cycle_index = FAKE.random_int(max=self.cycle_length)
        be_start_year = self.make_cycle_start_year(
            completed_cycles, proleptic=True
        )
        be_year = be_start_year - cycle_index
        assert self.indian_cd.cycle_index(-400) == 0
        assert self.indian_cd.cycle_index(-399) == 399
        assert self.indian_cd.cycle_index(-300) == 300
        assert self.indian_cd.cycle_index(-200) == 200
        assert self.indian_cd.cycle_index(-100) == 100
        assert self.indian_cd.cycle_index(0) == 0
        assert (
            self.indian_cd.cycle_index(be_year, completed_cycles, 0, -1)
            == cycle_index
        )

    def test_all_cycle_ordinals(self):
        assert self.indian_cd.all_cycle_ordinals == self.all_cycle_ordinals
        with pytest.raises(AttributeError):
            self.indian_cd.all_cycle_ordinals = FAKE.pylist()

    @patch("src.customdate.ConvertibleDate.common_years_in_normal_cycle")
    def test_days_in_normal_cycle(self, p_common_years_in_normal_cycle):
        cyinc = self.common_years_in_normal_cycle
        p_common_years_in_normal_cycle.__get__ = lambda *_: cyinc

        days_in_normal_cycle = self.indian_dc.from_gregorian(
            *convertdate.indian_civil.to_gregorian(400, 1, 1)
        )
        assert self.indian_cd.days_in_normal_cycle == days_in_normal_cycle
        with pytest.raises(AttributeError):
            self.indian_cd.days_in_normal_cycle = FAKE.random_int()

    @patch("src.customdate.ConvertibleDate.all_cycle_ordinals")
    def test_common_year_cycle_ordinals(self, patch_all_cycle_ordinals):
        patch_all_cycle_ordinals.__get__ = lambda *_: self.all_cycle_ordinals
        common_ords = tuple(self.common_ordinals)
        assert self.indian_cd.common_year_cycle_ordinals == common_ords
        with pytest.raises(AttributeError):
            self.indian_cd.common_year_cycle_ordinals = FAKE.pytuple()

    @patch("src.customdate.ConvertibleDate.common_year_cycle_ordinals")
    def test_common_years_in_normal_cycle(self, p_common_year_cycle_ordinals):
        p_common_year_cycle_ordinals.__get__ = lambda *_: self.common_ordinals
        cyinc = self.common_years_in_normal_cycle
        assert self.indian_cd.common_years_in_normal_cycle == cyinc
        with pytest.raises(AttributeError):
            self.indian_cd.common_years_in_normal_cycle = FAKE.random_int()

    def test_special_years(self):
        ast_year = FAKE.random_int(min=-9999)
        assert self.indian_cd.net_elapsed_special_years(ast_year) == (0, 0)

    #
    # ConvertibleDate.ast_ymd_to_ordinal_date
    #
    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ast_ymd_to_ordinal_date_for_common_year(self, *_):
        indian_cdt = self.indian_cd
        assert indian_cdt.ast_ymd_to_ordinal_date((1, 1, 1)) == (1, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((2, 12, 30)) == (2, 365)
        assert indian_cdt.ast_ymd_to_ordinal_date((178, 5, 4)) == (178, 127)
        assert indian_cdt.ast_ymd_to_ordinal_date((0, 12, 30)) == (0, 365)
        assert indian_cdt.ast_ymd_to_ordinal_date((-2, 1, 1)) == (-2, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((-66, 8, 7)) == (-66, 222)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=True,
    )
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ast_ymd_to_ordinal_date_for_leap_year(self, *_):
        indian_cdt = self.indian_cd
        assert indian_cdt.ast_ymd_to_ordinal_date((3, 1, 1)) == (3, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((7, 12, 30)) == (7, 366)
        assert indian_cdt.ast_ymd_to_ordinal_date((15, 10, 17)) == (15, 293)
        assert indian_cdt.ast_ymd_to_ordinal_date((-1, 1, 1)) == (-1, 1)
        assert indian_cdt.ast_ymd_to_ordinal_date((-73, 12, 30)) == (-73, 366)
        assert indian_cdt.ast_ymd_to_ordinal_date((-38, 7, 22)) == (-38, 208)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ast_ymd",
        return_value=False,
    )
    def test_ast_ymd_to_ordinal_date_raises(self, _):
        with pytest.raises(ValueError):
            self.indian_cd.ast_ymd_to_ordinal_date(self.random_ymd())

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
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_for_common_year(self, *_):
        indian_cdt = self.indian_cd
        assert indian_cdt.ordinal_date_to_ast_ymd((1, 1)) == (1, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((13, 107)) == (13, 4, 15)
        assert indian_cdt.ordinal_date_to_ast_ymd((55, 365)) == (55, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((0, 365)) == (0, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-25, 335)) == (-25, 11, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-111, 1)) == (-111, 1, 1)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_for_leap_year(self, *_):
        indian_cdt = self.indian_cd
        assert indian_cdt.ordinal_date_to_ast_ymd((3, 1)) == (3, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((323, 31)) == (323, 1, 31)
        assert indian_cdt.ordinal_date_to_ast_ymd((43, 366)) == (43, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-1, 366)) == (-1, 12, 30)
        assert indian_cdt.ordinal_date_to_ast_ymd((-5, 1)) == (-5, 1, 1)
        assert indian_cdt.ordinal_date_to_ast_ymd((-37, 82)) == (-37, 3, 20)

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=True,
    )
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_common_year(self, *_):
        common_year, month, day = self.random_common_ymd()
        ordinal_date = common_year, FAKE.random_int(min=1, max=365)
        ast_ymd = common_year, month, day
        assert (
            self.indian_cd.ordinal_date_to_ast_ymd(
                self.indian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.indian_cd.ast_ymd_to_ordinal_date(
                self.indian_cd.ordinal_date_to_ast_ymd(ordinal_date)
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
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_ordinal_date_to_ast_ymd_is_reversible_for_leap_year(self, *_):
        leap_year, month, day = self.random_leap_ymd()
        ordinal_date = leap_year, FAKE.random_int(min=1, max=366)
        ast_ymd = leap_year, month, day
        assert (
            self.indian_cd.ordinal_date_to_ast_ymd(
                self.indian_cd.ast_ymd_to_ordinal_date(ast_ymd)
            )
            == ast_ymd
        )
        assert (
            self.indian_cd.ast_ymd_to_ordinal_date(
                self.indian_cd.ordinal_date_to_ast_ymd(ordinal_date)
            )
            == ordinal_date
        )

    @patch(
        "src.customdate.ConvertibleDate.is_valid_ordinal_date",
        return_value=False,
    )
    def test_ordinal_date_to_ast_ymd_can_raise(self, _):
        with pytest.raises(ValueError):
            self.indian_cd.ordinal_date_to_ast_ymd((1, 0))

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
        assert self.indian_cd.shift_ast_ymd(ymd, zero_interval) == ymd
        # fmt: off
        assert self.indian_cd.shift_ast_ymd(
            (ast_year, 2, 3), plus_years
        ) == (ast_year + plus_delta, 2, 3)
        assert self.indian_cd.shift_ast_ymd(
            (ast_year, 1, 30), plus_months
        ) == (ast_year, 1 + plus_delta, 30)
        # fmt: on
        assert self.indian_cd.shift_ast_ymd(
            (ast_year, 7, 15), [[10, DateUnit.YEAR], [5, DateUnit.MONTH]]
        ) == (ast_year + 10, 12, 15)
        assert self.indian_cd.shift_ast_ymd(
            (ast_year, 9, 25), [[-7, DateUnit.YEAR], [2, DateUnit.MONTH]]
        ) == (ast_year - 7, 11, 25)

    def test_shift_ast_ymd_to_invalid_day(self):
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.indian_cd.shift_ast_ymd(
            (common_year, 6, 31), [[1, DateUnit.MONTH]]
        ) == (common_year, 7, 30)
        assert self.indian_cd.shift_ast_ymd(
            (leap_year, 1, 31), [[6, DateUnit.MONTH]]
        ) == (leap_year, 7, 30)
        assert self.indian_cd.shift_ast_ymd(
            (2, 2, 31), [[-1, DateUnit.MONTH]]
        ) == (2, 1, 30)
        assert self.indian_cd.shift_ast_ymd(
            (leap_year, 1, 31), [[-1, DateUnit.MONTH]]
        ) == (leap_year - 1, 12, 30)

    def test_shift_ast_year(self):
        delta = FAKE.random_int()
        year = self.random_year()
        expected_year = year + delta
        assert self.indian_cd.shift_ast_year(year, delta) == expected_year

    def test_shift_month(self):
        year, month, _ = self.random_ymd()
        assert self.indian_cd.shift_month(year, month, -24) == (
            year - 2,
            month,
        )
        assert self.indian_cd.shift_month(year, month, -12) == (
            year - 1,
            month,
        )
        assert self.indian_cd.shift_month(year, month, 0) == (year, month)
        assert self.indian_cd.shift_month(year, month, 12) == (
            year + 1,
            month,
        )
        assert self.indian_cd.shift_month(year, month, 24) == (
            year + 2,
            month,
        )
        assert self.indian_cd.shift_month(year, 2, 3) == (year, 5)
        assert self.indian_cd.shift_month(year, 12, 1) == (year + 1, 1)
        assert self.indian_cd.shift_month(year, 8, 7) == (year + 1, 3)
        assert self.indian_cd.shift_month(year, 3, 14) == (year + 1, 5)
        assert self.indian_cd.shift_month(year, 6, 29) == (year + 2, 11)
        assert self.indian_cd.shift_month(year, 10, -1) == (year, 9)
        assert self.indian_cd.shift_month(year, 1, -1) == (year - 1, 12)
        assert self.indian_cd.shift_month(year, 2, -3) == (year - 1, 11)
        assert self.indian_cd.shift_month(year, 5, -7) == (year - 1, 10)
        assert self.indian_cd.shift_month(year, 7, -15) == (year - 1, 4)
        assert self.indian_cd.shift_month(year, 12, -28) == (year - 2, 8)

    #
    # Next DateUnit
    #

    # ConvertibleDate.next_ast_ymd tested in test_customdate
    # ConvertibleDate.next_era tested in test_customdate
    # ConvertibleDate.next_ast_year tested in test_customdate

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_month_moving_forward(self, _):
        assert self.indian_cd.next_month(121, 4, 3, True) == (121, 6, 1)
        assert self.indian_cd.next_month(65, 11, 4, True) == (65, 12, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_month_moving_backward(self, _):
        assert self.indian_cd.next_month(41, 3, 2, False) == (41, 2, 1)
        assert self.indian_cd.next_month(450, 12, 5, False) == (450, 10, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test_next_day_moving_forward(self, _):
        assert self.indian_cd.next_day((230, 4, 4), 5, True) == (230, 4, 5)
        assert self.indian_cd.next_day((411, 12, 1), 10, True) == (411, 12, 10)
        assert self.indian_cd.next_day((3, 1, 30), 1, True) == (3, 1, 31)
        assert self.indian_cd.next_day((2, 1, 30), 1, True) == (2, 2, 1)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test_next_day_moving_backward(self, _):
        assert self.indian_cd.next_day((23, 10, 10), 2, False) == (23, 10, 8)
        assert self.indian_cd.next_day((4, 1, 22), 4, False) == (4, 1, 20)
        assert self.indian_cd.next_day((3, 2, 1), 1, False) == (3, 1, 31)
        assert self.indian_cd.next_day((2, 2, 1), 1, False) == (2, 1, 30)

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=1)
    def test__overflow_month_moving_forward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.indian_cd._overflow_month(year, month) == (year, month)
        assert self.indian_cd._overflow_month(common_year, 13, True) == (
            common_year + 1,
            1,
        )
        assert self.indian_cd._overflow_month(leap_year, 13, True) == (
            leap_year + 1,
            1,
        )

    @patch("src.customdate.ConvertibleDate._get_delta", return_value=-1)
    def test__overflow_month_moving_backward(self, _):
        year, month, _ = self.random_ymd()
        common_year = self.random_common_year()
        leap_year = self.random_leap_year()
        assert self.indian_cd._overflow_month(year, month) == (year, month)
        assert self.indian_cd._overflow_month(common_year, 0, False) == (
            common_year - 1,
            12,
        )
        assert self.indian_cd._overflow_month(leap_year, 0, False) == (
            leap_year - 1,
            12,
        )

    # test ConvertibleDate._get_delta() in test_customdate.py

    #
    # Human-readable years
    #
    def test_hr_to_ast(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = ast_se_year - 1
        assert self.indian_cd.hr_to_ast(0, 1) == 1
        assert self.indian_cd.hr_to_ast(1, 0) == 0
        assert self.indian_cd.hr_to_ast(2, 0) == -1
        assert self.indian_cd.hr_to_ast(hr_be_year, 0) == ast_be_year
        assert self.indian_cd.hr_to_ast(hr_se_year, 1) == ast_se_year

    def test_ast_to_hr(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = abs(ast_se_year - 1)
        assert self.indian_cd.ast_to_hr(1) == (0, 1)
        assert self.indian_cd.ast_to_hr(0) == (1, 0)
        assert self.indian_cd.ast_to_hr(-1) == (2, 0)
        assert self.indian_cd.ast_to_hr(ast_be_year) == (hr_be_year, 0)
        assert self.indian_cd.ast_to_hr(ast_se_year) == (hr_se_year, 1)

    def test_ast_to_hr_and_hr_to_ast_are_reversible(self):
        ast_be_year = self.random_bce_year()
        hr_be_year = abs(ast_be_year - 1)
        ast_se_year = self.random_ce_year()
        hr_se_year = ast_se_year - 1
        assert (
            self.indian_cd.hr_to_ast(*self.indian_cd.ast_to_hr(ast_be_year))
            == ast_be_year
        )
        assert (
            self.indian_cd.hr_to_ast(*self.indian_cd.ast_to_hr(ast_se_year))
            == ast_se_year
        )
        assert self.indian_cd.ast_to_hr(
            self.indian_cd.hr_to_ast(hr_be_year, 0)
        ) == (hr_be_year, 0)
        assert self.indian_cd.ast_to_hr(
            self.indian_cd.hr_to_ast(hr_se_year, 1)
        ) == (hr_se_year, 1)

    @patch("src.customdate.ConvertibleDate.gen_years_before_era")
    def test_ast_to_hr_raise(self, _):
        ast_ah_year = self.random_ce_year()
        with pytest.raises(RuntimeError):
            self.l_hijri_cd.ast_to_hr(ast_ah_year)

    def test_parse_hr_date(self):
        se_ymd = self.random_ce_ymd()
        se_ast_year, se_month, se_day = se_ymd
        se_hr_year = se_ast_year - 1

        be_ymd = self.random_bce_ymd()
        be_ast_year, be_month, be_day = be_ymd
        be_hr_year = abs(be_ast_year - 1)

        se_hr_date = self.indian_cd.date_sep.join(
            [str(se_hr_year), str(se_month), str(se_day), "एस ई"]
        )
        be_hr_date = self.indian_cd.date_sep.join(
            [str(be_hr_year), str(be_month), str(be_day), "बी ई"]
        )
        assert self.indian_cd.parse_hr_date(se_hr_date) == se_ymd
        assert self.indian_cd.parse_hr_date(be_hr_date) == be_ymd

    def test_format_hr_date(self):
        be_ast_ymd = self.random_bce_ymd()
        be_ast_year, be_month, be_day = be_ast_ymd
        be_hr_year = abs(be_ast_year - 1)
        be_hr_date = self.indian_cd.date_sep.join(
            [str(be_hr_year), str(be_month), str(be_day), "बी ई"]
        )

        se_ast_ymd = self.random_ce_ymd()
        se_ast_year, se_month, se_day = se_ast_ymd
        se_hr_year = se_ast_year - 1
        se_hr_date = self.indian_cd.date_sep.join(
            [str(se_hr_year), str(se_month), str(se_day), "एस ई"]
        )
        assert self.indian_cd.format_hr_date(be_ast_ymd) == be_hr_date
        assert self.indian_cd.format_hr_date(se_ast_ymd) == se_hr_date

    #
    # ConvertibleDate.era
    #
    def test_era(self):
        be_year = self.random_bce_year()
        se_year = self.random_ce_year()
        assert self.indian_cd.era(be_year) == "बी ई"
        assert self.indian_cd.era(se_year) == "एस ई"

    #
    # ConvertibleDate.is_leap_year
    #
    def test_is_leap_year(self):
        # all_cycle_ordinals reverses to early when patched...so don't patch
        common_be_year = self.random_common_bce_year()
        common_se_year = self.random_common_ce_year()
        leap_be_year = self.random_leap_bce_year()
        leap_se_year = self.random_leap_ce_year()
        assert self.indian_cd.is_leap_year(0) is False
        assert self.indian_cd.is_leap_year(common_be_year) is False
        assert self.indian_cd.is_leap_year(common_se_year) is False
        assert self.indian_cd.is_leap_year(3)
        assert self.indian_cd.is_leap_year(leap_be_year)
        assert self.indian_cd.is_leap_year(leap_se_year)

    #
    # ConvertibleDate.is_valid_ast_ymd
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_is_valid_ast_ymd_for_valid_common_ast_ymd(self, *_):
        year, month, day = self.random_common_ymd()
        assert self.indian_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_is_valid_ast_ymd_for_valid_leap_ast_ymd(self, *_):
        year, month, day = self.random_leap_ymd()
        assert self.indian_cd.is_valid_ast_ymd((year, month, day))

    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_ast_ymd_for_invalid_ast_ymd(self, _):
        year, month, day = self.random_ymd()
        bad_month = FAKE.random_int(min=13)
        bad_day = FAKE.random_int(min=32)
        indian_cdt = self.indian_cd
        assert not indian_cdt.is_valid_ast_ymd((year, bad_month, day))
        assert not indian_cdt.is_valid_ast_ymd((year, month, bad_day))

    #
    # ConvertibleDate.is_valid_month
    #
    @patch("src.customdate.ConvertibleDate.months_in_year", return_value=12)
    def test_is_valid_month(self, _):
        year, month, _ = self.random_ymd()
        negative_month = FAKE.random_int(min=-9999, max=-1)
        too_big_month = FAKE.random_int(min=13)
        assert self.indian_cd.is_valid_month(year, month)
        assert self.indian_cd.is_valid_month(year, negative_month) is False
        assert self.indian_cd.is_valid_month(year, too_big_month) is False

    #
    # ConvertibleDate.is_valid_ordinal_date
    #
    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=365)
    def test_is_valid_ordinal_date_for_common_year(self, _):
        year = self.random_common_year()
        valid_day_of_year = FAKE.random_int(min=1, max=365)
        bad_day_of_year = FAKE.random_int(min=366)
        indian_cdt = self.indian_cd
        assert not indian_cdt.is_valid_ordinal_date((1, 366))
        assert indian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not indian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    @patch("src.customdate.ConvertibleDate.days_in_year", return_value=366)
    def test_is_valid_ordinal_date_for_leap_year(self, _):
        year = self.random_leap_year()
        valid_day_of_year = FAKE.random_int(min=1, max=366)
        bad_day_of_year = FAKE.random_int(min=367)
        indian_cdt = self.indian_cd
        assert not indian_cdt.is_valid_ordinal_date((1, 367))
        assert indian_cdt.is_valid_ordinal_date((year, valid_day_of_year))
        assert not indian_cdt.is_valid_ordinal_date((year, bad_day_of_year))

    # skip ConvertibleDate.gen_years_before_era, not applicable

    #
    # ConvertibleDate.days_in_months
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_months_for_common_year(self, _):
        common_year = self.random_common_year()
        assert (
            self.indian_cd.days_in_months(common_year)
            # fmt: off
            == [30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30]
            # fmt: on
        )

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_months_for_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert (
            self.indian_cd.days_in_months(leap_year)
            # fmt: off
            == [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30]
            # fmt: on
        )

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(30, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_days_in_month_for_common_month(self, _):
        common_year, month, _ = self.random_common_ymd()
        assert self.indian_cd.days_in_month(
            common_year, month
        ) == convertdate.indian_civil.month_length(common_year, month)

    #
    # ConvertibleDate.days_in_month
    #
    @patch(
        "src.customdate.ConvertibleDate.days_in_months",
        return_value=(31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30),
    )
    def test_days_in_month_for_leap_month(self, _):
        leap_year, month, _ = self.random_leap_ymd()
        hr_leap_year = leap_year - 1
        assert self.indian_cd.days_in_month(
            leap_year, month
        ) == convertdate.indian_civil.month_length(hr_leap_year, month)

    #
    # ConvertibleDate.days_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_days_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.indian_cd.days_in_year(common_year) == 365

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_days_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.indian_cd.days_in_year(leap_year) == 366

    #
    # ConvertibleDate.months_in_year
    #
    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=False)
    def test_months_in_common_year(self, _):
        common_year = self.random_common_year()
        assert self.indian_cd.months_in_year(common_year) == 12

    @patch("src.customdate.ConvertibleDate.is_leap_year", return_value=True)
    def test_months_in_leap_year(self, _):
        leap_year = self.random_leap_year()
        assert self.indian_cd.months_in_year(leap_year) == 12

    #
    # Weeks
    #
    @patch("src.db.ConvertibleCalendar.days_in_weeks", return_value=7)
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
        assert self.indian_cd.day_of_week(1) == 2  # 0/1/1 is the third day
        assert self.indian_cd.day_of_week(2) == 3
        assert self.indian_cd.day_of_week(3) == 4
        assert self.indian_cd.day_of_week(4) == 5
        assert self.indian_cd.day_of_week(5) == 6
        assert self.indian_cd.day_of_week(6) == 0
        assert self.indian_cd.day_of_week(7) == 1
        assert self.indian_cd.day_of_week(8) == 2
        assert (
            self.indian_cd.day_of_week(be_ordinal) == (be_julian_day + 1.5) % 7
        )
        assert (
            self.indian_cd.day_of_week(se_ordinal) == (se_julian_day + 1.5) % 7
        )
