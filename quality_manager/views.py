from celery import chain

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.mixins import ExperimentContextMixin
from experiments_manager.models import ChosenExperimentSteps
from helpers.helper_mixins import ExperimentPackageTypeMixin

from .models import ExperimentMeasure
from .mixins import MeasurementMixin, get_recent_measurements_for_type
from .helpers.what_now_helper import WhatNow
from .helpers.helper import get_description_measure_list
from .tasks import task_complete_quality_check


class DashboardView(ExperimentContextMixin, MeasurementMixin, View):
    template_name = 'quality_manager/dashboard.html'

    def get(self, request, experiment_id):
        context = super(DashboardView, self).get(request, experiment_id)
        what_now = WhatNow(self.experiment)
        active_step = self.experiment.get_active_step()
        context['what_now_list'] = what_now.what_to_do_now()
        context['object_type'] = ExperimentPackageTypeMixin.EXPERIMENT_TYPE
        context['active_step_id'] = 0 if not active_step else active_step.id
        context['dashboard_active'] = True

        messages = {}
        for measurement in self._get_recent_measurements_for_all_types(active_step):
            measurement_slug = measurement.slug()
            messages[measurement_slug] = measurement

        context['descriptions'] = get_description_measure_list()
        context['dashboard_messages'] = messages
        return render(request, self.template_name, context)


class VcsOverviewView(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(VcsOverviewView, self).get(request, experiment_id)
        return render(request, 'quality_manager/vcs_overview.html', context)


class NrOfCommitsView(MeasurementMixin, View):
    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        experiment_measure = ExperimentMeasure.objects.get(name='Version control use')
        measurement = get_recent_measurements_for_type(experiment.get_active_step(),
                                                       experiment_measure)

        raw_values = []
        key_values = []
        for measure in measurement:
            key_values.append(measure.created)
            for raw in measure.raw_values.all():
                raw_values.append(raw.value)
        return JsonResponse({'values': raw_values, 'keys': key_values})


@login_required
def refresh_measurements(request, step_id):
    step = ChosenExperimentSteps.objects.get(pk=step_id)
    verify_and_get_experiment(request, step.experiment_id)
    task_complete_quality_check.delay(step_id)
    return JsonResponse({'refresh': True})
