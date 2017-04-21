import subprocess
import os
import shutil

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
        if not os.path.isdir(self.repo_dir):
            Repo.clone_from(clone_url, self.repo_dir)
        else:
            self.repo = Repo(self.repo_dir)
            self.pull_repository()

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
        folder_path = '{0}/{1}'.format(self.repo_dir, folder_name)
        current_path = '{0}'.format(self.repo_dir)
        dir_list = os.listdir(current_path)
        subprocess.call(['mkdir', folder_path])
        for file in dir_list:
            file_path = '{0}/{1}'.format(current_path, file)
            if os.path.isfile(file_path):
                shutil.move(file_path, folder_path)
                self.repo.git.rm(file)
        self.repo.git.add(folder_name)

    def set_remote(self, new_remote):
        subprocess.call(['git', 'remote', 'set-url', 'origin', new_remote], cwd=self.repo_dir)

    def push_changes(self):
        origin = self.repo.remotes.origin
        origin.push()
