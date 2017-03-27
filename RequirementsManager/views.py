from django.shortcuts import render, reverse, redirect
import requirements
from .models import ExperimentRequirement
from ExperimentsManager.models import Experiment
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.core import serializers
from .forms import ExperimentRequirementForm
from GitManager.github_helper import update_file_in_repository
from django.contrib import messages
# Create your views here.

def parse_requirements_file(requirements_file):
    for req in requirements.parse(requirements_file):
        print(req.name, req.specs, req.extras)


class ExperimentRequirementListView(ListView):
    model = ExperimentRequirement

    def get_queryset(self):
        experiment = Experiment.objects.get(id=self.kwargs['pk'])
        assert experiment.owner.user == self.request.user
        return ExperimentRequirement.objects.filter(experiment=experiment)

    def get_context_data(self, **kwargs):
        context = super(ExperimentRequirementListView, self).get_context_data(**kwargs)
        context['requirements_form'] = ExperimentRequirementForm()
        context['experiment_id'] = self.kwargs['pk']
        return context


class ExperimentRequirementCreateView(CreateView):
    model = ExperimentRequirement
    fields = ['package_name', 'version']

    def form_valid(self, form):
        experiment = Experiment.objects.get(id=self.kwargs['experiment_id'])
        assert experiment.owner.user == self.request.user
        form.instance.experiment = experiment
        return super(ExperimentRequirementCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('experiment_detail', kwargs={'pk': self.kwargs['experiment_id']})


@login_required
def remove_experiment_requirement(request, experiment_id, requirement_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    requirement = ExperimentRequirement.objects.get(id=requirement_id)
    requirement.delete()


@login_required
def write_requirements_file(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    requirements_txt = ''
    for requirement in ExperimentRequirement.objects.filter(experiment=experiment):
        requirements_txt += '{0}\n'.format(str(requirement))
    update_file_in_repository(request.user, experiment.git_repo.name, 'requirements.txt', 'Updated requirements.txt file by MOOC workbench', requirements_txt)
    messages.add_message(request, messages.INFO, 'Successfully updated requirements in your repository')
    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id}))
