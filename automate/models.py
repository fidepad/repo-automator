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
    primary_client_id = models.TextField(
        verbose_name="Primary Bitbucket ClientID", null=True
    )
    primary_client_secret = models.TextField(
        verbose_name="Primary Bitbucket Client Secret", null=True
    )
    primary_refresh_token = models.TextField(
        verbose_name="Primary Bitbucket Refresh Token", null=True
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
    secondary_client_id = models.TextField(
        verbose_name="Secondary Bitbucket ClientID", null=True
    )
    secondary_client_secret = models.TextField(
        verbose_name="Secondary Bitbucket Client Secret", null=True
    )
    secondary_refresh_token = models.TextField(
        verbose_name="Secondary Bitbucket Refresh Token", null=True
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
    body = models.TextField(null=True, blank=True)
    url = models.URLField(help_text="url link for the new PR")
    primary_url = models.URLField(help_text="url link for the initial PR")
    author = models.CharField(max_length=200)
    comments = models.IntegerField(default=0)
    merged_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.project}: {self.action}"


class ProjectActivities(models.Model):
    """Project Activities Model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    action = models.TextField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for Project Activities."""

        ordering = ("-created_at",)
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.action}"
