import copy
import itertools
import pytest

from src.db.eon.customcalendar import (
    ConvertibleCalendar,
    CalendarConversion,
    default_eras,
    default_era_ranges,
)
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.factories import (
    CalendarConversionFactory,
    ConvertibleCalendarFactory,
)
from tests.utils import CalendarTestCase, FAKE
from unittest.mock import patch


def test_default_eras():
    assert default_eras() == ["BCE", "CE"]


def test_default_era_ranges():
    assert default_era_ranges() == [["-inf", 1], [1, "inf"]]


@pytest.mark.db
def test_convertible_calendar_factory():
    # noinspection PyBroadException
    try:
        ConvertibleCalendarFactory()
    except Exception:
        assert False, "default ConvertibleCalendarFactory raised an error"


class FactoriesMixin:
    calendar_factory = ConvertibleCalendarFactory
    conversion_factory = CalendarConversionFactory


class ConvertibleCalendarTest(CalendarTestCase, FactoriesMixin):

    #
    # Helper functions
    #
    @staticmethod
    def random_bad_days_in_months() -> tuple[int, tuple]:
        num_months = FAKE.random_int(min=1, max=20)
        length = num_months + FAKE.random_int(min=1)
        num_elements = length + FAKE.random_int(min=1)
        bad_days_in_months = FAKE.random_elements(
            length=length,
            elements=[days for days in range(1, num_elements)],
        )
        return num_months, bad_days_in_months

    def rand_cal_with_patched_ss(
        self, patch_ss: patch
    ) -> tuple[tuple, "ConvertibleCalendar", patch]:  # noqa: F821
        """random calendar with patched string sanitization"""
        weekday_names = FAKE.words()
        patch_ss.return_value = weekday_names
        calendar = self.calendar_factory.build(
            weekday_names=weekday_names,
            epoch_weekday=0,
            weekday_start=0,
            weekends=(0,),
        )
        return weekday_names, calendar, patch_ss

    def test_convertible_calendar__repr__(self):
        calendar = self.calendar_factory.build()
        assert (
            calendar.__repr__()
            == f"{calendar.name}(Epoch: {calendar.jd_epoch})"
        )

    @pytest.mark.db
    def test_weekday_names_constraint(self):
        no_epoch_weekday_calendar = self.calendar_factory.build(
            epoch_weekday=None
        )
        no_weekday_start_calendar = self.calendar_factory.build(
            weekday_start=None
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(no_epoch_weekday_calendar)
            self.session.commit()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(no_weekday_start_calendar)
            self.session.commit()

    #
    # Weeks
    #
    @patch("src.db.utils.string_sanitization")
    def test__sanitize_weekday_names(self, patch_ss):
        weekday_names, calendar, patch_ss = self.rand_cal_with_patched_ss(
            patch_ss
        )
        week_length = len(calendar.weekday_names)
        new_weekday_names = FAKE.words(nb=week_length)
        calendar.weekday_names = new_weekday_names
        patch_ss.assert_any_call(new_weekday_names)

    @pytest.mark.db
    def test_days_in_week(self):
        calendar = self.calendar_factory.build()
        expected_days_in_weeks = len(calendar.weekday_names)
        with self.session:
            self.session.add(calendar)
            self.session.flush()
            assert calendar.days_in_weeks == expected_days_in_weeks

    @pytest.mark.db
    def test_epoch_weekday_minimum_constraint(self):
        negative_epoch_weekday_calendar = self.calendar_factory.build(
            epoch_weekday=FAKE.random_int(min=-9999, max=-1)
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_epoch_weekday_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_epoch_weekday_maximum_constraint(self):
        week_len = FAKE.random_int(min=1)
        too_big_epoch_weekday_calendar = self.calendar_factory.build(
            weekday_names=FAKE.words(nb=week_len),
            epoch_weekday=FAKE.random_int(min=week_len + 1, max=week_len + 99),
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(too_big_epoch_weekday_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_epoch_weekday_weekless_constraint(self):
        bad_weekless_calendar = self.calendar_factory.build(
            weekday_names=(),
            epoch_weekday=FAKE.random_int(),  # bad weekday_start
            weekday_start=None,
            weekends=(),
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_weekless_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_weekday_start_minimum_constraint(self):
        negative_weekday_start_calendar = self.calendar_factory.build(
            weekday_start=FAKE.random_int(min=-9999, max=-1)
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_weekday_start_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_weekday_start_maximum_constraint(self):
        week_len = FAKE.random_int(min=1)
        too_big_weekday_start_calendar = self.calendar_factory.build(
            weekday_names=FAKE.words(nb=week_len),
            weekday_start=FAKE.random_int(min=week_len + 1, max=week_len + 99),
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(too_big_weekday_start_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_weekday_start_weekless_constraint(self):
        bad_weekless_calendar = self.calendar_factory.build(
            weekday_names=(),
            epoch_weekday=None,
            weekday_start=FAKE.random_int(),  # should be None
            weekends=(),
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_weekless_calendar)
            self.session.commit()

    @patch("src.db.utils.integer_sanitization")
    def test__validate_weekends(self, patch_integer_sanitization):
        week_length = FAKE.random_int(min=1, max=20)
        good_weekends = (0,)
        calendar = self.calendar_factory.build(
            weekday_names=FAKE.words(week_length),
            epoch_weekday=0,
            weekday_start=0,
            weekends=good_weekends,
        )
        bad_weekends = [day for day in range(week_length, week_length + 9)]
        patch_integer_sanitization.assert_any_call(good_weekends)
        with pytest.raises(AssertionError):
            self.calendar_factory.build(
                weekday_names=(),
                epoch_weekday=None,
                weekday_start=None,
                weekends=bad_weekends,
            )
        with pytest.raises(AssertionError):
            calendar.weekends = bad_weekends

    #
    # Common years
    #
    @pytest.mark.db
    def test_common_months_constraint_with_months(self):
        num_months, bad_days_in_months = self.random_bad_days_in_months()
        bad_num_common_months_calendar = self.calendar_factory.build(
            common_year_month_names=FAKE.words(nb=num_months),
            days_in_common_year_months=bad_days_in_months,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_num_common_months_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_common_months_constraint_without_months(self):
        _, days_in_months = self.random_bad_days_in_months()
        bad_monthless_calendar = self.calendar_factory.build(
            common_year_month_names=(),
            days_in_common_year_months=days_in_months,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_monthless_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_months_in_common_year(self):
        calendar = self.calendar_factory.build()
        expected_num_months = len(calendar.common_year_month_names)
        with self.session:
            self.session.add(calendar)
            self.session.flush()
            assert calendar.months_in_common_year == expected_num_months

    def test_days_in_common_year(self):
        calendar = self.calendar_factory.build()
        expected_days_in_common_year = sum(calendar.days_in_common_year_months)
        assert calendar.days_in_common_year == expected_days_in_common_year

    #
    # Leap years
    #
    @pytest.mark.db
    def test_days_in_leap_year_months_constraint_with_months(self):
        num_months, days_in_months = self.random_bad_days_in_months()
        bad_num_leap_months_calendar = self.calendar_factory.build(
            has_leap_year=True,
            leap_year_month_names=FAKE.words(nb=num_months),
            days_in_leap_year_months=days_in_months,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_num_leap_months_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_months_in_leap_year(self):
        calendar = self.calendar_factory.build()
        expected_num_months = len(calendar.leap_year_month_names)
        with self.session:
            self.session.add(calendar)
            self.session.flush()
            assert calendar.months_in_leap_year == expected_num_months

    @pytest.mark.db
    def test_days_in_leap_year_months_constraint_without_months(self):
        bad_monthless_leap_year_calendar = self.calendar_factory.build(
            has_leap_year=True,
            leap_year_month_names=(),
            days_in_leap_year_months=(1, 2),
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_monthless_leap_year_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_day_in_leap_year_months_constraint_without_leap_years(self):
        no_leap_year_calendar = self.calendar_factory.build(
            # leap months made by factory
            has_leap_year=False,
            leap_year_cycles=(),
            leap_year_cycle_ordinals=(),
            leap_year_cycle_start=None,
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(no_leap_year_calendar)
            self.session.commit()

    def test_days_in_leap_year(self):
        calendar = self.calendar_factory.build()
        expected_days_in_leap_year = sum(calendar.days_in_leap_year_months)
        assert calendar.days_in_leap_year == expected_days_in_leap_year

    @patch("src.db.utils.string_sanitization")
    def test__sanitize_month_names(self, patch_ss):
        weekday_names, calendar, patch_ss = self.rand_cal_with_patched_ss(
            patch_ss
        )
        bad_month_names1 = FAKE.random_elements(elements=[1, 2, 3, 4, 5, 6, 7])
        bad_month_names2 = FAKE.random_elements(elements=[0, 8, 9, 10, 11, 12])
        calendar.common_year_month_names = bad_month_names1
        calendar.leap_year_month_names = bad_month_names2
        patch_ss.assert_any_call(bad_month_names1)
        patch_ss.assert_any_call(bad_month_names2)

    @patch("src.db.utils.integer_sanitization")
    def test__validate_days_in_months(self, patch_integer_sanitization):
        num = FAKE.random_int(min=2)
        days_in_common_year_months = FAKE.random_elements(
            elements=[day for day in range(1, num)]
        )
        days_in_leap_year_months = FAKE.random_elements(
            elements=[day for day in range(1, num)]
        )
        negative_days_in_months = FAKE.random_elements(
            elements=[-day for day in range(1, num)]
        )

        self.calendar_factory.build(
            days_in_common_year_months=days_in_common_year_months,
            days_in_leap_year_months=days_in_leap_year_months,
        )
        patch_integer_sanitization.assert_any_call(days_in_common_year_months)
        patch_integer_sanitization.assert_any_call(days_in_leap_year_months)
        with pytest.raises(AssertionError):
            self.calendar_factory.build(
                days_in_common_year_months=negative_days_in_months,
            )
        with pytest.raises(AssertionError):
            self.calendar_factory.build(
                days_in_leap_year_months=negative_days_in_months,
            )

    @patch("src.db.utils.integer_sanitization")
    def test__validates_cycles(self, patch_integer_sanitization):
        leap_year_cycles = FAKE.random_elements(
            elements=[x for x in range(1, 99)]
        )
        patch_integer_sanitization.return_value = leap_year_cycles
        calendar = self.calendar_factory.build(
            leap_year_cycles=leap_year_cycles
        )
        bad_cycles = [x for x in range(FAKE.random_int(min=-9999, max=-1), 0)]
        patch_integer_sanitization.return_value = bad_cycles
        with pytest.raises(AssertionError):
            calendar.leap_year_cycles = bad_cycles
        patch_integer_sanitization.assert_any_call(leap_year_cycles)
        patch_integer_sanitization.assert_any_call(bad_cycles)

    @pytest.mark.db
    def test_leap_year_cycles_constraint(self):
        cycle_length = FAKE.random_int(min=2)
        cycles = [x for x in range(1, cycle_length)]
        cycle_ordinals = [x for x in range(1, cycle_length, 2)]
        leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=cycles,  # should be empty
            leap_year_cycle_start=None,
            leap_year_cycle_ordinals=(),
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(leapless_calendar)
            self.session.commit()

        non_empty_ordinals_leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),
            leap_year_cycle_start=None,
            leap_year_cycle_ordinals=cycle_ordinals,  # should be empty
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(non_empty_ordinals_leapless_calendar)
            self.session.commit()

        non_null_cycle_start_leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),
            leap_year_cycle_start=FAKE.random_int(),  # should be none
            leap_year_cycle_ordinals=(),
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(non_null_cycle_start_leapless_calendar)
            self.session.commit()

        empty_cycle_start_leap_year_calendar = self.calendar_factory.build(
            has_leap_year=True,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=cycles,
            leap_year_cycle_start=None,  # should **not** be None
            leap_year_cycle_ordinals=cycle_ordinals,
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(empty_cycle_start_leap_year_calendar)
            self.session.commit()

        non_empty_cycles_leap_year_calendar = self.calendar_factory.build(
            has_leap_year=True,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),  # should **not** be empty
            leap_year_cycle_start=FAKE.random_int(),
            leap_year_cycle_ordinals=cycle_ordinals,
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(non_empty_cycles_leap_year_calendar)
            self.session.commit()

        non_empty_ordinals_leap_year_calendar = self.calendar_factory.build(
            has_leap_year=True,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=cycles,
            leap_year_cycle_start=FAKE.random_int(),
            leap_year_cycle_ordinals=(),  # should **not** be empty
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(non_empty_ordinals_leap_year_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_leap_year_cycle_start_constraint(self):
        negative_leap_year_cycle_start_calendar = self.calendar_factory.build(
            leap_year_cycle_start=FAKE.random_int(min=-9999, max=-1)
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_leap_year_cycle_start_calendar)
            self.session.commit()

    @patch("src.db.utils.integer_sanitization")
    def test__validates_cycle_ordinals(self, patch_integer_sanitization):
        leap_year_cycle_ordinals = FAKE.random_elements(
            elements=[x for x in range(1, FAKE.random_int(min=2))]
        )
        patch_integer_sanitization.return_value = leap_year_cycle_ordinals
        calendar = self.calendar_factory.build(
            leap_year_cycle_ordinals=leap_year_cycle_ordinals
        )
        bad_leap_ords = [x for x in range(FAKE.random_int(min=-99, max=-1), 0)]
        patch_integer_sanitization.return_value = bad_leap_ords
        with pytest.raises(AssertionError):
            calendar.leap_year_cycle_ordinals = bad_leap_ords
        patch_integer_sanitization.assert_any_call(leap_year_cycle_ordinals)
        patch_integer_sanitization.assert_any_call(bad_leap_ords)

    @pytest.mark.db
    def test_special_common_years_constraint(self):
        bad_leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),
            leap_year_cycle_start=None,
            leap_year_cycle_ordinals=(),
            special_common_years=[x for x in range(FAKE.random_int(min=1))],
            special_leap_years=(),
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_leapless_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_special_leap_years_constraint(self):
        bad_leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),
            leap_year_cycle_start=None,
            leap_year_cycle_ordinals=(),
            special_common_years=(),
            special_leap_years=[x for x in range(FAKE.random_int(min=1))],
            leap_year_offset=None,
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_leapless_calendar)
            self.session.commit()

    @pytest.mark.db
    def test_leap_year_offset_constraint(self):
        bad_leapless_calendar = self.calendar_factory.build(
            has_leap_year=False,
            leap_year_month_names=(),
            days_in_leap_year_months=(),
            leap_year_cycles=(),
            leap_year_cycle_start=None,
            leap_year_cycle_ordinals=(),
            special_common_years=(),
            special_leap_years=(),
            leap_year_offset=FAKE.random_int(min=-9999),  # should be none
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(bad_leapless_calendar)
            self.session.commit()

    @pytest.mark.db
    def test__validate_disjoint_outlaws(self):
        special_years = [year for year in range(FAKE.random_int(min=1))]
        same_special_years_calendar = self.calendar_factory.build(
            special_leap_years=special_years,
            special_common_years=special_years,
        )
        assert event.contains(
            ConvertibleCalendar,
            "before_insert",
            ConvertibleCalendar.validate_disjoint_special_years,
        )
        assert event.contains(
            ConvertibleCalendar,
            "before_update",
            ConvertibleCalendar.validate_disjoint_special_years,
        )
        with pytest.raises(AssertionError), self.session:
            self.session.add(same_special_years_calendar)
            self.session.commit()
        with pytest.raises(AssertionError), self.session:
            calendar = self.calendar_factory.build(
                special_leap_years=special_years,
                special_common_years=[],
            )
            self.session.add(calendar)
            self.session.commit()
            calendar.special_common_years = special_years
            self.session.commit()

    #
    # Eras
    #
    def test_eras_constraint(self):
        no_eras_calendar = self.calendar_factory.build(eras=())
        mismatch_eras_and_ranges_calendar = self.calendar_factory.build(
            eras=(FAKE.word(), FAKE.word()), era_ranges=(("-inf", "inf"),)
        )

        with pytest.raises(IntegrityError), self.session:
            self.session.add(no_eras_calendar)
            self.session.commit()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(mismatch_eras_and_ranges_calendar)
            self.session.commit()

    @patch("src.db.utils.integer_sanitization")
    def test__validate_era_ranges(self, patch_integer_sanitization):
        calendar = self.calendar_factory.build()
        bad_era_range = (-1, FAKE.random_int())
        new_era_ranges = copy.deepcopy(calendar.era_ranges)
        new_era_ranges.insert(1, bad_era_range)
        flat_new_era_ranges = list(
            itertools.chain.from_iterable(new_era_ranges)
        )
        patch_integer_sanitization.return_value = flat_new_era_ranges[1:-1]
        with pytest.raises(AssertionError):
            calendar.era_ranges = new_era_ranges
        with pytest.raises(AssertionError):
            self.calendar_factory.build(  # first era not infinite
                era_ranges=((1, 2), (1, "inf"))
            )
        with pytest.raises(AssertionError):
            self.calendar_factory.build(  # last era not infinite
                era_ranges=(("-inf", 1), (1, FAKE.random_int(min=2)))
            )

    #
    # Collections
    #
    def test_calendars(self):
        with self.session:
            conversion1 = self.conversion_factory.build()
            main_calendar = conversion1.source_calendar
            convertible_calendar1 = conversion1.target_calendar
            conversion2 = self.conversion_factory.build(
                target_calendar=main_calendar
            )
            convertible_calendar2 = conversion2.source_calendar
            non_convertible_calendar = self.calendar_factory.build()
            assert convertible_calendar1 in main_calendar.calendars()
            assert convertible_calendar2 in main_calendar.calendars()
            assert main_calendar not in main_calendar.calendars()
            assert non_convertible_calendar not in main_calendar.calendars()

    def test_conversions(self):
        with self.session:
            conversion1 = self.conversion_factory.build()
            source_calendar = conversion1.source_calendar
            target_calendar = conversion1.target_calendar
            conversion2 = self.conversion_factory.build(
                target_calendar=source_calendar
            )
            unrelated_conversion = self.conversion_factory.build()
            assert conversion1 in source_calendar.conversions()
            assert conversion2 in source_calendar.conversions()
            assert conversion1 in target_calendar.conversions()
            assert conversion2 not in target_calendar.conversions()
            assert unrelated_conversion not in source_calendar.conversions()
            assert unrelated_conversion not in target_calendar.conversions()

    def test_conversion(self):
        with self.session:
            right_conversion = self.conversion_factory.build()
            source_calendar = right_conversion.source_calendar
            target_calendar = right_conversion.target_calendar
            wrong_conversion = self.conversion_factory.build()
            unrelated_calendar = wrong_conversion.source_calendar
            # fmt: off
            assert source_calendar.conversion(target_calendar) is right_conversion  # noqa: E501
            assert target_calendar.conversion(source_calendar) is right_conversion  # noqa: E501
            # fmt: on
            assert source_calendar.conversion(unrelated_calendar) is None
            assert target_calendar.conversion(unrelated_calendar) is None
            assert unrelated_calendar.conversion(target_calendar) is None
            assert unrelated_calendar.conversion(source_calendar) is None

    def test_sync_ordinal(self):
        with self.session:
            conversion = self.conversion_factory.build()
            source_calendar = conversion.source_calendar
            source_sync_ordinal = conversion.source_sync_ordinal
            target_calendar = conversion.target_calendar
            target_sync_ordinal = conversion.target_sync_ordinal
            unrelated_calendar = (
                self.conversion_factory.build().source_calendar
            )
            assert (
                source_calendar.sync_ordinal(target_calendar)
                == source_sync_ordinal
            )
            assert (
                target_calendar.sync_ordinal(source_calendar)
                == target_sync_ordinal
            )
            assert unrelated_calendar.sync_ordinal(source_calendar) is None
            assert source_calendar.sync_ordinal(unrelated_calendar) is None
            assert target_calendar.sync_ordinal(unrelated_calendar) is None


@pytest.mark.db
def test_calendar_conversion_factory():
    # noinspection PyBroadException
    try:
        CalendarConversionFactory()
    except Exception:
        assert False, "default CalendarAssociationFactory raised an error"


class CalendarConversionTest(CalendarTestCase, FactoriesMixin):
    def test_calendar_conversion__repr__(self):
        cc = self.conversion_factory.build()
        assert (
            cc.__repr__() == f"{cc.source_calendar} <-> {cc.target_calendar}"
        )

    @pytest.mark.db
    def test_make_mutual_conversions(self):
        with self.session:
            conversion1_2 = self.conversion_factory()
            calendar1 = conversion1_2.source_calendar
            calendar2 = conversion1_2.target_calendar
            conversion2_3 = self.conversion_factory(source_calendar=calendar2)
            calendar3 = conversion2_3.target_calendar
            expected_sync_ordinal_difference = abs(
                conversion1_2.source_sync_ordinal
                - conversion2_3.target_sync_ordinal
            )
            self.session.flush()

            conversions = set(
                object_
                for object_ in self.session
                if isinstance(object_, CalendarConversion)
            )
            conversion1_3 = conversions - {conversion1_2, conversion2_3}
            conversion1_3 = conversion1_3.pop()  # set -> CalendarConversion

            assert event.contains(
                Session,
                "before_flush",
                CalendarConversion.make_mutual_conversions,
            )
            assert (
                abs(
                    conversion1_3.source_sync_ordinal
                    - conversion1_3.target_sync_ordinal
                )
                == expected_sync_ordinal_difference
            )
            if calendar1.id == conversion1_3.source_calendar.id:
                assert calendar3.id == conversion1_3.target_calendar.id
            elif calendar3.id == conversion1_3.source_calendar.id:
                assert calendar1.id == conversion1_3.target_calendar.id
            else:
                self.fail("Automatic conversion not made")
