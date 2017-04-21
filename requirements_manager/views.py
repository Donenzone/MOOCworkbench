import requirements
from django.shortcuts import reverse, redirect
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from requirements_manager.models import Requirement
from helpers.helper_mixins import ExperimentPackageTypeMixin
from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.github_helper import GitHubHelper
from requirements_manager.forms import RequirementForm
from marketplace.models import InternalPackage


def parse_requirements_file(experiment, requirements_file):
    for req in requirements.parse(requirements_file):
        requirement = Requirement()
        requirement.package_name = req.name
        if req.specs:
            requirement.version = req.specs[0][1]
        requirement.experiment = experiment
        requirement.save()


class RequirementListView(ExperimentPackageTypeMixin, ListView):
    model = Requirement

    def get_queryset(self):
        if self.kwargs['object_type'] == self.EXPERIMENT_TYPE:
            exp_or_package = verify_and_get_experiment(self.request, self.kwargs['pk'])
        elif self.kwargs['object_type'] == self.PACKAGE_TYPE:
            exp_or_package = InternalPackage.objects.get(id=self.kwargs['pk'])
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

    def form_valid(self, form):
        response = super(RequirementCreateView, self).form_valid(form)
        req_type = self.kwargs['object_type']
        object_id = self.kwargs['object_id']
        if req_type == self.EXPERIMENT_TYPE:
            experiment = verify_and_get_experiment(self.request, object_id)
            self.add_req_to_object(form.instance, experiment)
        elif req_type == self.PACKAGE_TYPE:
            internal_package = InternalPackage.objects.get(id=object_id)
            self.add_req_to_object(form.instance, internal_package)
        return response

    def add_req_to_object(self, req, obj):
        obj.requirements.add(req)
        obj.save()

    def get_success_url(self):
        if self.kwargs['object_type'] == self.EXPERIMENT_TYPE:
            experiment = verify_and_get_experiment(self.request, self.kwargs['object_id'])
            response = reverse('experiment_detail', kwargs={'pk': experiment.id, 'slug': experiment.slug()})
        elif self.kwargs['object_type']  == self.PACKAGE_TYPE:
            response = reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['object_id']})
        return response


@login_required
def remove_experiment_requirement(request, experiment_id, requirement_id):
    verify_and_get_experiment(request, experiment_id)
    requirement = Requirement.objects.get(id=requirement_id)
    requirement.delete()


@login_required
def write_requirements_file(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    requirements_txt = ''
    for requirement in Requirement.objects.filter(experiment=experiment):
        requirements_txt += '{0}\n'.format(str(requirement))
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    github_helper.update_file_in_repository('requirements.txt', 'Updated requirements.txt file by MOOC workbench', requirements_txt)
    messages.add_message(request, messages.INFO, 'Successfully updated requirements in your repository')
    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id}))
