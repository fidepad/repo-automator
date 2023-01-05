import json

from celery import shared_task
import requests

from automate.models import History

@shared_task()
def check_new_comments():
    # I'd get all Open PRs that have not been closed
    open_pr = History.objects.filter(action="open", merged_at=None)

    # If there's an open PR then it would run a forloop checking comments on all of them
    if open_pr:
        for pr in open_pr:
            if pr.project.secondary_repo_type == "github":
                comments = pr.comments
                header = {
                    "Authorization": f"Bearer {pr.project.secondary_token}"
                }
                # Get the number of comments existing in the PR online
                response = requests.get(pr.url+"/comments", headers=header)
                content = json.loads(response.content)

                # Next we check if the length of the content (comments) matches the comment field
                if comments != len(content):
                    # Update the primary PR
                    primary_pr = pr.project.primary_repo_url # Todo: Find a way to get the primary pull url from the webhook url
                    for comment in content:
                        print(comment["url"])
                print(pr.action)
