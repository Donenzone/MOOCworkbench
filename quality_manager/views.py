from django.shortcuts import render
from django.http import JsonResponse
from experiments_manager.helper import verify_and_get_experiment
from quality_manager.models import ExperimentMeasure, ExperimentMeasureResult
from quality_manager.models import RawMeasureResult
from django.contrib.auth.decorators import login_required
from quality_manager.mixins import MeasurementMixin
from quality_manager.helper import WhatNow
from django.views import View
from experiments_manager.mixins import ExperimentContextMixin
from quality_manager.models import RawMeasureResult
from .tasks import version_control_quality_check

class DashboardView(ExperimentContextMixin, MeasurementMixin, View):

    def get(self, request, experiment_id):
        context = super(DashboardView, self).get(request, experiment_id)
        what_now = WhatNow(self.experiment)
        context['what_now_list'] = what_now.what_to_do_now()

        messages = {}
        for measurement in self._get_recent_measurements_for_all_types(self.experiment):
            messages[measurement.measurement.name] = measurement.get_message()
        context['messages'] = messages
        return render(request, 'quality_manager/dashboard.html', context)


class NrOfCommitsView(MeasurementMixin, View):

    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        experiment_measure = ExperimentMeasure.objects.get(name='Version control use')
        measurement = self.get_recent_measurements_for_type(experiment, experiment_measure)

        raw_values = []
        key_values = []
        for measure in measurement:
            key_values.append(measure.created)
            for raw in measure.raw_values.all():
                raw_values.append(raw.value)
        return JsonResponse({'values': raw_values, 'keys': key_values})
