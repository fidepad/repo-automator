import json

import requests
from requests import (
    ConnectionError as RequestError,
    Timeout as ResponseTimeout,
    ConnectTimeout as RequestTimeout,
)

from accounts.models import User
from automate.models import ProjectActivities, Project
from automate.choices import RepoTypeChoices
from automate.encryptor import Crypt
from repo.utils import MakeRequest

crypt = Crypt()


def log_activity(user, activity, project, status=None):
    ProjectActivities.objects.create(
        user=user, project=project, action=activity, status=status
    )
    return


# pylint: disable=duplicate-code


def clean_url(url):
    return url.replace(" ", "-").strip().lower()


def add_hook_to_repo(project_webhook_url, user, project_data):
    """Add a webhook to a repository.
    Parameters:
        project_webhook_url (str): The URL of the webhook to be added to the repository.
        project (Project): The newly created project.
        user (User): User attached to the project.
    """
    # Decrypt access tokens
    project_data["primary_repo_token"] = crypt.decrypt(project_data["primary_repo_token"])
    project_data["secondary_repo_token"] = crypt.decrypt(project_data["secondary_repo_token"])

    if project_data["primary_repo_type"] == RepoTypeChoices.GITHUB:
        # Modify webhook_url for github to find it. Change "Repo Name" to "repo-name" to suite git_url
        webhook_url = f"https://api.github.com/repos/{project_data['primary_repo_owner']}/{project_data['primary_repo_name']}/hooks"
        webhook_url = clean_url(webhook_url)
        payload = {
            "name": "web",
            "active": True,
            "events": ["pull_request"],
            "config": {
                "url": project_webhook_url,
                "content_type": "json",
                "insecure_ssl": "1",
            },
        }
        not_allowed = ["127.0.0.1", "localhost", "0.0.0.0"]
        # Modify payload url if it's localhost to not fail validation
        for host in not_allowed:
            if host in payload["config"]["url"]:
                # Get the remaining endpoint after localhost
                url = project_webhook_url[21:]
                payload["config"]["url"] = "https://localtestsite.com" + url
                break  # To stop the loop

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {project_data['primary_repo_token']}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    else:

        webhook_url = f"https://api.bitbucket.org/2.0/workspaces/{project_data['primary_repo_name']}/hooks"
        payload = {
            "description": f"Auto webhook to {project_data['secondary_repo_name']}",
            "url": "%s" % project_webhook_url,
            "active": True,
            "events": ["repo:push", "issue:created", "issue:updated"],
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {project_data['primary_repo_token']}",
        }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=3000,
        )
    except (RequestError, RequestTimeout, ResponseTimeout):
        response = None
    if response:
        status = False
        user = User.objects.get(email=user)
        project = Project.objects.get(id=project_data["id"])
        activity = f"{user} initialized a project, webhook create status -> {response.status_code}"
        if response.status_code in [200, 201]:

            status = True
        log_activity(user=user, activity=activity, status=status, project=project)

    return response


def refresh_bitbucket_token(credentials: dict):
    """This function accepts a dictionary of credentials needed to generate a new access token."""
    url = "https://bitbucket.org/site/oauth2/access_token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": credentials["refresh_token"],
        "client_id": credentials["client_id"],
        "client_secret": credentials["client_secret"],
    }
    req = MakeRequest(url)
    response = req.post(data)
    content = response.json()
    status = response.status_code
    if status == 200:
        return content.get("access_token")
    else:
        return content
