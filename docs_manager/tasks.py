import logging

from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from MOOCworkbench.celery import app
from helpers.helper import get_package_or_experiment_without_request
from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus


logger = logging.getLogger(__name__)


@app.task
def task_generate_docs(object_type, object_id):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    username = exp_or_package.owner.user.username
    if exp_or_package.docs.enabled:
        logger.debug('start docs generation for %s (%s)', exp_or_package, username)
        language_helper = exp_or_package.language_helper()
        language_helper.generate_documentation()
        send_message(username, MessageStatus.SUCCESS,
                     'Documentation regenerated.')
    else:
        send_message(username, MessageStatus.WARNING,
                     'Before you can generate docs, first enable docs for your experiment.')