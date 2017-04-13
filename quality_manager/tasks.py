from celery.decorators import task
from experiments_manager.models import Experiment
from quality_manager.measurements.requirements_measurement import RequirementsMeasurement
from quality_manager.measurements.vcs_measurement import VersionControlUseMeasurement
from quality_manager.measurements.test_measurement import TestMeasurement
from quality_manager.measurements.ci_measurement import CiEnabledMeasurement
from quality_manager.measurements.docs_measurement import DocsMeasurement
from git_manager.github_helper import GitHubHelper

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

@task
def test_quality_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    test_measure = TestMeasurement(experiment, github_helper)
    test_measure.measure()
    result = test_measure.save_and_get_result()

@task
def ci_quality_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    ci_measure = CiEnabledMeasurement(experiment)
    ci_measure.measure()
    result = ci_measure.save_and_get_result()

@task
def docs_coverage_check(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    docs_measure = DocsMeasurement(experiment)
    docs_measure.measure()
    result = docs_measure.save_and_get_result()
