import subprocess
import os

from git import Repo

REPO_DIR = 'github_repositories/'


class GitHelper(object):

    def __init__(self, github_helper):
        self.github_helper = github_helper
        self.repo_dir = self.get_repo_dir()

        if os.path.isdir(self.repo_dir):
            self.repo = Repo(self.repo_dir)

    def clone_repository(self):
        clone_url = self.github_helper.get_clone_url()
        Repo.clone_from(clone_url, self.repo_dir)
        self.repo = Repo(self.repo_dir)

    def pull_repository(self):
        origin = self.repo.remotes.origin
        origin.pull()

    def get_repo_dir(self):
        return '{0}{1}/{2}'.format(REPO_DIR, self.github_helper.github_repository.owner.login, self.github_helper.github_repository.name)

    def create_branch(self, branch_name):
        new_branch = self.repo.create_head(branch_name)
        assert self.repo.active_branch != new_branch

    def filter_and_checkout_subfolder(self, folder_name):
        subprocess.call(['git', 'filter-branch', '--prune-empty', '--subdirectory-filter', folder_name, 'master'], cwd=self.repo_dir)

    def move_repo_contents_to_folder(self, folder_name):
        subprocess.call(['mv', '.', folder_name], cwd=self.repo_dir)

    def set_remote(self, new_remote):
        subprocess.call(['git', 'remote', 'set-url', 'origin', new_remote], cwd=self.repo_dir)

    def push_changes(self):
        origin = self.repo.remotes.origin
        origin.push()
