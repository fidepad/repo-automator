import json
from unittest import TestCase
from unittest.mock import patch

from rest_framework.reverse import reverse

from automate.choices import RepoTypeChoices
from automate.factories import ProjectFactory
from automate.utils import add_hook_to_repo
from repo.testing.model import BaseModelTestCase
from repo.utils import MakeRequest


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
                primary_repo_token="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",
                primary_repo_type=RepoTypeChoices.GITHUB,
            )
            url = "https://example.com" + reverse(
                "project:project-webhook", args=(project.slug,)
            )
            add_hook_to_repo(
                project_webhook_url=url,
                webhook_url=project.primary_repo_webhook_url,
                repo_type=RepoTypeChoices.GITHUB,
                repo_token=project.primary_repo_token,
            )

            expected_payload = {
                "name": "web",
                "active": True,
                "events": ["push", "pull_request"],
                "config": {
                    "url": url,
                    "content_type": "json",
                    "insecure_ssl": "1",
                },
            }
            expected_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {project.primary_repo_token}",
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
                primary_repo_token="PxXQEo5jkJR6utKdWqcI",
                primary_repo_type=RepoTypeChoices.BITBUCKET,
            )
            url = "https://example.com" + reverse(
                "project:project-webhook", args=(project.slug,)
            )

            expected_payload = {
                "description": "repo-automator-webhook",
                "url": url,
                "active": True,
                "events": [
                    "pullrequest:created",
                    "pullrequest:fulfilled",
                    "repo:push",
                    "pullrequest:rejected",
                    "pullrequest:updated",
                ],
                "skip_cert_verification": True,
            }
            expected_headers = {
                "Authorization": f"Bearer {project.primary_repo_token}",
            }
            add_hook_to_repo(
                project_webhook_url=url,
                webhook_url=project.primary_repo_webhook_url,
                repo_type=RepoTypeChoices.BITBUCKET,
                repo_token=project.primary_repo_token,
            )
            post_mock.assert_called_with(
                project.primary_repo_webhook_url,
                data=json.dumps(expected_payload),
                headers=expected_headers,
                timeout=3000,
            )


class TestMakeRequest(TestCase):
    """This tests the make request class"""

    def setUp(self):
        self.url = "https://httpbin.org/"  # This is an endpoint for testing requests
        self.headers = {"Content-Type": "application/json"}
        self.data = {"key": "value"}
        self.make_request = MakeRequest(self.url, self.headers)

    def test_get(self):
        response = self.make_request.get(self.url + "get")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["url"], self.url + "get")

    def test_post(self):
        response = self.make_request.post(self.data, json=True, url=self.url + "post")
        content = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["json"], self.data)

    def test_put(self):
        response = self.make_request.put(self.data, json=True, url=self.url + "put")
        content = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["json"], self.data)

    def test_that_exception_works(self):
        self.url = "https://examplebadnotworking.com/"
        self.make_request = MakeRequest(self.url)
        response = self.make_request.get()

        self.assertIn("HTTPSConnectionPool", response["data"]["error"])
