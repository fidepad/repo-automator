import tempfile

import requests
from git import Repo

from automate.choices import RepoTypeChoices
from automate.encryptor import Crypt
from automate.models import History, Project
from automate.utils import log_activity, refresh_bitbucket_token

crypt = Crypt()


class GitRemote:
    """Git Remote Class to handle all git related activities."""

    def __init__(self, instance, data):
        """The initialization point of the git remote class."""

        self.primary_access = crypt.decrypt(instance.primary_repo_token)

        self.primary_url = instance.primary_repo_url
        self.primary_type = instance.primary_repo_type
        self.primary_user = instance.primary_repo_owner
        self.branch_name = data["pull_request"]["head"]["ref"]
        self.secondary_access = crypt.decrypt(instance.secondary_repo_token)

        self.secondary_url = instance.secondary_repo_url
        self.secondary_user = instance.secondary_repo_owner
        self.secondary_repo = instance.secondary_repo_name.replace(" ", "-").lower()
        self.secondary_type = instance.secondary_repo_type
        self.repo = data["pull_request"]["head"]["repo"]["name"]
        self.base = instance.base
        self.title = data["pull_request"]["title"]
        self.body = data["pull_request"]["body"]
        self.action = data["action"]
        self.pr_url = data["pull_request"]["url"]
        self.project = instance
        self.repository = None

    def clone(self, temp_dir):
        """This function clones the primary repository into a temporary folder."""
        clone_from = ""

        if self.primary_type == RepoTypeChoices.GITHUB:
            clone_from = self.primary_url.replace(
                "https://", f"https://oauth2:{self.primary_access}@"
            )
        elif self.primary_type == RepoTypeChoices.BITBUCKET:
            clone_from = self.primary_url.replace(
                f"https://{self.primary_user}",
                f"https://{self.primary_user}:{self.primary_access}",
            )

        self.repository = Repo.clone_from(clone_from, temp_dir)

    def checkout(self):
        """This function checkouts to the new branch."""
        self.repository.git.checkout(self.branch_name)

    def push(self):
        """This function pushes the code to the secondary url."""
        push_to = ""

        if self.secondary_type == RepoTypeChoices.GITHUB:
            push_to = self.secondary_url.replace(
                "https://", f"https://oauth2:{self.secondary_access}@"
            )

        elif self.secondary_type == RepoTypeChoices.BITBUCKET:
            # Due to bitbucket expiring token, we would always refresh bitbucket token here
            credentials = {
                "refresh_token": self.project.secondary_refresh_token,
                "client_id": self.project.secondary_client_id,
                "client_secret": self.project.secondary_client_secret,
            }
            credentials = crypt.multi_decrypt(credentials)
            self.secondary_access = refresh_bitbucket_token(credentials)

            push_to = self.secondary_url.replace(
                f"https://{self.secondary_user}",
                f"https://{self.secondary_user}:{self.secondary_access}",
            )

        self.repository.create_remote(self.secondary_repo, push_to)
        secondary = self.repository.remote(self.secondary_repo)
        secondary.push()

    def populate_history(self, content, project):
        """This function populates the history of PRs."""

        History.objects.create(
            project=project,
            pr_id=content.get("id"),
            action=content.get("state").lower(),
            body=content.get("body")
            if content.get("body")
            else content.get("description"),
            primary_url=self.pr_url,
            url=content.get("url")
            if content.get("url")
            else content.get("links")["self"]["href"],
            author=content.get("user")["login"]
            if content.get("user")
            else content.get("author")["display_name"],
            merged_at=content.get("merged_at") if content.get("merged_at") else None,
            closed_at=content.get("closed_at")
            if content.get("closed_at")
            else content.get("closed_by"),
        )

    def make_pr(self):
        """This method handles the creating of a new PR in the secondary repository."""
        user = Project.objects.get(name=self.project.name)
        user = user.owner
        bitflag = False
        headers = {
            "Authorization": f"Bearer {self.secondary_access}",
        }

        if self.secondary_type == RepoTypeChoices.GITHUB:
            data = {
                "title": self.title,
                "body": self.body,
                "head": self.branch_name,
                "base": self.base,
                "maintainer_can_modify": True,
                "allow_unrelated_histories": True,
            }

            api_url = f"https://api.github.com/repos/{self.secondary_user}/{self.secondary_repo}/pulls"

        elif self.secondary_type == RepoTypeChoices.BITBUCKET:
            bitflag = True
            data = {
                "title": self.title,
                "description": self.body,
                "source": {"branch": {"name": self.branch_name}},
                "destination": {"branch": {"name": self.base}},
                "close_source_branch": True,
                "merge_strategy": "merge_commit",
                "allow_unrelated_histories": True,
            }
            api_url = f"https://api.bitbucket.org/2.0/repositories/{self.secondary_user}/{self.secondary_repo}/pullrequests"

        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        status = response.status_code
        status_ = False
        project = Project.objects.get(id=self.project.id)
        if status == 201:
            status_ = True
            self.populate_history(response.json(), project)
            activity = f"`{user}` made a pull request to `{self.secondary_repo}` from project `{self.project.name}`"
        else:
            pr_res = response.json()
            if bitflag:
                # bitbucket error
                pr_res = pr_res.get("error").get("message")
            else:
                # github error
                pr_res = pr_res.get("errors")[0]["message"]

            activity = f"`{user}` made a pull request to `{self.secondary_repo}` failed with response `{pr_res}`"

        log_activity(user=user, activity=activity, project=project, status=status_)

    def run(self):
        """This function runs all functions required to clone, push and merge PRs."""
        if self.action == "closed":
            with tempfile.TemporaryDirectory() as parent_dir:
                self.clone(parent_dir)
                self.checkout()
                self.push()
                self.make_pr()
