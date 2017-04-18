from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from git_manager.models import GitRepository
from user_manager.models import get_workbench_user


def create_new_internal_package(experiment, step_folder, user):
    # create new GitHub repository
    github_helper_package = GitHubHelper(experiment.owner, experiment.git_repo.name, create=True)

    # create git repository in DB
    repo = github_helper_package.github_repository
    git_repo_obj = GitRepository()
    git_repo_obj.name = repo.name
    git_repo_obj.owner = get_workbench_user(user)
    git_repo_obj.github_url = repo.html_url
    git_repo_obj.save()

    # clone current experiment
    github_helper_experiment = GitHubHelper(experiment.owner, experiment.git_repo.name)
    git_helper = GitHelper(github_helper_experiment)
    git_helper.clone_repository()

    # take code from module and commit it to new repo
    git_helper.filter_and_checkout_subfolder(step_folder)
    new_remote = github_helper_package.get_clone_url()
    git_helper.set_remote(new_remote)
    git_helper.push_changes()
    return git_repo_obj
