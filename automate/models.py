from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from repo.models import BaseModel
from automate.choices import RepoType


User = get_user_model()


class Project(BaseModel):
    """Project Repository Model."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200,
        help_text="Name of task or project i.e copy from parent to child",
        unique=True,
    )
    primary_repo = models.CharField(
        max_length=100, help_text="Name of original repository"
    )
    primary_repo_url = models.CharField(
        max_length=500, help_text="The url repository to be copied from"
    )
    primary_repo_type = models.CharField(
        max_length=50, choices=RepoType.choices, default=RepoType.GITHUB
    )
    secondary_repo = models.CharField(
        max_length=100,
        help_text="Name of repository that new changes would be pushed to",
    )
    secondary_repo_url = models.CharField(
        max_length=500,
        help_text="The url repository that new changes would be pushed to",
    )
    secondary_repo_type = models.CharField(
        max_length=50, choices=RepoType.choices, default=RepoType.GITHUB
    )
    slug = models.SlugField(max_length=250, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Project"
