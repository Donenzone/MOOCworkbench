from quality_manager.models import ExperimentMeasureResult
from abc import abstractmethod


class MeasurementAbstraction(object):
    def __init__(self, experiment):
        self.result = ExperimentMeasureResult()
        self.experiment = experiment
        self.result.experiment = experiment

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def save_and_get_result(self):
        pass
