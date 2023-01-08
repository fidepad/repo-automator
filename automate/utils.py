import logging

import requests
import json

from automate.choices import RepoTypeChoices


logger = logging.getLogger(__name__)


def add_hook_to_repo(project_webhook_url, webhook_url, repo_type, repo_token):
    if repo_type == RepoTypeChoices.GITHUB:
        payload = {
            "name": "Repo Automator Webhook",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "url": project_webhook_url,
                "content_type": "json",
                "insecure_ssl": "0",
            },
        }
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {repo_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    else:
        payload = {
            "description": "Repo Automator Webhook",
            "url": project_webhook_url,
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
        headers = {
            "Authorization": f"Bearer {repo_token}",
        }
    # TODO: Would be nice to add this to an Activity Log, This way you know what fails
    #  and what passes. So that you can retry again.
    try:
        requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        logger.warning(f"Webhook creation failed for {project_webhook_url}")


def gen_hook_url(username, repo_name):
    return f"https://domain.com/{username}/repo/hooks/{repo_name}/"
