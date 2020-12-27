# noinspection PyUnresolvedReferences
import factory
import factory.random

from src.models import CalBase
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from unittest import TestCase

engine = create_engine("sqlite://", future=True)
Session = scoped_session(sessionmaker(bind=engine))

factory.random.reseed_random("julianbc")
FAKE = factory.faker.faker.Faker()


class DatabaseTestCase(TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.close()
        Session.remove()


class CalendarTestCase(DatabaseTestCase):
    def setUp(self):
        super(CalendarTestCase, self).setUp()
        CalBase.metadata.create_all(self.session.bind)

    def tearDown(self):
        CalBase.metadata.drop_all(self.session.bind)
        super(CalendarTestCase, self).tearDown()

    @staticmethod
    # fmt: off
    def random_common_month_and_day(calendar: "ConvertibleCalendar") -> tuple:  # noqa: F821, E501
        # fmt: on
        month = FAKE.random_element(elements=calendar.common_year_month_names)
        month = calendar.common_year_month_names.index(month) + 1
        days_in_month = calendar.days_in_common_year_months[month - 1]
        day = FAKE.random_element(
            elements=[x for x in range(1, days_in_month + 1)]
        )
        return month, day

    @staticmethod
    # fmt: off
    def random_leap_month_and_day(calendar: "ConvertibleCalendar") -> tuple:  # noqa: F821, E501
        # fmt: on
        month = FAKE.random_element(elements=calendar.leap_year_month_names)
        month = calendar.leap_year_month_names.index(month) + 1
        days_in_month = calendar.days_in_leap_year_months[month - 1]
        day = FAKE.random_element(
            elements=[x for x in range(1, days_in_month + 1)]
        )
        return month, day
