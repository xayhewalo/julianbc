import pytest

from sqlalchemy.exc import IntegrityError
from tests.factories import ConvertibleClockFactory
from tests.utils import DatabaseTestCase, FAKE


@pytest.mark.db
def test_convertible_clock_factory():
    # noinspection PyBroadException
    try:
        ConvertibleClockFactory()
    except Exception:
        assert False, "default ConvertibleClockFactory raised an error"


class ConvertibleTimeTest(DatabaseTestCase):
    def setUp(self):
        super(ConvertibleTimeTest, self).setUp()
        self.time_factory = ConvertibleClockFactory

    @pytest.mark.db
    def test_validate_positive(self):
        negative_seconds_time = self.time_factory.build(
            seconds_in_minute=FAKE.random_int(min=-9999, max=-1)
        )
        negative_minutes_time = self.time_factory.build(
            minutes_in_hour=FAKE.random_int(min=-9999, max=-1)
        )
        negative_hours_time = self.time_factory.build(
            hours_in_day=FAKE.random_int(min=-9999, max=-1)
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_seconds_time)
            self.session.flush()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_minutes_time)
            self.session.flush()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_hours_time)
            self.session.flush()
