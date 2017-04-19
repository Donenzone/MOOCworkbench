from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import ExperimentMeasure, ExperimentMeasureResult
from quality_manager.models import RawMeasureResult
from docs_manager.sphinx_helper import SphinxHelper
from experiments_manager.models import ChosenExperimentSteps
from git_manager.helpers.github_helper import GitHubHelper
from docs_manager.models import Docs


class DocsMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Documentation')
        self.raw_funcs = RawMeasureResult()
        self.raw_class = RawMeasureResult()

    def measure(self):
        docs = Docs.objects.filter(experiment=self.experiment)
        docs_instance = None
        if docs:
            docs_instance = docs[0]
        if docs_instance and docs_instance.enabled:
            github_helper = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
            steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
            sphinx_helper = SphinxHelper(self.experiment, steps, github_helper.owner)
            sphinx_helper.update_coverage()
            coverage = sphinx_helper.get_coverage_data()
            if coverage:
                undoced_funcs = coverage[1]
                undoced_classes = coverage[2]

                if undoced_classes == 0 and undoced_funcs == 0:
                    self.result.result = ExperimentMeasureResult.HIGH
                elif undoced_funcs < 10 and undoced_classes < 10:
                    self.result.result = ExperimentMeasureResult.MEDIUM
                else:
                    self.result.result = ExperimentMeasureResult.LOW
                self.add_raw_values(coverage)
        else:
            self.result.result = ExperimentMeasureResult.LOW

    def add_raw_values(self, coverage):
        self.raw_funcs.key = 'docs_coverage_funcs'
        self.raw_funcs.value = coverage[1]

        self.raw_class.key = 'docs_coverage_classes'
        self.raw_class.value = coverage[2]

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()

        self.raw_funcs.save()
        self.result.raw_values.add(self.raw_funcs)

        self.raw_class.save()
        self.result.raw_values.add(self.raw_class)

        self.result.save()

        return self.result
