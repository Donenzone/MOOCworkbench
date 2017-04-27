

from git_manager.views import create_new_github_repository
from cookiecutter_manager.helpers.helper_cookiecutter import clone_cookiecutter_data_science

from .models import Experiment
from .models import ChosenExperimentSteps


def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment


def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')


def create_new_experiment_with_boilerplate(experiment, cookiecutter):
    git_repo = create_new_github_repository(experiment.title, experiment.owner.user)

    experiment.git_repo = git_repo
    experiment.save()
    #clone_cookiecutter_data_science(cookiecutter, )

