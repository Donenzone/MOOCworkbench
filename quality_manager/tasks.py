from celery.decorators import task
from experiments_manager.models import Experiment
from quality_manager.measurements.requirements_measurement import RequirementsMeasurement
from quality_manager.measurements.vcs_measurement import VersionControlUseMeasurement

@task
def requirements_quality_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    req_measure = RequirementsMeasurement(experiment)
    req_measure.measure()
    result = req_measure.save_and_get_result()

@task
def version_control_quality_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    vcs_measure = VersionControlUseMeasurement(experiment)
    vcs_measure.measure()
    result = vcs_measure.save_and_get_result()
