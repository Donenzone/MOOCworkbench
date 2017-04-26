from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import ExperimentMeasureResult, ExperimentMeasure
from build_manager.models import TravisInstance


class CiEnabledMeasurement(MeasurementAbstraction):
    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Use of CI')

    def measure(self):
        is_travis_enabled = TravisInstance.objects.filter(experiment=self.experiment)
        if is_travis_enabled:
            self.result.result = ExperimentMeasureResult.HIGH
        else:
            self.result.result = ExperimentMeasureResult.LOW

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
