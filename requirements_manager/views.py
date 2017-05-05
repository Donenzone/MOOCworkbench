from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from helpers.helper_mixins import ExperimentPackageTypeMixin
from helpers.helper import get_package_or_experiment
from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus

from .forms import RequirementForm
from .models import Requirement
from .mixins import RequirementSuccessUrlMixin
from .tasks import task_write_requirements_file


class RequirementListView(ExperimentPackageTypeMixin, ListView):
    model = Requirement

    def get_queryset(self):
        exp_or_package = get_package_or_experiment(self.request, self.kwargs['object_type'], self.kwargs['pk'])
        return exp_or_package.requirements.all()

    def get_context_data(self, **kwargs):
        context = super(RequirementListView, self).get_context_data(**kwargs)
        context['requirements_form'] = RequirementForm()
        context['object_id'] = self.kwargs['pk']
        context['object_type'] = self.kwargs['object_type']
        return context


class RequirementCreateView(ExperimentPackageTypeMixin, RequirementSuccessUrlMixin, CreateView):
    model = Requirement
    fields = ['package_name', 'version']
    template_name = 'requirements_manager/requirement_list.html'

    def form_valid(self, form):
        response = super(RequirementCreateView, self).form_valid(form)
        object_type = self.kwargs['object_type']
        object_id = self.kwargs['object_id']
        exp_or_package = get_package_or_experiment(self.request, object_type, object_id)
        self.add_req_to_object(form.instance, exp_or_package)
        return response

    def add_req_to_object(self, req, obj):
        obj.requirements.add(req)
        obj.save()


class RequirementUpdateView(ExperimentPackageTypeMixin, RequirementSuccessUrlMixin, UpdateView):
    model = Requirement
    fields = ['package_name', 'version']

    def get_context_data(self, **kwargs):
        context = super(RequirementUpdateView, self).get_context_data(**kwargs)
        context['object_id']= self.kwargs['object_id']
        context['object_type'] = self.kwargs['object_type']
        context['pk'] = self.kwargs['pk']
        return context


@login_required
def remove_experiment_requirement(request, object_id, object_type):
    if request.POST:
        assert 'requirement_id' in request.POST
        requirement_id = request.POST['requirement_id']
        exp_or_package = get_package_or_experiment(request, object_type, object_id)
        requirement = exp_or_package.requirements.filter(pk=requirement_id)
        if requirement:
            requirement = requirement[0]
            with transaction.atomic():
                exp_or_package.requirements.remove(requirement)
                exp_or_package.save()
                requirement.delete()
            return JsonResponse({'deleted': True})
    return JsonResponse({'deleted': False})


@login_required
def write_requirements_file(request, object_id, object_type):
    get_package_or_experiment(request, object_type, object_id)
    task_write_requirements_file.delay(object_id, object_type)
    send_message(request.user.username, MessageStatus.INFO, 'Task started to update dependencies...')
    return JsonResponse({'success': True})



