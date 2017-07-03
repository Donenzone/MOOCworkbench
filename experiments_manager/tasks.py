from django.shortcuts import reverse

from cookiecutter_manager.models import CookieCutterTemplate
from experiments_manager.utils import send_exp_package_creation_status_update
from MOOCworkbench.celery import app

from .models import Experiment
from .utils import init_git_repo_for_experiment


@app.task
def initialize_repository(experiment_id, cookiecutter_id):
    """Initializes an experiment: fetches experiment obj, username and cookiecutter
    object and calls function to initialize and create git repo.
    In case of failure, redirects to experiment_new page and sends error message.
    :param experiment_id: PK of experiment to initialize
    :param cookiecutter_id: PK of cookiecutter template to use for initialization"""
    experiment = Experiment.objects.get(id=experiment_id)
    cookiecutter = CookieCutterTemplate.objects.get(id=cookiecutter_id)
    username = experiment.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    creation = init_git_repo_for_experiment(experiment, cookiecutter)
    if creation:
        redirect_url = reverse('experimentsteps_choose', kwargs={'experiment_id': experiment.id})
        send_exp_package_creation_status_update(username, 7, completed=True, redirect_url=redirect_url)
    else:
        redirect_url = reverse('experiment_new')
        error = "Experiment creation failed. Undoing changes..."
        send_exp_package_creation_status_update(username, 7, completed=False, redirect_url=redirect_url, error=error)
