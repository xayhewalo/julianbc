from src.db import ConvertibleClock
from tests.factories.utils import BaseFactory, factory


class ConvertibleClockFactory(BaseFactory):
    class Meta:
        model = ConvertibleClock

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    seconds_in_minute = factory.Faker("random_int", min=1)
    minutes_in_hour = factory.Faker("random_int", min=1)
    hours_in_day = factory.Faker("random_int", min=1)
