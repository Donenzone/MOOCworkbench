from experiments_manager.models import Experiment
from experiments_manager.models import ChosenExperimentSteps


def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment


def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')
