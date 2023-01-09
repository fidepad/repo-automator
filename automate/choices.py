from django.db import models


class RepoType(models.TextChoices):
    """Repository Types."""

    GITHUB = "github", "Github"
    BITBUCKET = "bitbucket", "Bitbucket"
