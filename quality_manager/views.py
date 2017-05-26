import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.mixins import ExperimentContextMixin
from experiments_manager.models import ChosenExperimentSteps
from helpers.helper_mixins import ExperimentPackageTypeMixin

from .mixins import MeasurementMixin
from .helpers.what_now_helper import WhatNow
from .helpers.helper import get_description_measure_list, get_nr_of_commits_last_week
from .tasks import task_complete_quality_check


logger = logging.getLogger(__name__)


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
        logger.debug('dashboard view for %s', self.experiment)
        return render(request, self.template_name, context)


class VcsOverviewView(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(VcsOverviewView, self).get(request, experiment_id)
        return render(request, 'quality_manager/vcs_overview.html', context)


class NrOfCommitsView(MeasurementMixin, View):
    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        raw_values, key_values = get_nr_of_commits_last_week(experiment)
        return JsonResponse({'values': raw_values, 'keys': key_values})


@login_required
def refresh_measurements(request, step_id):
    step = ChosenExperimentSteps.objects.get(pk=step_id)
    verify_and_get_experiment(request, step.experiment_id)
    task_complete_quality_check.delay(step_id)
    return JsonResponse({'refresh': True})
