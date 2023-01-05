import tempfile
import json

import requests

from git import Repo

from automate.models import History


class GitRemote:
    """Git Remote Class to handle all git related activities."""

    def __init__(self, instance, data):
        """The initialization point of the git remote class."""
        self.primary_access = instance.primary_token  # Todo: (Mark) Decrypt key here
        self.primary_url = instance.primary_repo_url
        self.primary_type = instance.primary_repo_type
        self.primary_user = instance.primary_username
        self.branch_name = data["pull_request"]["head"]["ref"]
        self.secondary_access = (
            instance.secondary_token
        )  # Todo: (Mark) Decrypt key here
        self.secondary_url = instance.secondary_repo_url
        self.secondary_user = instance.secondary_username
        self.secondary_repo = instance.secondary_repo.replace(" ", "-").lower()
        self.secondary_type = instance.secondary_repo_type
        self.repo = data["pull_request"]["head"]["repo"]["name"]
        self.base = instance.base
        self.title = data["pull_request"]["title"]
        self.body = data["pull_request"]["body"]
        self.action = data["action"]
        self.project = instance

    def clone(self, temp_dir):
        """This function clones the primary repository into a temporary folder."""
        # clone_from = f"https://{self.primary_access}@github.com/{self.primary_user}/{self.repo}"
        clone_from = self.primary_url.replace(
            "https://", f"https://oauth2:{self.primary_access}@"
        )
        self.repository = Repo.clone_from(clone_from, temp_dir)

    def checkout(self):
        """This function checkouts to the new branch"""
        self.repository.git.checkout(self.branch_name)

    def push(self):
        """This function pushes the code to the secondary url"""
        if self.secondary_type == "github":
            push_to = self.secondary_url.replace(
                "https://", f"https://oauth2:{self.secondary_access}@"
            )
            self.repository.create_remote("secondary", push_to)
            secondary = self.repository.remote("secondary")
            secondary.push()

    def populate_history(self, content):
        # This function populates the history of PRs
        if content:
            content = json.loads(content)
            History.objects.create(
                project=self.project,
                pr_id=content.get("id"),
                action=content.get("state"),
                body=content.get("body"),
                url=content.get("url"),
                author=content["user"]["login"],
                merged_at=content.get("merged_at"),
                closed_at=content.get("closed_at"),
            )

    def make_pr(self):
        """THis method handles the creating of a new PR in the secondary repository."""
        headers = {
            "Authorization": f"Bearer {self.secondary_access}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        data = {
            "title": self.title,
            "body": self.body,
            "head": self.branch_name,
            "base": self.base,
        }

        api_url = f"https://api.github.com/repos/{self.secondary_user}/{self.secondary_repo}/pulls"
        response = requests.post(api_url, headers=headers, json=data)
        status = response.status_code
        if status == 201:
            self.populate_history(response.content)

    def run(self):
        if self.action == "closed":
            with tempfile.TemporaryDirectory() as parent_dir:
                self.clone(parent_dir)
                self.checkout()
                self.push()
                self.make_pr()
