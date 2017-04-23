from celery.decorators import task

from git_manager.repo_init import ExperimentGitRepoInit
from experiments_manager.models import Experiment

@task
def initialize_repository(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    git_init = ExperimentGitRepoInit(experiment)
    git_init.init_repo_boilerplate()
