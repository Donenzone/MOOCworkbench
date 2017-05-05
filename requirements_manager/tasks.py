from MOOCworkbench.celery import app

from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.helper import get_experiment_from_repo_name
from helpers.helper import get_package_or_experiment_without_request

from .helper import build_requirements_file, parse_requirements_file
from .helper import delete_existing_requirements


@app.task
def task_write_requirements_file(object_id, object_type):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    requirements_txt = build_requirements_file(exp_or_package)
    github_helper = GitHubHelper(exp_or_package.owner.user, exp_or_package.git_repo.name)
    github_helper.update_file('requirements.txt', 'Updated requirements.txt file by MOOC workbench',
                              requirements_txt)
    username = exp_or_package.owner.user.username
    send_message(username, MessageStatus.SUCCESS, 'Dependencies updated in GitHub')


@app.task
def task_update_requirements(repository_name):
    experiment = get_experiment_from_repo_name(repository_name)
    github_helper = GitHubHelper(experiment.owner, repository_name)
    requirements_file = github_helper.view_file('requirements.txt')
    delete_existing_requirements(experiment)
    parse_requirements_file(experiment, requirements_file)
