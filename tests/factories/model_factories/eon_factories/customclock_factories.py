import factory

from src.models import ConvertibleTime
from tests.factories.utils import BaseFactory
from tests.factories.providers import Provider

factory.Faker.add_provider(Provider)


class ConvertibleTimeFactory(BaseFactory):
    class Meta:
        model = ConvertibleTime

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    seconds_in_minute = factory.Faker("random_int", min=1)
    minutes_in_hour = factory.Faker("random_int", min=1)
    hours_in_day = factory.Faker("random_int", min=1)
