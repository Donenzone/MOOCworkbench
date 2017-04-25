import requirements
from django.shortcuts import reverse, redirect
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from requirements_manager.models import Requirement
from helpers.helper_mixins import ExperimentPackageTypeMixin
from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.github_helper import GitHubHelper
from requirements_manager.forms import RequirementForm
from helpers.helper import get_package_or_experiment


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


class RequirementCreateView(ExperimentPackageTypeMixin, CreateView):
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

    def get_success_url(self):
        if self.kwargs['object_type'] == self.EXPERIMENT_TYPE:
            experiment = verify_and_get_experiment(self.request, self.kwargs['object_id'])
            success_url = reverse('experiment_detail', kwargs={'pk': experiment.id, 'slug': experiment.slug()})
        elif self.kwargs['object_type']  == self.PACKAGE_TYPE:
            success_url = reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['object_id']})
        return success_url


@login_required
def remove_experiment_requirement(request, object_id, object_type):
    if request.POST:
        assert 'requirement_id' in request.POST
        requirement_id = request.POST['requirement_id']
        exp_or_package = get_package_or_experiment(request, object_type, object_id)
        requirement = Requirement.objects.get(id=requirement_id)
        exp_or_package.requirements.remove(requirement)
        exp_or_package.save()
        requirement.delete()
        return JsonResponse({'deleted': True})


@login_required
def write_requirements_file(request, object_id, object_type):
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    requirements_txt = build_requirements_file(exp_or_package)
    github_helper = GitHubHelper(request.user, exp_or_package.git_repo.name)
    github_helper.update_file_in_repository('requirements.txt', 'Updated requirements.txt file by MOOC workbench',
                                            requirements_txt)
    messages.add_message(request, messages.INFO, 'Successfully updated requirements in your repository')
    return redirect(to=exp_or_package.get_absolute_url())


def build_requirements_file(exp_or_package):
    requirements_txt = ''
    for requirement in exp_or_package.requirements.all():
        requirements_txt += '{0}\n'.format(str(requirement))
    return requirements_txt


def parse_requirements_file(exp_or_package, requirements_file):
    for req in requirements.parse(requirements_file):
        requirement = Requirement()
        requirement.package_name = req.name
        if req.specs:
            requirement.version = req.specs[0][1]
        requirement.save()

        exp_or_package.requirements.add(requirement)
        exp_or_package.save()

