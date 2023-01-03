import os
import tempfile

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
        self.secondary_type = instance.secondary_repo_type
        self.repo = data["pull_request"]["head"]["repo"]["name"]

    def make_directory(self, project):
        """This function exists to create a temporary directory for the project and return the address."""
        with tempfile.TemporaryDirectory() as parent_dir:

            # path = os.path.join(parent_dir, "projects")
            # try:
            #     os.mkdir(path=path)
            # except FileExistsError:
            #     pass
            
            # This handles creating temporary directory
            try:
                path = os.path.join(parent_dir, project)
                os.mkdir(path=path)
                self.project = path
                self.run()
            except FileExistsError:
                pass

                # Had to remove the code below because it demands for permission
                # shutil.rmtree(path=path)
                # os.mkdir(path=path)
            # except FileNotFoundError:
            #     pass

            return path

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
        push_to = self.secondary_url.replace("https://", f"https://{self.secondary_access}@")
        self.repository.create_remote("secondary", push_to)
        # remotes = repository.remotes
        secondary = self.repository.remote("secondary")
        secondary.push()
        # Todo: Create and remove context directory. Also see if it's possible to create online branch here

    def run(self):
        with tempfile.TemporaryDirectory() as parent_dir:
            self.clone(parent_dir)
            self.checkout()
            self.push()
