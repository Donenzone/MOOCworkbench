
from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import RawMeasureResult, ExperimentMeasure
from quality_manager.models import ExperimentMeasureResult


class PyLintMeasurement(MeasurementAbstraction):
    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Pylint static code analysis')
        self.raw_value_list =[]

    def measure(self):
        # parse pylint results
        self.result.result = ExperimentMeasureResult.HIGH

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.result.raw_values.set(self.raw_value_list)
        self.result.save()
        return self.result
