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
                new_comments = len(content)

                # Next we check if the length of the content (comments) matches the comment field
                if comments < new_comments:
                    # Update the primary PR
                    primary_url = pr.primary_url + "/comments"
                    # Reduce comments so it only runs a loop for new comments
                    # content = content[new_comments - comments:]
                    for comment in content:
                        data = {
                                "body": comment["body"],
                                "position": comment["position"],
                                "commit_id": comment["commit_id"],
                                "path": comment["path"],
                                "start_line": comment["start_line"],
                                "start_side": comment["start_side"],
                                "line": comment["line"],
                                "side": comment["side"]
                            }
                        try:
                            response = requests.post(primary_url, json=data, headers=header)
                            status = response.status_code
                            if status == 201:
                                # Increment comments
                                pr.comments = comments + 1
                                pr.save()
                        except Exception as err:
                            print(err)  # Todo: Perform logging function here

                print(pr.action)
