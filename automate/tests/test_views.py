from unittest.mock import patch

from django.shortcuts import reverse
from faker import Faker

from automate.choices import RepoTypeChoices
from automate.factories import ProjectFactory, UserFactory
from automate.models import Project
from automate.serializers import ProjectSerializer
from repo.testing.api import BaseAPITestCase

fake = Faker()


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
            "primary_repo_url": fake.url(),
            "primary_repo_type": RepoTypeChoices.GITHUB.value,
            "base": "main",
            "secondary_repo_owner": "sec-owner",
            "secondary_repo_name": "sec-name",
            "secondary_repo_token": "2353w423",
            "secondary_repo_type": RepoTypeChoices.BITBUCKET.value,
            "secondary_repo_url": fake.url(),
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

    @patch("automate.tasks.add_hook_to_repo_task.delay")
    @patch("automate.serializers.ProjectSerializer.validate_repo")
    def test_create_project(self, validate_repo_mock, add_hook_to_repo_mock):
        """Test creating of a project."""
        response = self.client.post(self.url_list, data=self.data)
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(response.data["name"], project.name)
        self.assertEqual(response.data["owner"]["email"], project.owner.email)

        # Assert add Hook to repo function gets called with the right parameters
        project_ = ProjectSerializer(project)
        add_hook_to_repo_mock.assert_called_with(
            "http://testserver"
            + reverse("project:project-webhook", args=[project.slug]),
            self.user.email,
            project_.data,
        )

        self.assertTrue(validate_repo_mock.called)

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


class TestWebhook(BaseAPITestCase):
    """Test for Webhook."""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.project = ProjectFactory(owner=self.user)
        self.url = reverse(
            "project:project-webhook", kwargs={"slug": self.project.slug}
        )
        self.data = {
            "action": "closed",
            "pull_request": {
                "id": fake.random_number(9),
                "url": fake.url(),
                "state": "closed",
                "title": fake.text(30),
                "body": fake.sentence(30),
                "head": {"ref": fake.text(15), "repo": {"name": fake.text(10)}},
            },
        }

    def test_to_ensure_webhook_gets_data(self):
        """this test throws a validation if webhook is called without data."""
        response = self.client.post(self.url)
        content = response.json()

        self.assertTrue(response.status_code == 400)
        self.assertEqual(content.get("action"), ["This field is required."])
        self.assertEqual(content.get("pull_request"), ["This field is required."])

    @patch("automate.tasks.init_run_git.delay")
    def test_to_ensure_webhook_works(self, run):
        """This is a mocked test to ensure our webhook works."""
        response = self.client.post(self.url, data=self.data, format="json")
        content = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(content.get("action") == self.data.get("action"))
        self.assertTrue(
            content["pull_request"]["url"] == self.data["pull_request"]["url"]
        )
        self.assertEqual(
            content["pull_request"]["head"], self.data["pull_request"]["head"]
        )
        self.assertTrue(run.called)
