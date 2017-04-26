from celery.decorators import task

from experiments_manager.models import Experiment
from git_manager.utils.repo_init import ExperimentGitRepoInit


@task
def initialize_repository(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    git_init = ExperimentGitRepoInit(experiment)
    git_init.init_repo_boilerplate()
