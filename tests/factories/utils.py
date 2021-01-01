import factory

from tests.factories.providers import Provider
from tests.utils import Session

factory.Faker.add_provider(Provider)


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = Session
