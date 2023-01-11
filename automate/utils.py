import json

import requests

from automate.choices import RepoTypeChoices


# pylint: disable=duplicate-code
def add_hook_to_repo(project_webhook_url, webhook_url, repo_type, repo_token):
    """Add a webhook to a repository.

    Parameters:
        project_webhook_url (str): The URL of the webhook to be added to the repository.
        webhook_url (str): The URL of the repository's webhooks API endpoint.
        repo_type (RepoTypeChoices): The type of repository (GitHub or Bitbucket).
        repo_token (str): The token for authenticating the request to the repository's webhooks API.
    """
    if repo_type == RepoTypeChoices.GITHUB:
        # Modify webhook_url for github to find it. Change "Repo Name" to "repo-name" to suite git_url
        webhook_url = webhook_url.strip().replace(" ", "-").lower()
        payload = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "url": project_webhook_url,
                "content_type": "json",
                "insecure_ssl": "1",
            },
        }
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {repo_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    else:
        payload = {
            "description": "repo-automator-webhook",
            "url": project_webhook_url,
            "active": True,
            "events": [
                "pullrequest:created",
                "pullrequest:fulfilled",
                "repo:push", # NOTE: @Timizuo I noticed push was used here.
                "pullrequest:rejected",
                "pullrequest:updated",
            ],
            "skip_cert_verification": True,
        }
        headers = {
            "Authorization": f"Bearer {repo_token}",
        }
    # TODO: Would be nice to add this to an Activity Log, This way you know what fails
    #  and what passes. So that you can retry again.
    #  Also, Log status code


    requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers=headers,
        timeout=5,
    )
