from QualityManager.measurements.measurement import MeasurementAbstraction
from RequirementsManager.models import ExperimentRequirement
from QualityManager.models import ExperimentMeasureResult, ExperimentMeasure
from QualityManager.models import RawMeasureResult
from BuildManager.models import TravisInstance
from BuildManager.travis_ci_helper import TravisCiHelper
from GitManager.github_helper import GitHubHelper

class RequirementsMeasurement(MeasurementAbstraction):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.measurement = ExperimentMeasure.objects.get(name='Requirements')
        self.raw = RawMeasureResult()

    def measure(self):
        requirements = ExperimentRequirement.objects.filter(experiment=self.experiment)
        travis_ci_config = TravisInstance.objects.filter(experiment=self.experiment).first()
        if travis_ci_config:
            if travis_ci_config.enabled:
                github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
                travis_helper = TravisCiHelper(github_helper)
                last_build_log = travis_helper.get_log_for_last_build()
                complete_requirements_file = self.find_if_missing_dependency(last_build_log)
                if complete_requirements_file:
                    self.result.result = ExperimentMeasureResult.HIGH
                else:
                    self.result.result = ExperimentMeasureResult.LOW
            else:
                self.result.result = ExperimentMeasureResult.LOW


    def find_if_missing_dependency(self, log_file):
        module_match = re.search('ModuleNotFoundError: No module named', log_file)
        import_match = re.search('ImportError: cannot import name', log_file)
        if module_match or import_match:
            return False
        return True

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
