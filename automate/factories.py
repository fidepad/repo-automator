import factory
from django.contrib.auth import get_user_model

from accounts.factories import UserFactory
from automate.choices import RepoTypeChoices
from automate.models import Project
from faker import Faker


User = get_user_model()
fake = Faker()


class ProjectFactory(factory.django.DjangoModelFactory):
    """Repository Factory."""

    class Meta:
        """Repository Meta Class."""

        model = Project
        django_get_or_create = (
            "primary_repo_owner",
            "primary_repo_name",
            "primary_repo_token",
            "primary_repo_type",
            "secondary_repo_owner",
            "secondary_repo_name",
            "secondary_repo_token",
            "secondary_repo_type",
        )

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker("word")
    primary_repo_owner = factory.Faker("word")
    primary_repo_name = factory.Faker("word")
    primary_repo_token = factory.Faker("sha256")
    primary_repo_type = factory.Faker("random_element", elements=RepoTypeChoices)
    primary_repo_project_name = factory.Faker("word")
    secondary_repo_owner = factory.Faker("word")
    secondary_repo_name = factory.Faker("word")
    secondary_repo_token = factory.Faker("sha256")
    secondary_repo_type = factory.Faker("random_element", elements=RepoTypeChoices)
    secondary_repo_project_name = factory.Faker("word")
