import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """User Factory."""

    class Meta:
        """User Factory Meta Class."""

        model = User
        django_get_or_create = ("email",)

    password = factory.PostGenerationMethodCall("set_password", "pass")
    email = fake.email()
