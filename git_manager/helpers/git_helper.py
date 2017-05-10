import subprocess
import os
import shutil

from django.conf import settings

from git import Repo


class GitHelper(object):

    BASE_REPO_DIR = 'github_repositories/'

    def __init__(self, github_helper):
        self.github_helper = github_helper

        if os.path.isdir(self.repo_dir):
            self.repo = Repo(self.repo_dir)

    @property
    def repo_dir(self):
        return os.path.join(settings.PROJECT_ROOT, self.BASE_REPO_DIR,
                            self.github_helper.github_repository.owner.login,
                            self.github_helper.github_repository.name)

    def repo_dir_of_user(self):
        return os.path.join(settings.PROJECT_ROOT, self.BASE_REPO_DIR,
                            self.github_helper.github_repository.owner.login)

    def clone_or_pull_repository(self):
        clone_url = self.github_helper.get_clone_url()
        if not os.path.isdir(self.repo_dir):
            self.repo = Repo.clone_from(clone_url, self.repo_dir)
        else:
            self.repo = Repo(self.repo_dir)
            self.pull()

    def create_branch(self, branch_name):
        new_branch = self.repo.create_head(branch_name)
        assert self.repo.active_branch != new_branch

    def set_remote(self, new_remote):
        subprocess.call(['git', 'remote', 'set-url', 'origin', new_remote], cwd=self.repo_dir)

    def pull(self):
        origin = self.repo.remotes.origin
        origin.pull()

    def commit(self, message):
        """
        Commits all unstaged files in the repository
        :param message: The commit message
        :return: 
        """
        self.repo.git.add('--all')
        self.repo.index.commit(message)

    def push(self):
        origin = self.repo.remotes.origin
        origin.push()

    def filter_and_checkout_subfolder(self, folder_name):
        if folder_name.startswith('/'):
            folder_name = folder_name[1:]
        subprocess.call(['git', 'filter-branch', '--prune-empty', '--subdirectory-filter', folder_name, 'master'], cwd=self.repo_dir)

    def move_repo_contents_to_folder(self, folder_name):
        if '/' in folder_name:
            folder_name = folder_name.split('/')
            folder_name = folder_name[-1]
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
