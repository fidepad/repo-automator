from django.conf import settings

from automate.choices import RepoTypeChoices
from automate.factories import ProjectFactory
from repo.testing.model import BaseModelTestCase


class ProjectTestCase(BaseModelTestCase):
    """Test class for Project model."""

    def test_primary_repo_webhook_url(self):
        """Test Project primary_repo_webhook_url method."""
        # Assert for GitHub
        project = ProjectFactory(primary_repo_type=RepoTypeChoices.GITHUB)
        self.assertEqual(
            project.primary_repo_webhook_url,
            settings.GITHUB_BASE_URL
            + f"/repos/{project.primary_repo_owner}/{project.primary_repo_name}/hooks",
        )
        # Assert for Bitbucket
        project = ProjectFactory(primary_repo_type=RepoTypeChoices.BITBUCKET)
        self.assertEqual(
            project.primary_repo_webhook_url,
            settings.BITBUCKET_BASE_URL
            + f"/repositories/{project.primary_repo_owner}/{project.primary_repo_name}/hooks",
        )
