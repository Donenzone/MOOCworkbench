from celery.decorators import task
from datetime import timedelta
from GitManager.repo_init import *

@task
def initialize_repository(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    git_init = GitRepoInit(experiment)
    git_init.init_repo_boilerplate()
