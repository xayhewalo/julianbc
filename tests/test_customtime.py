import datetime
import pytest

from src.customtime import TimeUnit
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

        earth_clock = self.clock_factory.build(
            seconds_in_minute=60,
            minutes_in_hour=60,
            hours_in_day=24,
        )
        self.session.add(earth_clock)
        self.session.commit()

        self.earth_ct = self.time_factory.build(
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

    @patch("src.db.eon.customclock.ConvertibleClock.convertible_clocks")
    @patch("src.customtime.ConvertibleTime.hms_to_seconds")
    @patch("src.customtime.ConvertibleTime.seconds_to_hms")
    def test_convert_hms(self, p_seconds_to_hms, p_hms_to_seconds, p_cc):
        patch_convertible_clocks = p_cc
        patch_hms_to_seconds = p_hms_to_seconds
        patch_seconds_to_hms = p_seconds_to_hms

        foreign_clock = self.clock_factory.build(
            seconds_in_minute=86400,
            minutes_in_hour=1,
            hours_in_day=1,
        )
        foreign_time = self.time_factory.build(clock=foreign_clock)
        seconds = FAKE.random_int(min=0, max=85399)
        foreign_hms = 0, 0, seconds
        patch_convertible_clocks.return_value = [foreign_clock]
        patch_hms_to_seconds.return_value = seconds
        self.earth_ct.convert_hms(foreign_hms, foreign_time)

        patch_convertible_clocks.assert_called_once()
        patch_hms_to_seconds.assert_called_once_with(foreign_hms)
        patch_seconds_to_hms.assert_called_once_with(seconds)

    @patch(
        "src.db.eon.customclock.ConvertibleClock.convertible_clocks",
        return_value=list(),
    )
    def test_convert_hms_raises(self, _):
        clock = self.clock_factory.build()
        time = self.time_factory.build(clock=clock)
        hms = 1, 1, 1
        with pytest.raises(ValueError):
            time.convert_hms(hms, time)

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_seconds_to_hms(self, *_):
        assert self.earth_ct.seconds_to_hms(self.seconds) == self.hms

    def test_hms_to_seconds(self):
        assert self.earth_ct.hms_to_seconds(self.hms) == self.seconds

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_shift_hms(self, _):
        plus_one_sec = [[1, TimeUnit.SECOND]]
        minus_one_sec = [[-1, TimeUnit.SECOND]]
        plus_one_min = [[1, TimeUnit.MINUTE]]
        minus_one_min = [[-1, TimeUnit.MINUTE]]
        plus_one_hour = [[1, TimeUnit.HOUR]]
        minus_one_hour = [[-1, TimeUnit.HOUR]]

        hours = FAKE.random_int(min=-9999)
        mins = FAKE.random_int(min=-9999)
        secs = FAKE.random_int(min=-9999)
        pydelta = datetime.timedelta(hours=hours, minutes=mins, seconds=secs)
        day_delta = pydelta.days
        shifted_pydt = self.py_dt + pydelta
        expected_hms = (
            shifted_pydt.hour,
            shifted_pydt.minute,
            shifted_pydt.second,
        )
        intervals = [
            [hours, TimeUnit.HOUR],
            [mins, TimeUnit.MINUTE],
            [secs, TimeUnit.SECOND],
        ]
        earth_ct = self.earth_ct
        assert earth_ct.shift_hms((0, 0, 0), plus_one_sec) == ((0, 0, 1), 0)
        assert earth_ct.shift_hms((23, 59, 59), plus_one_sec) == (
            (0, 0, 0),
            1,
        )
        assert earth_ct.shift_hms((0, 0, 1), minus_one_sec) == ((0, 0, 0), 0)
        assert earth_ct.shift_hms((0, 0, 0), minus_one_sec) == (
            (23, 59, 59),
            -1,
        )
        assert earth_ct.shift_hms((0, 0, 0), plus_one_min) == ((0, 1, 0), 0)
        assert earth_ct.shift_hms((23, 59, 0), plus_one_min) == ((0, 0, 0), 1)
        assert earth_ct.shift_hms((0, 1, 0), minus_one_min) == ((0, 0, 0), 0)
        assert earth_ct.shift_hms((0, 0, 0), minus_one_min) == (
            (23, 59, 0),
            -1,
        )
        assert earth_ct.shift_hms((0, 0, 0), plus_one_hour) == ((1, 0, 0), 0)
        assert earth_ct.shift_hms((23, 0, 0), plus_one_hour) == ((0, 0, 0), 1)
        assert earth_ct.shift_hms((1, 0, 0), minus_one_hour) == ((0, 0, 0), 0)
        assert earth_ct.shift_hms((0, 0, 0), minus_one_hour) == (
            (23, 0, 0),
            -1,
        )
        assert earth_ct.shift_hms(self.hms, intervals) == (
            expected_hms,
            day_delta,
        )

    def test_shift_hms_raises(self):
        bad_hms = -1, -1, -1
        bad_timeunit = -1
        with pytest.raises(ValueError):
            self.earth_ct.shift_hms(bad_hms, [[0, TimeUnit.SECOND]])
        with pytest.raises(ValueError):
            self.earth_ct.shift_hms(self.hms, [[0, bad_timeunit]])

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_next_hms(self, _):
        earth_ct = self.earth_ct
        one_sec = [1, TimeUnit.SECOND]
        two_sec = [2, TimeUnit.SECOND]
        five_sec = [5, TimeUnit.SECOND]
        six_sec = [6, TimeUnit.SECOND]
        ten_sec = [10, TimeUnit.SECOND]

        one_min = [1, TimeUnit.MINUTE]
        two_min = [2, TimeUnit.MINUTE]
        five_min = [5, TimeUnit.MINUTE]
        six_min = [6, TimeUnit.MINUTE]
        ten_min = [10, TimeUnit.MINUTE]

        one_hour = [1, TimeUnit.HOUR]
        two_hour = [2, TimeUnit.HOUR]
        four_hour = [4, TimeUnit.HOUR]
        six_hour = [6, TimeUnit.HOUR]
        assert earth_ct.next_hms((0, 0, 0), one_sec) == ((0, 0, 1), 0)
        assert earth_ct.next_hms((8, 4, 4), five_sec) == ((8, 4, 5), 0)
        assert earth_ct.next_hms((9, 3, 59), two_sec) == ((9, 4, 0), 0)
        assert earth_ct.next_hms((23, 59, 51), ten_sec) == ((0, 0, 0), 1)
        assert earth_ct.next_hms((2, 3, 8), one_sec, False) == ((2, 3, 7), 0)
        assert earth_ct.next_hms((1, 5, 8), two_sec, False) == ((1, 5, 6), 0)
        assert earth_ct.next_hms((8, 6, 0), ten_sec, False) == (
            (8, 5, 50),
            0,
        )
        assert earth_ct.next_hms((0, 0, 0), six_sec, False) == (
            (23, 59, 54),
            -1,
        )
        assert earth_ct.next_hms((0, 0, 0), one_min) == ((0, 1, 0), 0)
        assert earth_ct.next_hms((19, 3, 27), two_min) == ((19, 4, 0), 0)
        assert earth_ct.next_hms((20, 16, 11), five_min) == ((20, 20, 0), 0)
        assert earth_ct.next_hms((0, 0, 0), six_min, False) == (
            (23, 54, 0),
            -1,
        )
        assert earth_ct.next_hms((5, 9, 1), ten_min, False) == ((5, 0, 0), 0)
        assert earth_ct.next_hms((0, 0, 0), one_hour) == ((1, 0, 0), 0)
        assert earth_ct.next_hms((13, 24, 22), two_hour) == ((14, 0, 0), 0)
        assert earth_ct.next_hms((23, 45, 55), four_hour) == ((0, 0, 0), 1)
        assert earth_ct.next_hms((0, 0, 0), six_hour, False) == (
            (18, 0, 0),
            -1,
        )
        assert earth_ct.next_hms((16, 21, 33), one_hour, False) == (
            (16, 0, 0),
            0,
        )

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=False)
    def test_next_hms_for_invalid_hms(self, _):
        fake_hms = FAKE.pytuple()
        fake_interval = FAKE.pylist()
        with pytest.raises(ValueError):
            assert self.earth_ct.next_hms(fake_hms, fake_interval)

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_next_hms_raises_other_errors(self, _):
        fake_timeunit = FAKE.random_int()
        fake_interval = [FAKE.random_int(), fake_timeunit]
        timeunit = FAKE.random_element(elements=TimeUnit)
        big_frequency = FAKE.random_int(min=61)
        fake_float = FAKE.pyfloat(max_value=-1)
        earth_ct = self.earth_ct
        with pytest.raises(ValueError):
            assert earth_ct.next_hms(self.hms, fake_interval)
        with pytest.raises(ValueError):
            assert earth_ct.next_hms(self.hms, [big_frequency, timeunit])
        with pytest.raises(ValueError):
            assert earth_ct.next_hms(self.hms, [fake_float, timeunit])

    @patch("src.customtime.ConvertibleTime.is_valid_hms", return_value=True)
    def test_seconds_to_hms_and_hms_to_seconds_are_reversible(self, *_):
        assert (
            self.earth_ct.seconds_to_hms(
                self.earth_ct.hms_to_seconds(self.hms)
            )
            == self.hms
        )
        assert (
            self.earth_ct.hms_to_seconds(
                self.earth_ct.seconds_to_hms(self.seconds)
            )
            == self.seconds
        )

    @patch("src.customtime.ConvertibleTime.is_valid_hour", return_value=True)
    def test_hour(self, *_):
        assert self.earth_ct.hour(self.seconds) == self.py_dt.hour

    @patch("src.customtime.ConvertibleTime.is_valid_minute", return_value=True)
    def test_minute(self, _):
        assert self.earth_ct.minute(self.seconds) == self.py_dt.minute

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
        assert not self.earth_ct.is_valid_hms(big_second_hms)
        assert not self.earth_ct.is_valid_hms(negative_second_hms)
        assert self.earth_ct.is_valid_hms(self.hms)

    def test_is_valid_hour(self):
        big_hour = FAKE.random_int(min=24)
        negative_hour = FAKE.random_int(min=-9999, max=-1)
        assert not self.earth_ct.is_valid_hour(big_hour)
        assert not self.earth_ct.is_valid_hour(negative_hour)
        assert self.earth_ct.is_valid_hour(self.py_dt.hour)

    def test_is_valid_minute(self):
        big_minute = FAKE.random_int(min=60)
        negative_minute = FAKE.random_int(min=-9999, max=-1)
        assert not self.earth_ct.is_valid_minute(big_minute)
        assert not self.earth_ct.is_valid_minute(negative_minute)
        assert self.earth_ct.is_valid_minute(self.py_dt.minute)

    def test_hms_to_hr_time(self):
        split_hr_time = self.py_dt.time().strftime("%I:%M:%S:%p")
        mil_hr_time = self.py_dt.time().strftime("%H:%M:%S")
        assert self.earth_ct.hms_to_hr_time(self.hms, True) == split_hr_time
        assert self.earth_ct.hms_to_hr_time(self.hms, False) == mil_hr_time

    def test_hr_time_to_hms(self):
        split_hr_time = self.py_dt.time().strftime("%I:%M:%S:%p")
        mil_hr_time = self.py_dt.time().strftime("%H:%M:%S")
        assert self.earth_ct.hr_time_to_hms(split_hr_time) == self.hms
        assert self.earth_ct.hr_time_to_hms(mil_hr_time) == self.hms

    @patch(
        "src.customtime.ConvertibleTime.day_demarcations",
        return_value=[0, 12, 24],
    )
    @patch("src.customtime.ConvertibleTime.max_hr_hour", return_value=12)
    def test_labeled_hour(self, *_):
        hour_label = self.py_dt.time().strftime("%p")
        hour = int(self.py_dt.time().strftime("%H"))
        labeled_hour = int(self.py_dt.time().strftime("%I"))
        assert self.earth_ct.labeled_hour(hour) == (labeled_hour, hour_label)
        assert self.earth_ct.labeled_hour(0) == (12, "AM")

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

    @patch("src.customtime.ConvertibleTime.max_hr_hour", return_value=12)
    def test_day_demarcations(self, _):
        assert self.earth_ct.day_demarcations() == [0, 12, 24]

    def test_max_hr_hour(self):
        assert self.earth_ct.max_hr_hour() == 12

    def test_are_valid_hour_labels(self):
        hours_in_day = FAKE.random_int(min=1, max=100)
        bad_hour_labels = FAKE.words(nb=hours_in_day + 1, unique=True)
        ct = self.time_factory.build(
            clock=self.clock_factory.build(hours_in_day=hours_in_day),
        )
        assert ct.are_valid_hour_labels(bad_hour_labels) is False
        assert ct.are_valid_hour_labels([]) is True
        assert self.earth_ct.are_valid_hour_labels(["AM", "PM"]) is True
