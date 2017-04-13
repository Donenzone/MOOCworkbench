from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import ExperimentMeasureResult, ExperimentMeasure, RawMeasureResult
from build_manager.models import TravisCiConfig
from build_manager.travis_ci_helper import TravisCiHelper
import re
from statistics import mean
from coverage_manager.helpers.coveralls_helper import CoverallsHelper


class TestMeasurement(MeasurementAbstraction):
    def __init__(self, experiment, github_helper):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Testing')
        self.github_helper = github_helper
        self.raw = RawMeasureResult()

    def measure(self):
        code_coverage = self.measure_code_coverage()
        if code_coverage:
            code_coverage = float(code_coverage)

            self.raw.key = 'code_coverage'
            self.raw.value = code_coverage

            if code_coverage < 50:
                self.result.result = ExperimentMeasureResult.LOW
            elif code_coverage < 80:
                self.result.result = ExperimentMeasureResult.MEDIUM
            elif code_coverage >= 80:
                self.result.result = ExperimentMeasureResult.HIGH

    def measure_code_coverage(self):
        coveralls = CoverallsHelper(user=self.github_helper.owner, repo_name=self.github_helper.repo_name)
        return coveralls.code_coverage_data()

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        if self.raw.key:
            self.raw.save()
            self.result.raw_values.add(self.raw)
            self.result.save()
        return self.result
