import factory
from django.contrib.auth import get_user_model
from faker import Faker

from automate.models import Project

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """User Factory."""

    class Meta:
        """User Factory Meta Class."""

        model = User
        django_get_or_create = ("username",)

    password = factory.PostGenerationMethodCall("set_password", "pass")
    username = fake.name()
    email = fake.email()


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
