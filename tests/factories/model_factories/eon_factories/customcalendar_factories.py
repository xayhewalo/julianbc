from tests.factories.utils import BaseFactory, factory
from tests.utils import FAKE
from src.models import CalendarConversion, ConvertibleCalendar

num_weekdays = FAKE.random_int(min=1, max=20)
weekday_indexes = [x for x in range(num_weekdays)]
num_common_year_months = FAKE.random_int(min=1, max=20)
num_leap_year_months = FAKE.random_int(min=1, max=20)
num_eras = FAKE.random_int(min=2, max=10)


class ConvertibleCalendarFactory(BaseFactory):
    class Meta:
        model = ConvertibleCalendar

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    weekday_names = factory.Faker("words", nb=num_weekdays)
    weekday_start = factory.Faker("random_element", elements=weekday_indexes)
    weekends = factory.Faker(
        "random_elements", elements=weekday_indexes, unique=True
    )
    epoch_weekday = factory.Faker(
        "random_element", elements=[x for x in range(num_weekdays)]
    )
    common_year_month_names = factory.Faker("words", nb=num_common_year_months)
    days_in_common_year_months = factory.Faker(
        "random_choices",
        elements=[x for x in range(1, 200)],
        length=num_common_year_months,
    )
    has_leap_year = True
    leap_year_month_names = factory.Faker("words", nb=num_leap_year_months)
    days_in_leap_year_months = factory.Faker(
        "random_choices",
        elements=[x for x in range(1, 200)],
        length=num_leap_year_months,
    )
    leap_year_cycles = factory.Faker(
        "random_elements",
        elements=[x for x in range(1, FAKE.random_int(min=1, max=3000))],
    )
    leap_year_cycle_start = factory.Faker("random_element", elements=(0, 1))
    leap_year_cycle_ordinals = factory.Faker(
        "random_elements",
        elements=[x for x in range(1, FAKE.random_int(min=1, max=3000))],
    )
    leap_year_exceptions = factory.Faker(
        "random_elements",
        elements=[x for x in range(1, 10000, 2)],
        unique=True,
        length=2,
    )
    leap_year_overrules = factory.Faker(
        "random_elements",
        elements=[x for x in range(-9998, 10000, 2)],
        unique=True,
        length=2,
    )
    leap_year_offset = factory.Faker("random_int", min=-9999, max=9999)
    eras = factory.Faker("words", nb=num_eras, unique=True)
    era_ranges = factory.Faker("era_ranges", length=num_eras)
    jd_epoch = factory.Faker("random_int", min=-99999999, max=99999999)

    @factory.post_generation
    def _source_conversion(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for _source_conversion in extracted:
                self._source_conversion.append(_source_conversion)

    @factory.post_generation
    def _target_conversion(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for _target_conversion in extracted:
                self._target_conversion.append(_target_conversion)


class CalendarConversionFactory(BaseFactory):
    class Meta:
        model = CalendarConversion

    target_calendar = factory.SubFactory(ConvertibleCalendarFactory)
    source_calendar = factory.SubFactory(ConvertibleCalendarFactory)
    source_sync_ordinal = factory.Faker("random_int", min=-9999)
    target_sync_ordinal = factory.Faker("random_int", min=-9999)
