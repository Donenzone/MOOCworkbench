from celery.decorators import task

from cookiecutter_manager.models import CookieCutterTemplate

from .models import Experiment
from .helper import init_git_repo_for_experiment


@task
def initialize_repository(experiment_id, cookiecutter_id):
    experiment = Experiment.objects.get(id=experiment_id)
    cookiecutter = CookieCutterTemplate.objects.get(id=cookiecutter_id)
    init_git_repo_for_experiment(experiment, cookiecutter)
