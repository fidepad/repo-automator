from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from repo.models import BaseModel
from automate.choices import RepoType


class Project(BaseModel):
    """Project Repository Model."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200,
        help_text="Name of task or project i.e copy from parent to child",
        unique=True,
    )
    primary_username = models.CharField(
        max_length=200, help_text="The git username for the primary repository"
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
    primary_token = models.TextField(
        help_text="Primary Access token to make PR changes"
    )
    secondary_repo = models.CharField(
        max_length=100,
        help_text="Name of repository that new changes would be pushed to",
    )
    secondary_username = models.CharField(
        max_length=200, help_text="The git username for the secondary repository"
    )
    secondary_repo_url = models.CharField(
        max_length=500,
        help_text="The url repository that new changes would be pushed to",
    )
    secondary_repo_type = models.CharField(
        max_length=50, choices=RepoType.choices, default=RepoType.GITHUB
    )
    secondary_token = models.TextField(
        help_text="Secondary Access token to make PR changes"
    )
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    base = models.CharField(
        max_length=200,
        help_text="The branch you want to target with PR changes. i.e., main",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Project"


class History(BaseModel):
    """History Model to retain payload information."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    pr_id = models.IntegerField()
    action = models.CharField(max_length=30, null=True)
    body = models.TextField()
    url = models.URLField(help_text="url link for the new PR")
    primary_url = models.URLField(help_text="url link for the initial PR")
    author = models.CharField(max_length=200)
    comments = models.IntegerField(default=0)
    merged_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.project}: {self.action}"
