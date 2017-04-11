from git import Repo
from user_manager.models import WorkbenchUser

REPO_DIR = 'github_repositories/'

def clone_git_repository(github_helper):
    repo_dir = get_repo_dir(github_helper)
    clone_url = github_helper.get_clone_url()
    Repo.clone_from(clone_url, repo_dir)

def pull_git_repository(github_helper):
    repo_dir = get_repo_dir(github_helper)
    repo = Repo(repo_dir)
    origin = repo.remotes.origin
    origin.pull()

def get_repo_dir(github_helper):
    return '{0}{1}/{2}'.format(REPO_DIR, github_helper.github_repository.owner.login, github_helper.github_repository.name)
