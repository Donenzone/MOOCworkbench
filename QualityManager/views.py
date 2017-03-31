from django.shortcuts import render
from ExperimentsManager.helper import verify_and_get_experiment
from QualityManager.models import ExperimentMeasure, ExperimentMeasureResult
from QualityManager.models import RawMeasureResult
from django.contrib.auth.decorators import login_required
from QualityManager.utils import get_recent_measurements_for_all_types
# Create your views here.


def overview_metrics(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    messages = {}
    for measurement in get_recent_measurements_for_all_types(experiment):
        messages[measurement.measurement.name] = measurement.get_message()
    return render(request, 'QualityManager/metrics.html', {'messages': messages})
