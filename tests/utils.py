import datetime
# noinspection PyUnresolvedReferences
import factory
import factory.random

from src.customtime import ConvertibleTime
from src.db import ConvertibleClock
from src.db.utils import Base
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
        Base.metadata.create_all(self.session.bind)

    def tearDown(self):
        Base.metadata.drop_all(self.session.bind)
        self.session.close()


class TimeTestCase(DatabaseTestCase):
    def setUp(self):
        super(TimeTestCase, self).setUp()

        earth_clock = ConvertibleClock(
            name="Earth",
            seconds_in_minute=60,
            minutes_in_hour=60,
            hours_in_day=24,
        )
        self.session.add(earth_clock)
        self.session.commit()

        self.earth_ct = ConvertibleTime(
            clock=earth_clock,
            hour_labels=["AM", "PM"],
            clock_sep=":",
        )
        self.py_dt = FAKE.date_time(tzinfo=datetime.timezone.utc)
        midnight = self.py_dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self.seconds = (self.py_dt - midnight).seconds
        self.hms = self.py_dt.hour, self.py_dt.minute, self.py_dt.second


class CalendarTestCase(DatabaseTestCase):
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
