from QualityManager.measurements.measurement import MeasurementAbstraction
from RequirementsManager.models import ExperimentRequirement
from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from QualityManager.models import RawMeasureResult

class RequirementsMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Requirements')
        self.raw = RawMeasureResult()
        
    def measure(self):
        requirements = ExperimentRequirement.objects.filter(experiment=self.experiment)

        self.set_raw_value(requirements.count())

        if requirements.count() < 2:
            self.result.result = ExperimentMeasureResult.LOW
        if requirements.count() > 2 and requirements.count() < 4:
            self.result.result = ExperimentMeasureResult.MEDIUM
        if requirements.count()  > 5:
            self.result.result = ExperimentMeasureResult.HIGH

    def set_raw_value(self, current):
        previous_nr = self.get_previous_nr_of_reqs()
        self.raw.key = 'difference'

        if previous_nr == 0:
            self.raw.value = requirements.count()
        else:
            self.raw.value = abs(requirements.count() - previous_nr)

    def get_previous_nr_of_reqs(self):
        last_measurement_filter = ExperimentMeasureResult.objects.filter(measurement=self.measurement).order_by('-created')
        if last_measurement_filter.count() is not 0:
            last_measurement = last_measurement_filter[0]
            return last_measurement.raw_values.all()[0]
        return 0

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.raw.save()
        self.result.raw_values.add(self.raw)
        return self.result
