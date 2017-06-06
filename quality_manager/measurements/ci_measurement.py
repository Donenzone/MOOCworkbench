from build_manager.models import TravisInstance
from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import ExperimentMeasure, ExperimentMeasureResult, RawMeasureResult
from git_manager.helpers.github_helper import GitHubHelper
from build_manager.travis_ci_helper import TravisCiHelper


class CiEnabledMeasurement(MeasurementAbstraction):
    """Measure for Continuous Integration use for an experiment.
    If Travis is disabled, sets result as Low
    If travis is enabled, and of the last five builds at least one have passed, sets result as High
    If travis is enabled, and of the last five builds none have passed, sets result as Medium"""

    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Use of CI')
        self.raw_last_build = RawMeasureResult()

    def measure(self):
        travis_instance = TravisInstance.objects.filter(experiment=self.experiment)
        if travis_instance:
            travis_instance = travis_instance[0]
            if travis_instance.enabled:
                github_helper = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
                travis_helper = TravisCiHelper(github_helper)
                last_build_passed = travis_helper.get_last_build_status()
                self.add_raw_value(last_build_passed)

                if self.get_last_five_build_results():
                    self.result.result = ExperimentMeasureResult.HIGH
                else:
                    self.result.result = ExperimentMeasureResult.MEDIUM
            else:
                self.result.result = ExperimentMeasureResult.LOW

    def get_last_five_build_results(self):
        last_five_measures = ExperimentMeasureResult.objects.filter(measurement=self.measurement,
                                                                    step=self.experiment_step)
        last_five_measures = last_five_measures.order_by('-created')[:5]
        passed_list = []
        for measure in last_five_measures:
            for raw_value in measure.raw_values.all():
                passed_list.append(raw_value.value)
        
        return True if "True" in passed_list else False

    def add_raw_value(self, last_build_passed):
        self.raw_last_build.key = 'last_build_passed'
        self.raw_last_build.value = last_build_passed

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.raw_last_build.save()
        self.result.raw_values.add(self.raw_last_build)
        self.result.save()
        return self.result
