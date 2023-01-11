from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

from automate.choices import RepoTypeChoices
from repo.models import BaseModel

User = get_user_model()


class Project(BaseModel):
    """Project Repository Model."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200,
        help_text="Name of the project",
        unique=True,
    )
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    primary_repo_owner = models.CharField(
        max_length=100, help_text="Primary repo owner"
    )
    primary_repo_name = models.CharField(max_length=100, help_text="Primary repo name")
    primary_repo_token = models.TextField(help_text="Access Token for primary repo")
    primary_repo_type = models.CharField(
        max_length=50, choices=RepoTypeChoices.choices, default=RepoTypeChoices.GITHUB
    )
    primary_repo_project_name = models.CharField(
        max_length=100,
        help_text="Primary Repo project name; If repo is bitbucket",
        null=True,
        blank=True,
    )
    primary_repo_url = models.CharField(
        max_length=500, help_text="The url repository to be copied from"
    )
    base = models.CharField(
        max_length=200,
        help_text="The branch you want to target with PR changes. i.e., main",
    )
    secondary_repo_owner = models.CharField(
        max_length=100, help_text="Secondary repo owner"
    )
    secondary_repo_name = models.CharField(
        max_length=100, help_text="Secondary repo name"
    )
    secondary_repo_token = models.TextField(help_text="Access Token for secondary repo")
    secondary_repo_type = models.CharField(
        max_length=50, choices=RepoTypeChoices.choices, default=RepoTypeChoices.GITHUB
    )
    secondary_repo_project_name = models.CharField(
        max_length=100,
        help_text="Secondary Repo project name; If repo is bitbucket",
        null=True,
        blank=True,
    )
    secondary_repo_url = models.CharField(
        max_length=500, help_text="The url repository to be copied to"
    )

    @property
    def primary_repo_webhook_url(self):
        """Construct the primary repo webhook endpoint."""
        if self.primary_repo_type == RepoTypeChoices.GITHUB:
            url = settings.GITHUB_BASE_URL + "/repos/{owner}/{repo}/hooks"
        else:
            url = settings.BITBUCKET_BASE_URL + "/repositories/{owner}/{repo}/hooks"
        return url.format(owner=self.primary_repo_owner, repo=self.primary_repo_name)

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
