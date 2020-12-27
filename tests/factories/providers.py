"""Custom providers used with Factory Boy"""
import factory

from faker.providers import BaseProvider

FAKE = factory.faker.faker.Faker()


class Provider(BaseProvider):
    @staticmethod
    def era_ranges(length):
        """Random era_range for :py:class:`ConvertibleCalendar`"""
        eras_left = length - 2
        ranges = list()
        while eras_left > 0:
            start = FAKE.random_int(min=1, max=99999)
            end = FAKE.random_int(min=1, max=99999)
            ranges.append((start, end))
            eras_left -= 1
        start, end = "-inf", FAKE.random_int(min=1, max=99999)
        ranges.insert(0, (start, end))
        start, end = FAKE.random_int(min=1, max=99999), "inf"
        ranges.append((start, end))
        return ranges
