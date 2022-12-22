import json

from django.conf import settings
from django.shortcuts import reverse
from rest_framework.test import APITestCase

from automate.factories import UserFactory, RepositoryFactory


class TestRepository(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.repo1 = RepositoryFactory(owner=self.user)
        self.data = {
            "primary_repo": "Primary Repository",
            "primary_repo_url": "https://github.com/primary-repo.git",
            "primary_repo_type": "github",
            "secondary_repo": "Secondary Repository",
            "secondary_repo_url": "https://gitbucket.com/secondary-repo.git",
            "secondary_repo_type": "gitbucket"
        }
        self.url_list = reverse("repository:repository-list")
        self.url_detail = reverse("repository:repository-detail", kwargs={"slug": self.repo1.slug})

    def test_to_ensure_only_authenticated_users_can_access_endpoint(self):
        with self.subTest("Accessing notification-list"):
            response = self.client.get(self.url_list)
            self.assertEqual(response.status_code, 401)

        with self.subTest("Accessing notification-detail"):
            response = self.client.get(self.url_detail)
            content = json.loads(response.content)
            self.assertEqual(response.status_code, 401)
            self.assertIn('detail', content)
            self.assertEqual(content.get('detail'), "Authentication credentials were not provided.")

    def test_to_fetch_repository(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_list)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(content) > 0)

        with self.subTest("Test to ensure you only get projects you created"):
            user = UserFactory(username="anon")
            self.client.force_authenticate(user)
            response = self.client.get(self.url_list)
            content = json.loads(response.content)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(content) == 0)

        with self.subTest("Creating new Project with a different user"):
            response = self.client.post(self.url_list, data=self.data)
            content = json.loads(response.content)
            self.assertEqual(response.status_code, 201)
            self.assertIn("user", content)
            self.assertEqual("primary-repository-to-secondary-repository", content.get("slug"))

    def test_to_retrieve_and_update_project(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_detail)
        content = json.loads(response.content)
        self.assertIn('user', content)
        self.assertIn('primary_repo', content)

        with self.subTest("Update project"):
            response = self.client.patch(self.url_detail, data={"primary_repo_type": "gitbucket"})
            content = json.loads(response.content)
            self.assertEqual("gitbucket", content.get("primary_repo_type"))
