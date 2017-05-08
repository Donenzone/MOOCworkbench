from quality_manager.measurements.measurement import MeasurementAbstraction
from git_manager.helpers.github_helper import GitHubHelper
from quality_manager.models import ExperimentMeasureResult, ExperimentMeasure, RawMeasureResult
from datetime import datetime, timedelta
from statistics import mean, median


class VersionControlUseMeasurement(MeasurementAbstraction):

    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Version control use')
        self.raw = RawMeasureResult()

    def measure(self):
        today = datetime.now().date() - timedelta(3)
        commits_last_three_days = self.experiment.git_repo.commits.filter(timestamp__gte=today)
        if commits_last_three_days:
            if commits_last_three_days.count() < 6:
                self.result.result = ExperimentMeasureResult.MEDIUM
            elif commits_last_three_days.count() > 6:
                self.result.result = ExperimentMeasureResult.HIGH
            else:
                self.result.result = ExperimentMeasureResult.LOW
        else:
            self.result.result = ExperimentMeasureResult.LOW

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.raw.save()
        self.result.raw_values.add(self.raw)
        self.result.save()
        return self.result
