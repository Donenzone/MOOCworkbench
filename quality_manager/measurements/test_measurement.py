from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import ExperimentMeasureResult, ExperimentMeasure, RawMeasureResult
from build_manager.models import TravisCiConfig
from build_manager.travis_ci_helper import TravisCiHelper
import re
from statistics import mean

class TestMeasurement(MeasurementAbstraction):
    def __init__(self, experiment, github_helper):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Testing')
        self.github_helper = github_helper
        self.raw = RawMeasureResult()

    def measure(self):
        travis_ci_helper = TravisCiHelper(self.github_helper)
        log = travis_ci_helper.get_log_for_last_build()
        nr_of_tests = self.parse_travis_log(log)
        historical_values = self.get_last_month_measures()
        historical_values.append(nr_of_tests)
        difference_list = [b-a for a, b in zip(historical_values[:-1], historical_values[1:])]

        self.raw.key = 'nr_of_tests'
        self.raw.value = float(nr_of_tests)

        mean_of_tests = mean(difference_list)
        if mean_of_tests < 1:
            self.result.result = ExperimentMeasureResult.LOW
        elif mean_of_tests < 5:
            self.result.result = ExperimentMeasureResult.MEDIUM
        else:
            self.result.result = ExperimentMeasureResult.HIGH


    def parse_travis_log(self, log_file):
        match = re.search('Ran [0-9] test[s]? in', log_file)
        if match:
            match = match.group(0)
            nr_of_tests = re.findall(r'\d+', match)[0]

            return int(nr_of_tests)
        else:
            return 0

    def get_last_month_measures(self):
        results = ExperimentMeasureResult.objects.filter(measurement=self.measurement, experiment=self.experiment)
        if results.count() == 0:
            return []
        else:
            result_list = []
            for result in results[:21]:
                raw_values = result.raw_values
                if raw_values and raw_values.count() is not 0:
                    raw_value = raw_values.all()[0]
                    result_list.append(raw_value.value)
            return result_list


    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.raw.save()
        self.result.raw_values.add(self.raw)
        return self.result
