from abc import abstractmethod

from quality_manager.models import ExperimentMeasureResult


class MeasurementAbstraction(object):
    def __init__(self, experiment_step):
        self.result = ExperimentMeasureResult()
        self.experiment_step = experiment_step
        self.experiment = experiment_step.experiment
        self.result.step = experiment_step

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def save_and_get_result(self):
        pass
