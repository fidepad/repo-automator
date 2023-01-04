import os
import tempfile

import requests

from git import Repo


class GitRemote:
    """Git Remote Class to handle all git related activities."""

    # def __init__(self, primary_access, primary_url, branch_name, secondary_access, secondary_url, project, primary_type, secondary_type, repo):
    def __init__(self, instance, data):
        """The initialization point of the git remote class."""
        self.primary_access = instance.primary_access
        self.primary_url = instance.primary_repo_url
        self.primary_type = instance.primary_repo_type
        self.branch_name = data["pull_request"]['head']['ref']
        self.secondary_access = instance.secondary_access
        self.secondary_url = instance.secondary_repo_url
        self.secondary_repo = instance.secondary_repo.replace(" ", "-").lower()
        self.secondary_type = instance.secondary_repo_type
        self.repo = data["pull_request"]["head"]["repo"]["name"]
        self.title = data["pull_request"]["title"]
        self.body = data["pull_request"]["body"]
        self.action = data["action"]

    def clone(self, temp_dir):
        """This function clones the primary repository into a temporary folder."""
        # Todo: Create a username field for both primary and secondary repo
        # Todo: Change kramstyles to primary username
        clone_from = f"https://{self.primary_access}@github.com/kramstyles/{self.repo}"
        self.repository = Repo.clone_from(clone_from, temp_dir)

    def checkout(self):
        """This function checkouts to the new branch"""
        self.repository.git.checkout(self.branch_name)

    def push(self):
        """This function pushes the code to the secondary url"""
        if self.secondary_type == "github":
            push_to = self.secondary_url.replace("https://", f"https://{self.secondary_access}@")
            self.repository.create_remote("secondary", push_to)
            secondary = self.repository.remote("secondary")
            secondary.push()

    def make_pr(self):
        """THis method handles the creating of a new PR in the secondary repository."""
        headers = {
            "Authorization": f"Bearer {self.secondary_access}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        # Todo: Add base to the project
        # Todo: add owner for secondary repository to the project
        data = {
            "title": self.title,
            "body": self.body,
            "head": self.branch_name,
            "base": "main"
        }

        api_url = f"https://api.github.com/repos/kramstyles/{self.secondary_repo}/pulls"
        response = requests.post(api_url, headers=headers, json=data)
        status = response.status_code
        # Todo: use the response to populate history


    def run(self):
        if self.action == "closed":
            with tempfile.TemporaryDirectory() as parent_dir:
                self.clone(parent_dir)
                self.checkout()
                self.push()
                self.make_pr()
