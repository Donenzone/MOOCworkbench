from QualityManager.measurements.measurement import MeasurementAbstraction
from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from BuildManager.models import

class CiEnabledMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Use of CI')

    def measure(self):
        travis_query_set = TravisInstance.objects.filter(experiment=experiment)
        is_travis_enabled = travis_query_set.count() is not 0
        if is_travis_enabled:
            self.result.result = ExperimentMeasureResult.HIGH
        else:
            self.result.result = ExperimentMeasureResult.LOW

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
