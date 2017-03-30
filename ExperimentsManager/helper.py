from ExperimentsManager.models import Experiment

def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment
