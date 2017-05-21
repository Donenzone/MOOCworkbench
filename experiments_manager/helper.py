from markdown2 import Markdown

from git_manager.helpers.github_helper import GitHubHelper

from .models import Experiment
from .models import ChosenExperimentSteps


def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment


def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')


def get_readme_of_experiment(experiment):
    github_helper = GitHubHelper(experiment.owner.user, experiment.git_repo.name)
    content_file = github_helper.view_file('README.md')
    md = Markdown()
    return md.convert(content_file)


class MessageStatus(object):
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'danger'
