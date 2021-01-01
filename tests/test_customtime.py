import datetime
import pytest

from tests.factories import ConvertibleTimeFactory, ConvertibleClockFactory
from tests.utils import DatabaseTestCase, FAKE
from unittest.mock import patch


def test_convertible_time_factory():
    # noinspection PyBroadException
    try:
        ConvertibleTimeFactory()
    except Exception:
        assert False, "Default ConvertibleTimeFactory raised an error"


@patch(
    "src.customtime.ConvertibleTime.are_valid_hour_labels", return_value=True
)
def test___init__(patch_are_valid_hour_labels):
    ct = ConvertibleTimeFactory()
    hour_labels = ct.hour_labels
    patch_are_valid_hour_labels.assert_called_once_with(hour_labels)


@pytest.mark.db
class ConvertibleTimeTest(DatabaseTestCase):
    def setUp(self):
        super(ConvertibleTimeTest, self).setUp()
        self.time_factory = ConvertibleTimeFactory
        self.clock_factory = ConvertibleClockFactory

        earth_clock = self.clock_factory.create(
            seconds_in_minute=60,
            minutes_in_hour=60,
            hours_in_day=24,
        )
        self.session.add(earth_clock)
        self.session.commit()

        self.earth_time = self.time_factory.build(
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

    def test_convertible_clocks(self):
        convertible_clocks = set(
            self.clock_factory.create_batch(
                FAKE.random_int(min=1, max=10),
                **{
                    "seconds_in_minute": 60,
                    "minutes_in_hour": 60,
                    "hours_in_day": 24,
                },
            )
        )
        nonconvertible_clocks = set(
            self.clock_factory.create_batch(
                FAKE.random_int(min=1, max=10),
                **{
                    "seconds_in_minute": FAKE.random_int(min=61, max=100),
                    "minutes_in_hour": FAKE.random_int(min=61, max=100),
                    "hours_in_day": FAKE.random_int(min=24, max=100),
                },
            )
        )
        fetched_clocks = set(self.earth_time.convertible_clocks())
        assert convertible_clocks.issubset(fetched_clocks)
        # assert fetched_clocks == convertible_clocks
        assert fetched_clocks.isdisjoint(nonconvertible_clocks)

    def test_hms_to_seconds(self):
        assert self.earth_time.hms_to_seconds(self.hms) == self.seconds

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_seconds_to_hms(self, *_):
        assert self.earth_time.seconds_to_hms(self.seconds) == self.hms

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_seconds_to_hms_and_hms_to_seconds_are_reversible(self, *_):
        assert (
            self.earth_time.seconds_to_hms(
                self.earth_time.hms_to_seconds(self.hms)
            )
            == self.hms
        )
        assert (
            self.earth_time.hms_to_seconds(
                self.earth_time.seconds_to_hms(self.seconds)
            )
            == self.seconds
        )

    @patch("src.customtime.ConvertibleTime.is_valid_hour", return_value=True)
    def test_hour(self, *_):
        assert self.earth_time.hour(self.seconds) == self.py_dt.hour

    @patch("src.customtime.ConvertibleTime.is_valid_minute", return_value=True)
    def test_minute(self, _):
        assert self.earth_time.minute(self.seconds) == self.py_dt.minute

    @patch("src.customtime.ConvertibleTime.is_valid_hour", return_value=True)
    @patch("src.customtime.ConvertibleTime.is_valid_minute", return_value=True)
    def test_is_valid_hms(self, *_):
        big_second = FAKE.random_int(min=60)
        negative_second = FAKE.random_int(min=-9999, max=-1)
        big_second_hms = self.py_dt.hour, self.py_dt.minute, big_second
        negative_second_hms = (
            self.py_dt.hour,
            self.py_dt.minute,
            negative_second,
        )
        assert not self.earth_time.is_valid_hms(big_second_hms)
        assert not self.earth_time.is_valid_hms(negative_second_hms)
        assert self.earth_time.is_valid_hms(self.hms)

    def test_is_valid_hour(self):
        big_hour = FAKE.random_int(min=24)
        negative_hour = FAKE.random_int(min=-9999, max=-1)
        assert not self.earth_time.is_valid_hour(big_hour)
        assert not self.earth_time.is_valid_hour(negative_hour)
        assert self.earth_time.is_valid_hour(self.py_dt.hour)

    def test_is_valid_minute(self):
        big_minute = FAKE.random_int(min=60)
        negative_minute = FAKE.random_int(min=-9999, max=-1)
        assert not self.earth_time.is_valid_minute(big_minute)
        assert not self.earth_time.is_valid_minute(negative_minute)
        assert self.earth_time.is_valid_minute(self.py_dt.minute)

    def test_hms_to_hr_time(self):
        split_hr_time = self.py_dt.time().strftime("%I:%M:%S:%p")
        mil_hr_time = self.py_dt.time().strftime("%H:%M:%S")
        assert self.earth_time.hms_to_hr_time(self.hms, True) == split_hr_time
        assert self.earth_time.hms_to_hr_time(self.hms, False) == mil_hr_time

    def test_hr_time_to_hms(self):
        split_hr_time = self.py_dt.time().strftime("%I:%M:%S:%p")
        mil_hr_time = self.py_dt.time().strftime("%H:%M:%S")
        assert self.earth_time.hr_time_to_hms(split_hr_time) == self.hms
        assert self.earth_time.hr_time_to_hms(mil_hr_time) == self.hms

    @patch(
        "src.customtime.ConvertibleTime.day_demarcations",
        return_value=[0, 12, 24],
    )
    def test_labeled_hour(self, _):
        hour_label = self.py_dt.time().strftime("%p")
        hour = int(self.py_dt.time().strftime("%H"))
        labeled_hour = int(self.py_dt.time().strftime("%I"))
        assert self.earth_time.labeled_hour(hour) == (labeled_hour, hour_label)
        assert self.earth_time.labeled_hour(0) == (12, "AM")

    def test_labeled_hour_raises(self):
        num_hour_labels = FAKE.random_int(min=1, max=20)
        hours_in_day = FAKE.random_int(min=1, max=100) * num_hour_labels
        clock = self.clock_factory.create(hours_in_day=hours_in_day)
        no_hour_label_ct = self.time_factory.build(
            clock=clock, hour_labels=list()
        )
        ct = self.time_factory.build(
            clock=clock, hour_labels=FAKE.words(nb=num_hour_labels)
        )
        with pytest.raises(ValueError):
            no_hour_label_ct.labeled_hour(
                FAKE.random_int(min=1, max=hours_in_day - 1)
            )
        with pytest.raises(RuntimeError):
            ct.labeled_hour(hours_in_day + 1)

    def test_day_demarcations(self):
        assert self.earth_time.day_demarcations() == [0, 12, 24]

    def test_max_hr_hour(self):
        raise NotImplementedError

    def test_are_valid_hour_labels(self):
        hours_in_day = FAKE.random_int(min=1, max=100)
        bad_hour_labels = FAKE.words(nb=hours_in_day + 1, unique=True)
        ct = self.time_factory.build(
            clock=self.clock_factory.build(hours_in_day=hours_in_day),
        )
        assert ct.are_valid_hour_labels(bad_hour_labels) is False
        assert ct.are_valid_hour_labels([]) is True
        assert self.earth_time.are_valid_hour_labels(["AM", "PM"]) is True
