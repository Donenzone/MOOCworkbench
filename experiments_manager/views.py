import json
from datetime import datetime

from django.views.generic.detail import DetailView
from markdown2 import Markdown
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from docs_manager.mixins import DocsMixin
from experiments_manager.tables import ExperimentTable
from experiments_manager.forms import ExperimentForm
from experiments_manager.models import *
from experiments_manager.tasks import initialize_repository
from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.helper import get_steps
from experiments_manager.mixins import ActiveStepMixin
from experiments_manager.mixins import ExperimentContextMixin
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.mixins.repo_file_list import RepoFileListMixin
from git_manager.views import get_user_repositories
from quality_manager.mixins import MeasurementMixin
from helpers.helper_mixins import ExperimentPackageTypeMixin


class ExperimentDetailView(RepoFileListMixin, ActiveStepMixin, MeasurementMixin, DocsMixin, ExperimentPackageTypeMixin, DetailView):
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        context['steps'] = get_steps(experiment)
        context['object_type'] = self.get_requirement_type(experiment)
        context['active_step_id'] = experiment.get_active_step().id
        return context


class ExperimentCreateView(View):
    def get(self, request, experiment_id=0):
        try:
            form = ExperimentForm()
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_edit_new.html", {'form': form, 'experiment_id': experiment_id,
                                                                'repository_list': repository_list})
        except ValueError as a:
            messages.add_message(request, messages.INFO, 'Before creating an experiment, please sign in with GitHub')
            return redirect(to=reverse('view_my_profile'))

    def post(self, request, experiment_id=0):
        experiment = Experiment()
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            cookiecutter = form.cleaned_data['template']
            experiment.language = cookiecutter.language
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            return redirect(to=reverse('experimentsteps_choose', kwargs={'experiment_id': experiment.id}))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_edit_new.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


class FileListForStep(RepoFileListMixin, View):
    def get(self, request):
        assert 'experiment_id' in request.GET
        assert 'step_id' in request.GET

        step_id = request.GET['step_id']
        experiment_id = request.GET['experiment_id']
        experiment = verify_and_get_experiment(request, experiment_id)

        step = get_object_or_404(ChosenExperimentSteps, pk=step_id)
        file_list = self._get_files_in_repository(request.user, experiment.git_repo.name, step.folder_name())
        return_dict = []
        for content_file in file_list:
            return_dict.append((content_file.name, content_file.type))
        return JsonResponse({'files': return_dict})


class ChooseExperimentSteps(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(ChooseExperimentSteps, self).get(request, experiment_id)
        context['steps'] = ExperimentStep.objects.all()
        return render(request, "experiments_manager/experimentsteps_choose.html", context)

    def post(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        step_list = []
        step_json_list = json.loads(request.POST['steplist'])
        counter = 1
        if len(step_json_list) is not 0:
            delete_existing_chosen_steps(experiment)
            for step in step_json_list:
                step = int(step)
                step = ExperimentStep.objects.get(id=step)
                chosen_experiment_step = ChosenExperimentSteps(experiment=experiment, step=step, step_nr=counter)
                if counter == 1:
                    chosen_experiment_step.active = True
                    chosen_experiment_step.started_at = datetime.now()
                chosen_experiment_step.save()
                counter += 1
            initialize_repository.delay(experiment_id)
            url = reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()})
            return JsonResponse({'url': url})
        else:
            return JsonResponse({'message': 'Choose at least one step'})


class FileViewGitRepository(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(FileViewGitRepository, self).get(request, experiment_id)
        file_name = request.GET['file_name']
        experiment = verify_and_get_experiment(request, experiment_id)
        github_helper = GitHubHelper(request.user, experiment.git_repo.name)
        context['content_file'] = github_helper.view_file(file_name)
        return render(request, 'experiments_manager/file_detail.html', context)


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)
    return render(request, 'experiments_manager/experiments_table.html', {'table': table})


@login_required
def complete_step_and_go_to_next(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    active_step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
    active_step.active = False
    active_step.completed = True
    active_step.completed_at = datetime.now()
    active_step.save()
    next_step_nr = active_step.step_nr + 1
    next_step = ChosenExperimentSteps.objects.filter(experiment=experiment, step_nr=next_step_nr)
    if next_step.count() != 0:
        next_step = next_step[0]
        next_step.active = True
        next_step.save()
        return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))
    else:
        return JsonResponse({'completed': True})


@login_required
def readme_of_experiment(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    content_file = github_helper.view_file('README.md')
    md = Markdown()
    content_file = md.convert(content_file)
    return render(request, 'experiments_manager/experiment_readme.html', {'readme': content_file})
