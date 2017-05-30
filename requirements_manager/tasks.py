from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus
from git_manager.helpers.helper import get_exp_or_package_from_repo_name
from helpers.helper import get_package_or_experiment_without_request
from MOOCworkbench.celery import app


@app.task
def task_write_requirements_file(object_id, object_type):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    language_helper = exp_or_package.language_helper()
    language_helper.write_requirements_file()
    username = exp_or_package.owner.user.username
    send_message(username, MessageStatus.SUCCESS, 'Dependencies updated in GitHub')


@app.task
def task_update_requirements(repository_name):
    experiment = get_exp_or_package_from_repo_name(repository_name)
    language_helper = experiment.language_helper()
    language_helper.update_requirements()
