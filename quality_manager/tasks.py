from MOOCworkbench.celery import app

from experiments_manager.models import ChosenExperimentSteps
from git_manager.helpers.github_helper import GitHubHelper

from .measurements.requirements_measurement import RequirementsMeasurement
from .measurements.vcs_measurement import VersionControlUseMeasurement
from .measurements.test_measurement import TestMeasurement
from .measurements.ci_measurement import CiEnabledMeasurement
from .measurements.docs_measurement import DocsMeasurement
from .measurements.pylint_measurement import PylintMeasurement


@app.task
def task_complete_quality_check(step_id):
    task_version_control_quality_check(step_id)
    task_requirements_quality_check(step_id)
    task_test_quality_check(step_id)
    task_ci_quality_check(step_id)
    task_docs_coverage_check(step_id)
    task_pylint_static_quality_check(step_id)


@app.task
def task_requirements_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    req_measure = RequirementsMeasurement(step)
    req_measure.measure()
    req_measure.save_and_get_result()


@app.task
def task_version_control_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    vcs_measure = VersionControlUseMeasurement(step)
    vcs_measure.measure()
    vcs_measure.save_and_get_result()


@app.task
def task_test_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    experiment = step.experiment
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    test_measure = TestMeasurement(step, github_helper)
    test_measure.measure()
    test_measure.save_and_get_result()


@app.task
def task_ci_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    ci_measure = CiEnabledMeasurement(step)
    ci_measure.measure()
    ci_measure.save_and_get_result()


@app.task
def task_docs_coverage_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    docs_measure = DocsMeasurement(step)
    docs_measure.measure()
    docs_measure.save_and_get_result()


@app.task
def task_pylint_static_quality_check(step_id):
    step = ChosenExperimentSteps.objects.get(id=step_id)
    pylint_measure = PylintMeasurement(step)
    pylint_measure.measure()
    pylint_measure.save_and_get_result()
