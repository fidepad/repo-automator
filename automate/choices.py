from django.db import models


class RepoTypeChoices(models.TextChoices):
    """Repository Types."""

    GITHUB = "github", "Github"
    GITBUCKET = "gitbucket", "Gitbucket"
