from django.db import transaction


from experiments_manager.consumers import send_exp_package_creation_status_update
from git_manager.views import create_new_github_repository
from git_manager.helpers.git_helper import GitHelper
from cookiecutter_manager.helpers.helper_cookiecutter import clone_cookiecutter_template
from git_manager.models import GitRepository
from requirements_manager.helper import parse_requirements_file


class ExperimentProgress(object):
    STEP_CREATING_GITHUB_REPO = 2
    STEP_CREATING_BOILERPLATE_CODE = 3
    STEP_PUSHING_BOILERPLATE_CODE = 4
    STEP_READING_DEPENDENCIES = 5
    STEP_CLEAN_UP = 6


def init_git_repo_for_experiment(experiment, cookiecutter):
    username = experiment.owner.user.username
    github_helper = create_new_github_repository(experiment.title, experiment.owner.user)
    send_exp_package_creation_status_update(username, ExperimentProgress.STEP_CREATING_GITHUB_REPO)
    repo = github_helper.github_repository
    repo_name = repo.name

    git_repo = GitRepository()
    git_repo.name = repo_name
    git_repo.owner = experiment.owner
    git_repo.github_url = repo.html_url

    with transaction.atomic():
        git_repo.save()
        experiment.git_repo = git_repo
        experiment.save()

    git_helper = GitHelper(github_helper)
    git_helper.clone_or_pull_repository()

    repo_dir = git_helper.repo_dir_of_user()

    clone_cookiecutter_template(cookiecutter, repo_dir, repo_name, experiment.owner, experiment.description)
    send_exp_package_creation_status_update(username, ExperimentProgress.STEP_CREATING_BOILERPLATE_CODE)

    git_helper.commit('Cookiecutter template added')
    git_helper.push()
    send_exp_package_creation_status_update(username, ExperimentProgress.STEP_PUSHING_BOILERPLATE_CODE)

    requirements_file = github_helper.view_file('requirements.txt')
    parse_requirements_file(experiment, requirements_file)
    send_exp_package_creation_status_update(username, ExperimentProgress.STEP_READING_DEPENDENCIES)





