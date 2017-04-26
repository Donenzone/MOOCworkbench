from celery.decorators import task
from experiments_manager.models import ChosenExperimentSteps
from quality_manager.measurements.requirements_measurement import RequirementsMeasurement
from quality_manager.measurements.vcs_measurement import VersionControlUseMeasurement
from quality_manager.measurements.test_measurement import TestMeasurement
from quality_manager.measurements.ci_measurement import CiEnabledMeasurement
from quality_manager.measurements.docs_measurement import DocsMeasurement
from git_manager.helpers.github_helper import GitHubHelper


@task
def requirements_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    req_measure = RequirementsMeasurement(step)
    req_measure.measure()
    req_measure.save_and_get_result()


@task
def version_control_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    vcs_measure = VersionControlUseMeasurement(step)
    vcs_measure.measure()
    vcs_measure.save_and_get_result()


@task
def test_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    experiment = step.experiment
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    test_measure = TestMeasurement(step, github_helper)
    test_measure.measure()
    test_measure.save_and_get_result()


@task
def ci_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    ci_measure = CiEnabledMeasurement(step)
    ci_measure.measure()
    ci_measure.save_and_get_result()


@task
def docs_coverage_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    docs_measure = DocsMeasurement(step)
    docs_measure.measure()
    docs_measure.save_and_get_result()
