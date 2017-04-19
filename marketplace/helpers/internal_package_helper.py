from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from git_manager.models import GitRepository
from user_manager.models import get_workbench_user


def create_new_internal_package(internal_package, experiment, step_folder, user):
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
    git_helper.move_repo_contents_to_folder(step_folder)
    new_remote = github_helper_package.get_clone_url()
    git_helper.set_remote(new_remote)
    git_helper.push_changes()

    # add boilerplate code, e.g. setup.py for pip
    create_setup_py(internal_package, experiment)

    return git_repo_obj


def create_setup_py(internal_package, experiment):
    pass