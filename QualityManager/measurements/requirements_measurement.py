from QualityManager.measurements.measurement import MeasurementAbstraction
from RequirementsManager.models import ExperimentRequirement
from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure

class RequirementsMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Requirements')

    def measure(self):
        requirements = ExperimentRequirement.objects.filter(experiment=self.experiment)
        if requirements.count() < 2:
            self.result.result = ExperimentMeasureResult.LOW
        if requirements.count() > 2 and requirements.count() < 4:
            self.result.result = ExperimentMeasureResult.MEDIUM
        if requirements.count()  > 5:
            self.result.result = ExperimentMeasureResult.HIGH

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
