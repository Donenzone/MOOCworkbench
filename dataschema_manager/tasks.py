import json

from MOOCworkbench.celery import app

from experiments_manager.consumers import send_message
from experiments_manager.models import Experiment
from git_manager.helpers.github_helper import GitHubHelper


@app.task
def task_write_data_schema(experiment_id):
    experiment = Experiment.objects.get(pk=experiment_id)
    data_schema = experiment.schema.first()
    data_schema_str = str(json.dumps(data_schema.to_dict()))
    github_helper = GitHubHelper(experiment.owner.user, experiment.git_repo.name)
    github_helper.update_file('schema/schema.json', 'Updated data schema by MOOC workbench',
                              data_schema_str)
    username = experiment.owner.user.username
    send_message(username, 'success', 'Data schema successfully updated in GitHub')
