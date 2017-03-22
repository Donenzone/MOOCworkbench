from celery.decorators import task
from datetime import timedelta
from .models import ChosenExperimentSteps, Experiment
from GitManager.github_helper import add_file_to_repository
from django.template.defaultfilters import slugify

@task
def create_step_folders(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=experiment)
    for step in chosen_experiment_steps:
        name = slugify(step.step.step_name)
        commit_message = 'Create folder {0}'.format(name)
        add_file_to_repository(experiment.owner, experiment.git_repo.name, '__init__.py', commit_message, name)
