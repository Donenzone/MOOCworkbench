from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.template.defaultfilters import slugify

from experiments_manager.helper import verify_and_get_experiment
from quality_manager.models import ExperimentMeasure
from quality_manager.mixins import MeasurementMixin
from quality_manager.helpers.what_now_helper import WhatNow
from experiments_manager.mixins import ExperimentContextMixin
from quality_manager.tasks import version_control_quality_check
from quality_manager.tasks import requirements_quality_check
from quality_manager.tasks import test_quality_check
from quality_manager.tasks import ci_quality_check
from quality_manager.tasks import docs_coverage_check
from helpers.helper_mixins import ExperimentPackageTypeMixin


class DashboardView(ExperimentContextMixin, MeasurementMixin, View):

    def get(self, request, experiment_id):
        context = super(DashboardView, self).get(request, experiment_id)
        what_now = WhatNow(self.experiment)
        context['what_now_list'] = what_now.what_to_do_now()
        context['object_type'] = ExperimentPackageTypeMixin.EXPERIMENT_TYPE
        context['active_step_id'] = self.experiment.get_active_step()

        messages = {}
        for measurement in self._get_recent_measurements_for_all_types(self.experiment):
            measurement_slug = slugify(measurement.measurement.name).replace('-', '_')
            messages[measurement_slug] = measurement.get_message()
        context['messages'] = messages
        return render(request, 'quality_manager/dashboard.html', context)


class VcsOverviewView(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(VcsOverviewView, self).get(request, experiment_id)
        return render(request, 'quality_manager/vcs_overview.html', context)


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


@login_required
def refresh_measurements(request, step_id):
    verify_and_get_experiment(request, step_id)
    version_control_quality_check.delay(step_id)
    requirements_quality_check.delay(step_id)
    test_quality_check.delay(step_id)
    ci_quality_check.delay(step_id)
    docs_coverage_check.delay(step_id)

    return JsonResponse({'refresh': True})
