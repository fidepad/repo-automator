from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    """Base Model to reduce redundant columns below."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Repository(BaseModel):
    """Repository Model."""

    class RepoType(models.TextChoices):
        """Repository Types."""

        GITHUB = "github", "Github"
        GITBUCKET = "gitbucket", "Gitbucket"

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
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
    slug = models.SlugField(max_length=250, unique=True, null=True)
    
    def save(self, *args, **kwargs):
        task_name = f"{self.primary_repo} {self.secondary_repo}"
        self.slug = slugify(task_name)
        super(Repository, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} Repository"


class History(BaseModel):
    """History Model to retain payload information."""

    pr_id = models.IntegerField()
    action = models.CharField(max_length=30, null=True)
    body = models.TextField()
    url = models.URLField()
    author = models.CharField(max_length=200)
    merged_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)
