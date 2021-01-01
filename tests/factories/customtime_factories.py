from tests.factories import ConvertibleClockFactory
from tests.factories.utils import factory
from src.customtime import ConvertibleTime


class ConvertibleTimeFactory(factory.Factory):
    class Meta:
        model = ConvertibleTime

    clock = factory.SubFactory(ConvertibleClockFactory)
    clock_sep = factory.Faker("random_element", elements=[":", "-"])
    hour_labels = list()
