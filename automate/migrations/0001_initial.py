# Generated by Django 3.2.16 on 2023-01-08 18:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the project", max_length=200, unique=True
                    ),
                ),
                ("slug", models.SlugField(blank=True, max_length=250, unique=True)),
                (
                    "primary_repo_owner",
                    models.CharField(help_text="Primary repo owner", max_length=100),
                ),
                (
                    "primary_repo_name",
                    models.CharField(help_text="Primary repo name", max_length=100),
                ),
                (
                    "primary_repo_token",
                    models.CharField(
                        help_text="Access Token for primary repo", max_length=100
                    ),
                ),
                (
                    "primary_repo_type",
                    models.CharField(
                        choices=[("github", "Github"), ("gitbucket", "Gitbucket")],
                        default="github",
                        max_length=50,
                    ),
                ),
                (
                    "primary_repo_project_name",
                    models.CharField(
                        blank=True,
                        help_text="Primary Repo project name; If repo is bitbucket",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "secondary_repo_owner",
                    models.CharField(help_text="Secondary repo owner", max_length=100),
                ),
                (
                    "secondary_repo_name",
                    models.CharField(help_text="Secondary repo name", max_length=100),
                ),
                (
                    "secondary_repo_token",
                    models.CharField(
                        help_text="Access Token for secondary repo", max_length=100
                    ),
                ),
                (
                    "secondary_repo_type",
                    models.CharField(
                        choices=[("github", "Github"), ("gitbucket", "Gitbucket")],
                        default="github",
                        max_length=50,
                    ),
                ),
                (
                    "secondary_repo_project_name",
                    models.CharField(
                        blank=True,
                        help_text="Secondary Repo project name; If repo is bitbucket",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
