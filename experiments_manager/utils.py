import logging

from django.db import transaction

from cookiecutter_manager.helpers.helper_cookiecutter import \
    clone_cookiecutter_template
from experiments_manager.consumers import \
    send_exp_package_creation_status_update
from git_manager.helpers.git_helper import GitHelper
from git_manager.models import GitRepository
from git_manager.helpers.helper import create_new_github_repository

logger = logging.getLogger(__name__)


class ExperimentProgress(object):
    STEP_CREATING_GITHUB_REPO = 2
    STEP_CREATING_BOILERPLATE_CODE = 3
    STEP_PUSHING_BOILERPLATE_CODE = 4
    STEP_READING_DEPENDENCIES = 5
    STEP_CLEAN_UP = 6


def init_git_repo_for_experiment(experiment, cookiecutter):
    """Initialize a GitHub repository for an experiment with specified cookiecutter template
    If GitHub repo could not be created, but a repo already exists, returns True without modifying any code
    If a GitHub repo does not exist, initialize it with cookiecutter template, read existing dependencies and add those to DB model
    """
    try:
        username = experiment.owner.user.username
        github_helper, created = create_new_github_repository(experiment.title, experiment.owner.user)
        # if github helper is none, continuing is useless
        if not github_helper:
            return False

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

        # if we have a github helper, but a repo already exists
        # since one could not be created, return True and continue as normal
        if github_helper and not created:
            return True

        git_helper = GitHelper(github_helper)
        git_helper.clone_or_pull_repository()

        repo_dir = git_helper.repo_dir_of_user()

        clone_cookiecutter_template(cookiecutter, repo_dir, repo_name, experiment.owner, experiment.description)
        send_exp_package_creation_status_update(username, ExperimentProgress.STEP_CREATING_BOILERPLATE_CODE)

        git_helper.commit('Cookiecutter template added')
        git_helper.push()
        send_exp_package_creation_status_update(username, ExperimentProgress.STEP_PUSHING_BOILERPLATE_CODE)

        language_helper = experiment.language_helper()
        req_file_loc = language_helper.get_requirements_file_location()
        requirements_file = github_helper.view_file(req_file_loc)
        language_helper.parse_requirements(requirements_file)

        send_exp_package_creation_status_update(username, ExperimentProgress.STEP_READING_DEPENDENCIES)
        return True
    except Exception as e:
        logger.error('failed to create experiment %s with error %s', experiment, e)
        logger.error('removing experiment %s to maintain db integrity', experiment)
        experiment.delete()
        return False
