import json
import logging

from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus
from experiments_manager.models import Experiment
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.helper import get_exp_or_package_from_repo_name
from MOOCworkbench.celery import app

from .utils import parse_json_table_schema

logger = logging.getLogger(__name__)


@app.task
def task_write_data_schema(experiment_id):
    experiment = Experiment.objects.get(pk=experiment_id)
    data_schema = experiment.schema
    data_schema_str = str(json.dumps(data_schema.to_dict()))
    logger.debug('writing data schema for %s with schema: %s', experiment, data_schema_str)
    github_helper = GitHubHelper(experiment.owner.user, experiment.git_repo.name)
    github_helper.update_file('schema/schema.json', 'Updated data schema by MOOC workbench',
                              data_schema_str)
    username = experiment.owner.user.username
    send_message(username, MessageStatus.SUCCESS, 'Data schema successfully updated in GitHub')
    logger.debug('writing data schema success for: %s', experiment, data_schema_str)


@app.task
def task_read_data_schema(repository_name):
    experiment = get_exp_or_package_from_repo_name(repository_name)
    if isinstance(experiment, Experiment):
        logger.debug('reading data schema for: %s', experiment)
        github_helper = GitHubHelper(experiment.owner.user, experiment.git_repo.name)
        schema_json = json.loads(github_helper.view_file('schema/schema.json'))
        data_schema_fields = parse_json_table_schema(schema_json)
        data_schema = experiment.schema
        for field in data_schema.fields.all():
            data_schema.fields.remove(field)
            data_schema.save()
            field.delete()
        for new_field in data_schema_fields:
            new_field.save()
            data_schema.fields.add(new_field)
            data_schema.save()
        logger.debug('read data schema for: %s', experiment, data_schema_fields)
