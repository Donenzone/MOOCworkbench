from .models import PylintResult, PylintScan, PylintScanResult


def last_scan_results_for_experiment(experiment):
    pylint_scan = PylintScanResult.objects.filter(for_project=experiment.pylint).order_by('-scanned_at')
    if pylint_scan:
        return pylint_scan[0]
    else:
        return None


def return_results_for_file(experiment, file_path):
    pylint_scan = last_scan_results_for_experiment(experiment)
    if '/' in file_path:
        file_path = file_path.split('/')[-1]
    pylint_results = PylintResult.objects.filter(for_result=pylint_scan, file_path__contains=file_path)
    return pylint_results


def return_result_summary_for_file(experiment, file_path):
    pylint_results = return_results_for_file(experiment, file_path)
    result_dict = {'e': pylint_results.filter(pylint_type='e').count(),
                   'w': pylint_results.filter(pylint_type='w').count(),
                   'c': pylint_results.filter(pylint_type='c').count(),
                   's': pylint_results.filter(pylint_type='s').count()}
    return result_dict
