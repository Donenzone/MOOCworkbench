from celery.decorators import task
from ExperimentsManager.models import Experiment
from GitManager.github_helper import GitHubHelper
from BuildManager.travis_ci_helper import TravisCiHelper

@task
def get_last_log_for_build_task(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    travis_helper = TravisCiHelper(github_helper)
    return travis_helper.get_log_for_last_build()
