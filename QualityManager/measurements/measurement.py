from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from datetime import datetime, timedelta
from abc import abstractmethod
from GitManager.github_helper import GitHubHelper
from statistics import median, mean

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
