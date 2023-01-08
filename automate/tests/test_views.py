from unittest.mock import patch

from django.shortcuts import reverse

from automate.choices import RepoTypeChoices
from automate.factories import ProjectFactory
from accounts.factories import UserFactory
from automate.models import Project
from repo.testing.api import BaseAPITestCase


class ProjectAPITestCase(BaseAPITestCase):
    """Test Project API Case."""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.repo1 = ProjectFactory(owner=self.user)
        self.data = {
            "name": "Test Project",
            "primary_repo_owner": "test-owner",
            "primary_repo_name": "test-name",
            "primary_repo_token": "11223344",
            "primary_repo_type": RepoTypeChoices.GITHUB.value,
            "secondary_repo_owner": "sec-owner",
            "secondary_repo_name": "sec-name",
            "secondary_repo_token": "2353w423",
            "secondary_repo_type": RepoTypeChoices.BITBUCKET.value,
        }
        self.url_list = reverse("project:project-list")
        self.url_detail = reverse(
            "project:project-detail", kwargs={"slug": self.repo1.slug}
        )

    def test_to_ensure_only_authenticated_users_can_access_endpoint(self):
        """Test to ensure user is logged in."""
        with self.subTest("Accessing project-list"):
            response = self.unauthenticated_client.get(self.url_list)
            self.assertEqual(response.status_code, 401)

        with self.subTest("Accessing project-detail"):
            response = self.unauthenticated_client.get(self.url_detail)
            content = response.data
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                content.get("detail"), "Authentication credentials were not provided."
            )

    def test_to_fetch_project(self):
        """This gets the project."""
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_list)
        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(content) == 1)

        with self.subTest("Test to ensure you only get projects you created"):
            user = UserFactory(email="adam@a.com")
            client = self.authenticate_client(user)
            response = client.get(self.url_list)
            content = response.data
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(content) == 0)

    @patch("automate.serializers.add_hook_to_repo")
    def test_create_project(self, add_hook_to_repo_mock):
        response = self.client.post(self.url_list, data=self.data)
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(response.data["name"], project.name)
        self.assertEqual(response.data["owner"]["email"], project.owner.email)

        # Assert add Hook to repo function gets called with the right parameters
        add_hook_to_repo_mock.assert_called_with(
            project_webhook_url="http://testserver"
            + reverse("project:project-webhook", args=[project.slug]),
            webhook_url=project.primary_repo_webhook_url,
            repo_type=project.primary_repo_type,
            repo_token=project.primary_repo_token,
        )

    def test_to_retrieve_and_update_project(self):
        """Test to Get and Updates project."""
        response = self.client.get(self.url_detail)
        content = response.data
        self.assertEqual(self.repo1.name, content.get("name"))
        self.assertEqual(response.status_code, 200)

        with self.subTest("Update project"):
            response = self.client.patch(
                self.url_detail,
                data={"primary_repo_type": RepoTypeChoices.BITBUCKET.value},
            )
            content = response.data
            self.assertEqual(
                RepoTypeChoices.BITBUCKET.value, content.get("primary_repo_type")
            )
