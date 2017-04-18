from git import Repo
from user_manager.models import WorkbenchUser
import subprocess

REPO_DIR = 'github_repositories/'

def GitHelper(object):
    def __init__(github_helper):
        self.github_helper = github_helper
        self.repo_dir = get_repo_dir(self.github_helper)
        self.repo = Repo(repo_dir)

    def clone_repository():
        clone_url = github_helper.get_clone_url()
        Repo.clone_from(clone_url, self.repo_dir)

    def pull_repository():
        origin = self.repo.remotes.origin
        origin.pull()

    def get_repo_dir():
        return '{0}{1}/{2}'.format(REPO_DIR, self.github_helper.github_repository.owner.login, self.github_helper.github_repository.name)

    def create_branch(branch_name):
        new_branch = self.repo.create_head(branch_name)
        assert repo.active_branch != new_branch

    def filter_and_checkout_subfolder(folder_name, branch_name):
        subprocess.call(['git', 'filter-branch', '--prune-empty', '--subdirectory-filter', folder_name, branch_name])

    def set_remote(new_remote):
        subprocess.call(['git', 'remote', 'set-url', 'origin', new_remote])

    def push_changes():
        origin = self.repo.remotes.origin
        origin.push()
