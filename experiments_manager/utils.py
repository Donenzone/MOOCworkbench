from django.db import transaction

from git_manager.views import create_new_github_repository
from git_manager.helpers.git_helper import GitHelper
from cookiecutter_manager.helpers.helper_cookiecutter import clone_cookiecutter_template
from git_manager.models import GitRepository
from requirements_manager.helper import parse_requirements_file


def init_git_repo_for_experiment(experiment, cookiecutter):
    github_helper = create_new_github_repository(experiment.title, experiment.owner.user)
    repo = github_helper.github_repository

    git_repo = GitRepository()
    git_repo.name = repo.name
    git_repo.owner = experiment.owner
    git_repo.github_url = repo.html_url

    with transaction.atomic():
        git_repo.save()
        experiment.git_repo = git_repo
        experiment.save()

    git_helper = GitHelper(github_helper)
    git_helper.clone_repository()

    repo_dir = git_helper.repo_dir_of_user()
    repo_name = github_helper.repo_name

    clone_cookiecutter_template(cookiecutter, repo_dir, repo_name, experiment.owner, experiment.description)

    git_helper.commit('Cookiecutter template added')
    #git_helper.push()

    requirements_file = github_helper.view_file('requirements.txt')
    parse_requirements_file(experiment, requirements_file)





