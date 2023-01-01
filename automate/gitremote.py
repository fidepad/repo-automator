import os, shutil

from git import Repo

primary_access=""
primary_url = "".format(primary_access)
branch_name = ""
secondary_access=""
secondary_url = ""


class GitRemote:
    """Git Remote Class to handle all git related activities."""

    def __init__(self, primary_access, primary_url, branch_name, secondary_access, secondary_url, project):
        """The initialization point of the git remote class."""
        self.primary_access = primary_access
        self.primary_url = primary_url
        self.branch_name = branch_name
        self.secondary_access = secondary_access
        self.secondary_url = secondary_url
        self.project = self.make_directory(project)

    def make_directory(self, project):
        """This function exists to create a temporary directory for the project and return the address."""
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir, "projects")
        try:
            os.mkdir(path=path)
        except FileExistsError:
            shutil.rmtree(path=path)
            os.mkdir(path=path)
        
        # This handles creating temporary directory
        try:
            path = os.path.join(path, self.project)
            os.mkdir(path=path)
        except FileExistsError:
            shutil.rmtree(path=path)
            os.mkdir(path=path)
        except FileNotFoundError:
            pass

        return path

    def clone(self):
        """This function clones the primary repository into a temporary folder."""
        repository = Repo.clone_from(self.primary_url, self.project)
        return repository

    def checkout(self):
        """This function checkouts to the new branch"""
        repository = self.clone()
        repository.git.checkout(self.branch_name)
        return repository
