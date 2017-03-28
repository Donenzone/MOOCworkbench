from celery.decorators import task
from ExperimentsManager.models import Experiment
from .measurements.measurement import RequirementsMeasurement

@task
def requirements_quality_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    req_measure = RequirementsMeasurement(experiment)
    req_measure.measure()
    result = req_measure.save_and_get_result()
