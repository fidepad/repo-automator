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
                secondary_header = {
                    "Authorization": f"Bearer {pr.project.secondary_token}"
                }
                primary_header = {"Authorization": f"Bearer {pr.project.primary_token}"}
                # Get the number of comments existing in the PR online
                response = requests.get(pr.url + "/comments", headers=secondary_header)
                secondary_comments = json.loads(response.content)

                primary_url = pr.primary_url + "/comments"
                primary_response = requests.get(primary_url, headers=primary_header)
                primary_comments = json.loads(primary_response.content)

                # Get's comments that are in the secondary that are not in the primary
                comments_not_in_primary = []
                for comment in secondary_comments:
                    # Reduced comparable comment body
                    sub_comment = {
                        "body": comment["body"],
                        "position": comment["position"],
                        "commit_id": comment["commit_id"],
                        "path": comment["path"],
                        "start_line": comment["start_line"],
                        "start_side": comment["start_side"],
                        "line": comment["line"],
                        "side": comment["side"],
                    }
                    # Run a loop going through all comments in the primary comments and ensuring they are the same
                    counter = 0

                    for pri_comment in primary_comments:
                        sub_primary_comment = {
                            "body": pri_comment["body"],
                            "position": pri_comment["position"],
                            "commit_id": pri_comment["commit_id"],
                            "path": pri_comment["path"],
                            "start_line": pri_comment["start_line"],
                            "start_side": pri_comment["start_side"],
                            "line": pri_comment["line"],
                            "side": pri_comment["side"],
                        }

                        """Compares the sub_comment with the primary comment. If they are the same, 
                        it increments the counter. If at the end of the loop there is no counter, it means
                        the comment doesn't exist and it should be added 
                        """
                        if sub_comment == sub_primary_comment:
                            counter += 1
                            break

                    if not counter:
                        comments_not_in_primary.append(comment)

                # Next we check if the length of the content (comments) matches the comment field
                if comments_not_in_primary:
                    # Update the primary PR with comments
                    for comment in comments_not_in_primary:
                        data = {
                            "body": comment["body"],
                            "position": comment["position"],
                            "commit_id": comment["commit_id"],
                            "path": comment["path"],
                            "start_line": comment["start_line"],
                            "start_side": comment["start_side"],
                            "line": comment["line"],
                            "side": comment["side"],
                        }
                        try:
                            response = requests.post(
                                primary_url, json=data, headers=primary_header
                            )
                            status = response.status_code
                            if status == 201:
                                # Increment comments
                                pr.comments = len(comments_not_in_primary)
                                pr.save()
                        except Exception as err:
                            print(err)  # Todo: Perform logging function here

                print(pr.action)
