from django.shortcuts import reverse, redirect
import requirements
from .models import ExperimentRequirement
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from .forms import ExperimentRequirementForm
from git_manager.helpers.github_helper import GitHubHelper
from django.contrib import messages
from experiments_manager.helper import verify_and_get_experiment


def parse_requirements_file(experiment, requirements_file):
    for req in requirements.parse(requirements_file):
        requirement = ExperimentRequirement()
        requirement.package_name = req.name
        if len(req.specs) is not 0:
            requirement.version = req.specs[0][1]
        requirement.experiment = experiment
        requirement.save()


class ExperimentRequirementListView(ListView):
    model = ExperimentRequirement

    def get_queryset(self):
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
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
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        form.instance.experiment = experiment
        return super(ExperimentRequirementCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('experiment_detail', kwargs={'pk': self.kwargs['experiment_id']})


@login_required
def remove_experiment_requirement(request, experiment_id, requirement_id):
    experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
    requirement = ExperimentRequirement.objects.get(id=requirement_id)
    requirement.delete()


@login_required
def write_requirements_file(request, experiment_id):
    experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
    requirements_txt = ''
    for requirement in ExperimentRequirement.objects.filter(experiment=experiment):
        requirements_txt += '{0}\n'.format(str(requirement))
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    github_helper.update_file_in_repository('requirements.txt', 'Updated requirements.txt file by MOOC workbench', requirements_txt)
    messages.add_message(request, messages.INFO, 'Successfully updated requirements in your repository')
    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id}))
