from MOOCworkbench.celery import app

from experiments_manager.consumers import send_message
from git_manager.helpers.github_helper import GitHubHelper
from helpers.helper import get_package_or_experiment_without_request

from .helper import build_requirements_file, parse_requirements_file


@app.task
def task_write_requirements_file(object_id, object_type):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    requirements_txt = build_requirements_file(exp_or_package)
    github_helper = GitHubHelper(exp_or_package.owner.user, exp_or_package.git_repo.name)
    github_helper.update_file('requirements.txt', 'Updated requirements.txt file by MOOC workbench',
                              requirements_txt)
    username = exp_or_package.owner.user.username
    send_message(username, 'success', 'Dependencies updated in GitHub')


@app.task
def task_update_requirements(repository_name):
    experiment = None
    github_helper = GitHubHelper()
    requirements_file = github_helper.view_file('requirements.txt')
    parse_requirements_file(experiment, requirements_file)