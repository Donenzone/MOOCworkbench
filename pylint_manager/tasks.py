from MOOCworkbench.celery import app
from git_manager.helpers.helper import get_experiment_from_repo_name

from .utils import run_pylint


@app.task
def task_run_pylint(repository_name):
    experiment = get_experiment_from_repo_name(repository_name)
    run_pylint(experiment)
