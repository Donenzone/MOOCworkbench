import os
import shutil
import subprocess

from django.conf import settings
from django.utils.crypto import get_random_string
from git import Repo


class GitHelper(object):
    """GitHelper helps with common git functions"""

    BASE_REPO_DIR = 'github_repositories/'

    def __init__(self, github_helper):
        """Initialize a GitHelper
        The GitHelper uses a string of length 5 as a random key to ensure no other tasks interfer with the repo
        :param github_helper: GitHubHelper for the repository for which to provide Git helper functions"""
        self.github_helper = github_helper
        self.temporary_key = get_random_string(5)

        if os.path.isdir(self.repo_dir):
            self.repo = Repo(self.repo_dir)

    @property
    def repo_dir(self):
        """Get the repository directory for this Git repo"""
        return os.path.join(settings.PROJECT_ROOT, self.BASE_REPO_DIR,
                            self.github_helper.github_repository.owner.login,
                            self.temporary_key,
                            self.github_helper.github_repository.name)

    def repo_dir_of_user(self):
        """Get the directory of the user where Git repositories are placed"""
        return os.path.join(settings.PROJECT_ROOT, self.BASE_REPO_DIR,
                            self.github_helper.github_repository.owner.login, self.temporary_key)

    def clone_or_pull_repository(self):
        """Clone a non-existing repository, or, if the repository is already cloned, pull it"""
        clone_url = self.github_helper.get_clone_url()
        if not os.path.isdir(self.repo_dir):
            self.repo = Repo.clone_from(clone_url, self.repo_dir)
        else:
            self.repo = Repo(self.repo_dir)
            self.pull()

    def switch_to_branch(self, branch_name):
        """Switch to an existing branch
        :param branch_name: Name of branch to switch to"""
        subprocess.call(['git', 'checkout', branch_name], cwd=self.repo_dir)

    def create_branch(self, branch_name):
        """Create a new branch
        :param branch_name: Name of branch to create"""
        new_branch = self.repo.create_head(branch_name)
        assert self.repo.active_branch != new_branch

    def set_remote(self, new_remote):
        """Set a new remote for the Git repository
        :param new_remote: The remote URL to set"""
        subprocess.call(['git', 'remote', 'set-url', 'origin', new_remote], cwd=self.repo_dir)

    def pull(self):
        """Pull changes in a git repository"""
        origin = self.repo.remotes.origin
        origin.pull()

    def commit(self, message):
        """
        Commits all unstaged files in the repository
        :param message: The commit message
        """
        self.repo.git.add('.')
        self.repo.index.commit(message)

    def push(self):
        """Push commits in this Git repository"""
        origin = self.repo.remotes.origin
        origin.push()

    def filter_and_checkout_subfolder(self, folder_name):
        """Filters the existing folder and creates a subtree,
        so that the repository only contains that files and folders in that folder at /"""
        if folder_name.startswith('/'):
            folder_name = folder_name[1:]
        subprocess.call(['git', 'filter-branch', '--prune-empty', '--subdirectory-filter', folder_name, 'master'],
                        cwd=self.repo_dir)

    def move_repo_contents_to_folder(self, folder_name):
        """Move the contents of the repository into a folder"""
        if '/' in folder_name:
            folder_name = folder_name.split('/')
            folder_name = folder_name[-1]
        new_folder_path = os.path.join(self.repo_dir, folder_name)
        dir_list = os.listdir(self.repo_dir)
        subprocess.call(['mkdir', new_folder_path])
        for file in dir_list:
            file_path = os.path.join(self.repo_dir, file)
            if os.path.isfile(file_path):
                shutil.move(file_path, new_folder_path)
                self.repo.git.rm(file)
        self.repo.git.add(folder_name)


def clean_up_after_git_helper(git_helper):
    """Clean up after a GitHelper, by removing the repository directory
    as well as the temporary key directory that was created.
    :param git_helper: The GitHelper to clean-up for"""
    repo_dir = git_helper.repo_dir
    key_dir = git_helper.repo_dir_of_user()
    git_helper = None
    shutil.rmtree(repo_dir)
    shutil.rmtree(key_dir)
