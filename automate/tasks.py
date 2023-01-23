import json

from celery import shared_task

from automate.choices import RepoTypeChoices
from automate.encryptor import Crypt
from automate.gitremote import GitRemote
from automate.models import History, Project
from automate.utils import add_hook_to_repo, refresh_bitbucket_token, log_activity
from repo.utils import MakeRequest, logger

crypt = Crypt()


@shared_task()
def add_hook_to_repo_task(project_webhook_url, user, project):
    """This tasks simply adds hook to repo."""
    add_hook_to_repo(project_webhook_url, user, project)


@shared_task()
def init_run_git(project, data):
    """This is a delayed method to initialize and run git processes"""
    git = GitRemote(instance=project, data=data)
    git.run()


@shared_task()
def check_new_comments():
    """I'd get all Open PRs that have not been closed."""
    open_pr = History.objects.filter(action="open", merged_at=None)

    # If there's an open PR then it would run a for-loop checking comments on all of them
    if open_pr:

        for pr in open_pr:
            # Setup headers
            primary_header = {"Authorization": f"Bearer {crypt.decrypt(pr.project.primary_repo_token)}"}
            secondary_header = {"Authorization": f"Bearer {crypt.decrypt(pr.project.secondary_repo_token)}"}

            # Urls
            primary_url = pr.primary_url
            secondary_url = pr.url

            # Initialize MakeRequest
            pri_req = MakeRequest(primary_url, primary_header)
            sec_req = MakeRequest(secondary_url, secondary_header)

            owner = pr.project.owner

            # Check if the secondary PR is github or bitbucket for merging operations
            if pr.project.secondary_repo_type == RepoTypeChoices.GITHUB.value:
                # Checks if secondary PR is merged
                response = sec_req.get()
                content = response.json()
                if content.get("merged"):
                    # Merge the primary PR and not proceed to updating comments
                    data = {
                        "commit_title": "Pull requests merged automatically.",
                        "commit_message": f"""This pull request has been merged from {pr.project.secondary_repo_name}
                                        ({secondary_url})""",
                    }
                    response = pri_req.put(data, json=True, url=pri_req.url + "/merge")

                    # Todo: get status code and break out
                    break  # steps out of the loop
            else:
                # Refresh Token
                credentials = {
                    "refresh_token": pr.project.secondary_refresh_token,
                    "client_id": pr.project.secondary_client_id,
                    "client_secret": pr.project.secondary_client_secret
                }
                credentials = crypt.multi_decrypt(credentials)
                new_token = refresh_bitbucket_token(credentials)
                new_header = {"Authorization": f"Bearer {new_token}"}
                # checks if secondary PR is merged
                req = MakeRequest(secondary_url, new_header)
                response = req.get()
                content = response.json()

                if content.get("state") == "MERGED":
                    # Here we merge the primary github account
                    merge_commit = content.get("merge_commit")["links"]
                    data = {
                        "commit_title": "Pull requests merged automatically.",
                        "commit_message": f"""This pull request has been merged from {pr.project.secondary_repo_name}
                                            ({merge_commit['self']} and {merge_commit['html']})""",
                    }
                    response = pri_req.put(data, json=True, url=pri_req.url + "/merge")
                    status_code = response.status_code
                    if status_code == 200:
                        # Update Open PR History
                        pr.action = "merged"
                        pr.merged_at = content.get("updated_on")
                        pr.save()

                        activity = f"`{owner}`; {pr.project.primary_repo_name} was automatically merged with {pr.project.secondary_repo_name}. Passed with response `{status_code}`"
                        log_activity(user=owner, activity=activity, project=pr.project, status=True)
                    else:
                        content = response.json()
                        activity = f"`{owner}`; {pr.project.primary_repo_name} couldn't merged with {pr.project.secondary_repo_name}. Failed with response `{status_code}`. Reason is :{content.get('message')}"
                        log_activity(user=owner, activity=activity, project=pr.project, status=True)
                    break

            if pr.project.secondary_repo_type == RepoTypeChoices.GITHUB.value:
                # Get the number of comments existing in the PR online
                response = sec_req.get(pr.url + "/comments")
                secondary_comments = json.loads(response.content)

                primary_response = pri_req.get(pri_req.url + "/comments")
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

                        #  Compares the sub_comment with the primary comment. If they are the same,
                        #  it increments the counter. If at the end of the loop there is no counter,
                        #  it means the comment doesn't exist and it should be added

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
                            response = pri_req.post(data=data, json=True)
                            status = response.status_code
                            if status == 201:
                                # Increment comments
                                pr.comments = len(comments_not_in_primary)
                                pr.save()
                                # log_activity(user=user, activity=activity, project=project, status=status_)
                        except AttributeError as err:
                            logger.error(err)
                            logger.critical(response)
