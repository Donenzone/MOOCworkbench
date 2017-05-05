from django.shortcuts import reverse

from MOOCworkbench.celery import app
from cookiecutter_manager.models import CookieCutterTemplate
from experiments_manager.utils import send_experiment_creation_status_update

from .models import Experiment
from .utils import init_git_repo_for_experiment


@app.task
def initialize_repository(experiment_id, cookiecutter_id):
    experiment = Experiment.objects.get(id=experiment_id)
    cookiecutter = CookieCutterTemplate.objects.get(id=cookiecutter_id)
    username = experiment.owner.user.username
    send_experiment_creation_status_update(username, 1)
    init_git_repo_for_experiment(experiment, cookiecutter)
    redirect_url = reverse('experimentsteps_choose', kwargs={'experiment_id': experiment.id})
    send_experiment_creation_status_update(username, 7, completed=True, redirect_url=redirect_url)
