import json
from unittest import TestCase
from unittest.mock import patch

from rest_framework.reverse import reverse

from automate.choices import RepoTypeChoices
from automate.encryptor import Crypt
from automate.factories import ProjectFactory
from automate.serializers import ProjectSerializer
from automate.utils import add_hook_to_repo
from repo.testing.model import BaseModelTestCase
from repo.utils import MakeRequest

crypt = Crypt()


class ProjectUtilsTestCase(BaseModelTestCase):
    """Test class for Project utils."""

    @patch("automate.utils.requests.post")
    def test_add_hook_to_repo(self, post_mock):
        """Assert add_hook_to_repo is called with the expected data."""
        # Assert for GitHub
        with self.subTest("Assert GitHub Webhook creation"):
            project = ProjectFactory(
                primary_repo_owner="fidepad",
                primary_repo_name="primary",
                primary_repo_token=crypt.encrypt("I really want to swear here!"),
                secondary_repo_token=crypt.encrypt("Hello World. Remember me?"),
                primary_repo_type=RepoTypeChoices.GITHUB,
            )
            url = "https://example.com" + reverse(
                "project:project-webhook", args=(project.slug,)
            )
            project_ = ProjectSerializer(project)
            add_hook_to_repo(
                project_webhook_url=url,
                user=project.owner.email,
                project_data=project_.data,
            )

            expected_payload = {
                "name": "web",
                "active": True,
                "events": ["pull_request"],
                "config": {
                    "url": url,
                    "content_type": "json",
                    "insecure_ssl": "1",
                },
            }
            expected_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {crypt.decrypt(project.primary_repo_token)}",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            post_mock.assert_called_with(
                project.primary_repo_webhook_url,
                data=json.dumps(expected_payload),
                headers=expected_headers,
                timeout=3000,
            )

        with self.subTest("Assert BitBucket Webhook creation"):
            project = ProjectFactory(
                primary_repo_owner="automator-git",
                primary_repo_name="secondary-2",
                primary_repo_token=crypt.encrypt("expired token"),
                secondary_repo_token=crypt.encrypt("repo-automator"),
                primary_repo_type=RepoTypeChoices.BITBUCKET,
            )
            url = "https://example.com" + reverse(
                "project:project-webhook", args=(project.slug,)
            )

            expected_headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {crypt.decrypt(project.primary_repo_token)}",
            }
            project_ = ProjectSerializer(project)
            add_hook_to_repo(
                project_webhook_url=url,
                user=project.owner.email,
                project_data=project_.data,
            )
            expected_payload = {
                "description": f"Auto webhook to {project_.data['secondary_repo_name']}",
                "url": url,
                "active": True,
                "events": [
                    "pullrequest:created",
                    "pullrequest:fulfilled",
                    "pullrequest:rejected",
                    "pullrequest:updated",
                    "repo:push",
                    "issue:created",
                    "issue:updated",
                ],
                "skip_cert_verification": True,
            }
            post_mock.assert_called_with(
                project.primary_repo_webhook_url.replace(
                    "repositories/automator-git", "workspaces"
                ),
                data=json.dumps(expected_payload),
                headers=expected_headers,
                timeout=3000,
            )


class TestMakeRequest(TestCase):
    """This tests the make request class."""

    def setUp(self):
        self.url = "https://httpbin.org/"  # This is an endpoint for testing requests
        self.headers = {"Content-Type": "application/json"}
        self.data = {"key": "value"}
        self.make_request = MakeRequest(self.url, self.headers)

    def test_get(self):
        """Test for the get request."""
        response = self.make_request.get(self.url + "get")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["url"], self.url + "get")

    def test_post(self):
        """Test for the post request."""
        response = self.make_request.post(self.data, json=True, url=self.url + "post")
        content = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["json"], self.data)

    def test_put(self):
        """Test for the put request."""
        response = self.make_request.put(self.data, json=True, url=self.url + "put")
        content = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["json"], self.data)

    def test_that_exception_works(self):
        """Test to ensure exceptions are handled."""
        self.url = "https://examplebadnotworking.com/"
        self.make_request = MakeRequest(self.url)
        response = self.make_request.get()

        self.assertIn("HTTPSConnectionPool", response["data"]["error"])
