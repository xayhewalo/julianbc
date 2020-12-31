import pytest

from tests.factories import ConvertibleTimeFactory


@pytest.mark.db
def test_convertible_time_factory():
    # noinspection PyBroadException
    try:
        ConvertibleTimeFactory()
    except Exception:
        assert False, "default ConvertibleTimeFactory raised an error"
