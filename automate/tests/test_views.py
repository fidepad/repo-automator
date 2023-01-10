from django.shortcuts import reverse
from django.utils.text import slugify
from faker import Faker
from rest_framework.test import APITestCase
from unittest.mock import patch

from automate.factories import RepositoryFactory, UserFactory


fake = Faker()


class TestProject(APITestCase):
    """Test Project API Case."""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.repo1 = RepositoryFactory(owner=self.user)
        self.data = {
            "primary_repo": "Primary Repository",
            "primary_repo_url": "https://github.com/primary-repo.git",
            "primary_repo_type": "github",
            "secondary_repo": "Secondary Repository",
            "secondary_repo_url": "https://gitbucket.com/secondary-repo.git",
            "secondary_repo_type": "gitbucket",
        }
        self.url_list = reverse("repository:project-list")
        self.url_detail = reverse(
            "repository:project-detail", kwargs={"slug": self.repo1.slug}
        )

    def test_to_ensure_only_authenticated_users_can_access_endpoint(self):
        """Test to ensure user is logged in."""
        with self.subTest("Accessing project-list"):
            response = self.client.get(self.url_list)
            self.assertEqual(response.status_code, 401)

        with self.subTest("Accessing project-list"):
            response = self.client.get(self.url_detail)
            content = response.data
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                content.get("detail"), "Authentication credentials were not provided."
            )

    def test_to_fetch_repository(self):
        """This gets the project."""
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_list)
        content = response.data
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(content) == 1)

        with self.subTest("Test to ensure you only get projects you created"):
            user = UserFactory(username="anon")
            self.client.force_authenticate(user)
            response = self.client.get(self.url_list)
            content = response.data
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(content) == 0)

        with self.subTest("Ensuring name is provided when creating project"):
            response = self.client.post(self.url_list, data=self.data)
            content = response.data
            print(content)
            self.assertEqual(response.status_code, 400)
            self.assertContains(content, "This field is required")

        with self.subTest("Creating new Project with a different user"):
            self.data["name"] = "primary repository to secondary repository"
            response = self.client.post(self.url_list, data=self.data)
            content = response.data
            self.assertEqual(response.status_code, 201)
            self.assertIn("user", content)
            self.assertEqual(slugify(self.data.get("name")), content.get("slug"))

    def test_to_retrieve_and_update_project(self):
        """Test to Get and Updates project."""
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_detail)
        content = response.data
        self.assertEqual(self.repo1.name, content.get("name"))
        self.assertEqual(response.status_code, 200)

        with self.subTest("Update project"):
            response = self.client.patch(
                self.url_detail, data={"primary_repo_type": "gitbucket"}
            )
            content = response.data
            self.assertEqual("gitbucket", content.get("primary_repo_type"))


class TestWebhook(APITestCase):
    """Test for Webhook."""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.project = RepositoryFactory(owner=self.user)
        self.url = reverse(
            "repository:project-webhook", kwargs={"slug": self.project.slug}
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
        # this test throws a validation if webhook is called without data
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url)
        content = response.json()

        self.assertTrue(response.status_code == 400)
        self.assertEqual(content.get("action"), ["This field is required."])
        self.assertEqual(content.get("pull_request"), ["This field is required."])

    @patch("automate.gitremote.GitRemote.run")
    def test_to_ensure_webhook_works(self, run):
        self.client.force_authenticate(self.user)

        with patch("automate.gitremote.GitRemote.run") as mock_run:
            """This function exists to ensure the clone function was called after the webhook runs."""
            response = self.client.post(self.url, data=self.data, format="json")
            self.assertTrue(mock_run.called)

        content = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(content.get("action") == self.data.get("action"))
        self.assertTrue(
            content["pull_request"]["url"] == self.data["pull_request"]["url"]
        )
        self.assertEqual(
            content["pull_request"]["head"], self.data["pull_request"]["head"]
        )
