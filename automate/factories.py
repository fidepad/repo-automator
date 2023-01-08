import factory
from django.contrib.auth import get_user_model

from accounts.factories import UserFactory
from automate.models import Project
from faker import Faker


User = get_user_model()
fake = Faker()


class RepositoryFactory(factory.django.DjangoModelFactory):
    """Repository Factory."""

    class Meta:
        """Repository Meta Class."""

        model = Project

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker("sentence", nb_words=10)
    primary_repo = factory.Faker("sentence", nb_words=4)
    secondary_repo = factory.Faker("sentence", nb_words=4)
    primary_repo_url = fake.url(schemes=["https"])
    secondary_repo_url = fake.url(schemes=["https"])
