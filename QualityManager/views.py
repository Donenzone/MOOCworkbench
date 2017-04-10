from django.shortcuts import render
from ExperimentsManager.helper import verify_and_get_experiment
from QualityManager.models import ExperimentMeasure, ExperimentMeasureResult
from QualityManager.models import RawMeasureResult
from django.contrib.auth.decorators import login_required
from QualityManager.mixins import MeasurementMixin
from QualityManager.helper import WhatNow
# Create your views here.


@login_required
def dashboard(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    what_now = WhatNow(experiment)
    what_now_list = what_now.get_messages()

    messages = {}
    for measurement in get_recent_measurements_for_all_types(experiment):
        messages[measurement.measurement.name] = measurement.get_message()
    return render(request, 'QualityManager/dashboard.html', {'messages': messages, 'what_now_list': what_now_list})
