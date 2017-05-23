from pylint_manager.models import PylintScanResult
from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import RawMeasureResult, ExperimentMeasure
from quality_manager.models import ExperimentMeasureResult


class PylintMeasurement(MeasurementAbstraction):
    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Static code analysis')
        self.raw_value_list =[]

    def measure(self):
        language_helper = self.experiment.language_helper()
        language_helper.static_code_analysis()(self.experiment)
        scan_results = PylintScanResult.objects.filter(for_project=self.experiment.pylint).order_by('-scanned_at')
        if scan_results:
            scan_result = scan_results[0]
            if scan_result.nr_of_errors > 0:
                self.result.result = ExperimentMeasureResult.LOW
            elif scan_result.nr_of_warnings > 0:
                self.result.result = ExperimentMeasureResult.MEDIUM
            elif scan_result.nr_of_other_issues < 30:
                self.result.result = ExperimentMeasureResult.HIGH

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        return self.result
