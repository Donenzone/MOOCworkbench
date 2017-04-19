import requirements
from django.shortcuts import reverse, redirect
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from requirements_manager.models import Requirement
from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.github_helper import GitHubHelper
from requirements_manager.forms import RequirementForm


def parse_requirements_file(experiment, requirements_file):
    for req in requirements.parse(requirements_file):
        requirement = Requirement()
        requirement.package_name = req.name
        if req.specs:
            requirement.version = req.specs[0][1]
        requirement.experiment = experiment
        requirement.save()


class RequirementListView(ListView):
    model = Requirement

    def get_queryset(self):
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        return Requirement.objects.filter(experiment=experiment)

    def get_context_data(self, **kwargs):
        context = super(RequirementListView, self).get_context_data(**kwargs)
        context['requirements_form'] = RequirementForm()
        context['experiment_id'] = self.kwargs['pk']
        return context


class RequirementCreateView(CreateView):
    model = Requirement
    fields = ['package_name', 'version']

    def form_valid(self, form):
        response = super(RequirementCreateView, self).form_valid(form)
        experiment = verify_and_get_experiment(self.request, self.kwargs['experiment_id'])
        experiment.requirements.add(form.instance)
        experiment.save()
        return response

    def get_success_url(self):
        experiment = verify_and_get_experiment(self.request, self.kwargs['experiment_id'])
        return reverse('experiment_detail', kwargs={'pk': experiment.id, 'slug': experiment.slug()})


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
