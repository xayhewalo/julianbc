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
        self.clock_factory = ConvertibleClockFactory

    def test___repr__(self):
        name = FAKE.word()
        seconds_in_day = FAKE.random_int(min=1)
        convertible_clock = self.clock_factory.build(
            name=name, seconds_in_day=seconds_in_day
        )
        assert (
            repr(convertible_clock)
            == f"{name}(Seconds in a Day: {seconds_in_day})"
        )

    @pytest.mark.db
    def test_validate_positive(self):
        negative_seconds_clock = self.clock_factory.build(
            seconds_in_minute=FAKE.random_int(min=-9999, max=-1)
        )
        negative_minutes_clock = self.clock_factory.build(
            minutes_in_hour=FAKE.random_int(min=-9999, max=-1)
        )
        negative_hours_clock = self.clock_factory.build(
            hours_in_day=FAKE.random_int(min=-9999, max=-1)
        )
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_seconds_clock)
            self.session.flush()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_minutes_clock)
            self.session.flush()
        with pytest.raises(IntegrityError), self.session:
            self.session.add(negative_hours_clock)
            self.session.flush()

    @pytest.mark.db
    def test_convertible_clocks(self):
        params = {
            "seconds_in_minute": 60,
            "minutes_in_hour": 60,
            "hours_in_day": 24,
        }
        with self.session:
            clock = self.clock_factory.build(**params)
            convertible_clocks = set(
                self.clock_factory.build_batch(
                    FAKE.random_int(min=1, max=10),
                    **params,
                )
            )
            nonconvertible_clocks = set(
                self.clock_factory.build_batch(
                    FAKE.random_int(min=1, max=10),
                    **{
                        "seconds_in_minute": FAKE.random_int(min=61, max=100),
                        "minutes_in_hour": FAKE.random_int(min=61, max=100),
                        "hours_in_day": FAKE.random_int(min=24, max=100),
                    },
                )
            )
            self.session.add_all([*convertible_clocks, *nonconvertible_clocks])
            self.session.add(clock)
            self.session.commit()
            fetched_clocks = set(clock.convertible_clocks())
            assert convertible_clocks.issubset(fetched_clocks)
            # assert fetched_clocks == convertible_clocks
            assert fetched_clocks.isdisjoint(nonconvertible_clocks)
