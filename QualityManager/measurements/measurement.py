from RequirementsManager.models import ExperimentRequirement
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
        self.result.performed_at = datetime.now()
        self.result.measurement = self.measurement
        self.result.save()
        return self.result


class VersionControlUseMeasurement(MeasurementAbstraction):
    THREE_WEEKS = 21

    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Version control use')

    def measure(self):
        github_helper = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
        since = datetime.now() - timedelta(days=self.THREE_WEEKS)
        commits = github_helper.get_commits_in_repository(since)

        nr_of_commits_per_day = []
        median_size_of_commits_per_day = []

        for day in range(1, 21):
            day_commits = self.get_commits_of_day(commits, since, day)
            nr_of_commits_per_day.append(len(day_commits))
            commit_size_median = self.get_median_size_of_commits_per_day(day_commits)
            median_size_of_commits_per_day.append(commit_size_median)

        average_size_of_commits_total = mean(median_size_of_commits_per_day)
        median_nr_of_commits = median(nr_of_commits_per_day)

        print(average_size_of_commits_total)
        print(median_nr_of_commits)

        if median_nr_of_commits < 0.9:
            self.result.result = ExperimentMeasureResult.LOW
        if median_nr_of_commits > 0.9 and median_nr_of_commits < 1.5:
            self.result.result = ExperimentMeasureResult.MEDIUM
        if median_nr_of_commits > 1.5:
            self.result.result = ExperimentMeasureResult.HIGH

    def get_commits_of_day(self, commits, since, day):
        date_day = since + timedelta(days=day)
        commit_list = []
        for commit in commits:
            if commit.commit.author.date.date() == date_day.date():
                commit_list.append(commit)
        return commit_list

    def get_median_size_of_commits_per_day(self, commits):
        size_list = []
        for commit in commits:
            size_list.append(commit.stats.total)
        if len(size_list) is not 0:
            return median(size_list)
        return 0

    def save_and_get_result(self):
        self.result.performed_at = datetime.now()
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
