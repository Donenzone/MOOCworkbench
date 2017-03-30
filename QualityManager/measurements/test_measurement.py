from QualityManager.measurements.measurement import MeasurementAbstraction
from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from BuildManager.models import

class TestMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Testing')

    def measure(self):
        travis_ci_helper = TravisCiHelper(github_helper)
        log = travis_ci_helper.get_log_for_last_build()

    def parse_travis_log(self):
        pass

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
