from RequirementsManager.models import ExperimentRequirement
from .models import ExperimentMeasureResult, ExperimentMeasure
from datetime import datetime

class MeasurementAbstraction(object):
    def __init__(self, experiment):
        self.result = ExperimentMeasureResult()
        self.experiment = experiment
        self.result.experiment = experiment

    def measure(self):
        pass

    def save_and_get_result(self):
        pass

class RequirementsMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__()
        self.measurement = ExperimentMeasure.objects.get(name='Requirements')

    def measure(self):
        requirements = ExperimentRequirement.objects.filter(experiment=experiment)
        if requirements.count() == 0:
            self.result.result = ExperimentMeasureResult.LOW
        if requirements.count() == 1:
            self.result.result = ExperimentMeasureResult.MEDIUM
        if requirements.count()  > 1:
            self.result.result = ExperimentMeasureResult.HIGH

    def save_and_get_result(self):
        self.result.performed_at = datetime.now()
        self.result.measurement = self.measurement
        self.result.save()
        return self.result

class VersionControlUseMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__()
        self.measurement = ExperimentMeasure.objects.get(name='Version Control Use')

    def measure(self):
        pass

    def save_and_get_result(self):
        pass
