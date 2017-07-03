import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.mixins import ExperimentContextMixin
from experiments_manager.models import ChosenExperimentSteps
from helpers.helper_mixins import ExperimentPackageTypeMixin

from .helpers.helper import (get_description_measure_list,
                             get_nr_of_commits_last_week)
from .mixins import MeasurementMixin
from .tasks import task_complete_quality_check

logger = logging.getLogger(__name__)


class DashboardView(ExperimentContextMixin, MeasurementMixin, View):
    template_name = 'quality_manager/dashboard.html'

    def get(self, request, experiment_id):
        context = super(DashboardView, self).get(request, experiment_id)
        active_step = self.experiment.get_active_step()
        context['object_type'] = ExperimentPackageTypeMixin.EXPERIMENT_TYPE
        context['active_step_id'] = 0 if not active_step else active_step.id
        context['dashboard_active'] = True

        messages = {}
        for measurement in self._get_recent_measurements_for_all_types(active_step):
            measurement_slug = measurement.slug()
            messages[measurement_slug] = measurement

        context['descriptions'] = get_description_measure_list()
        context['dashboard_messages'] = messages
        logger.debug('%s dashboard view for %s', request.user, self.experiment)
        return render(request, self.template_name, context)


class VcsOverviewView(ExperimentContextMixin, View):
    """View for Version Control Use overview, with context.
    Actual contents is fetched on the page through ajax."""
    def get(self, request, experiment_id):
        context = super(VcsOverviewView, self).get(request, experiment_id)
        return render(request, 'quality_manager/vcs_overview.html', context)


class NrOfCommitsView(MeasurementMixin, View):
    """Json view for nr of commits to fill the graph with,
    returns a Json dict with keys as the days and values the nr of commits on that day"""
    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        raw_values, key_values = get_nr_of_commits_last_week(experiment)
        return JsonResponse({'values': raw_values, 'keys': key_values})


@login_required
def refresh_measurements(request, step_id):
    """View that starts the task to refresh all the quality measurements
    On the dashboard, the user can press a button to call this view/task."""
    step = ChosenExperimentSteps.objects.get(pk=step_id)
    verify_and_get_experiment(request, step.experiment_id)
    task_complete_quality_check.delay(step_id)
    return JsonResponse({'refresh': True})
