from ExperimentsManager.serializer import *
from ExperimentsManager.tables import ExperimentTable
from ExperimentsManager.forms import ExperimentForm
from ExperimentsManager.models import *
from django.views.generic.detail import DetailView
from django.utils import timezone
from GitManager.views import get_user_repositories, create_new_github_repository_local
from django.views import View
from ExperimentsManager.serializer import serializer_experiment_run_factory
from UserManager.models import get_workbench_user
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.http import HttpResponseRedirect, JsonResponse
from ExperimentsManager.tasks import initialize_repository
from django.contrib.auth.decorators import login_required
import json
from ExperimentsManager.helper import verify_and_get_experiment
from ExperimentsManager.helper import get_steps
from markdown2 import Markdown
from django.contrib import messages
from GitManager.github_helper import GitHubHelper
from django.shortcuts import get_object_or_404
from DocsManager.models import Docs
from GitManager.mixins.repo_file_list import RepoFileListMixin
from ExperimentsManager.mixins import ActiveStepMixin
from ExperimentsManager.mixins import ExperimentContextMixin
from QualityManager.mixins import MeasurementMixin
from DocsManager.mixins import DocsMixin


class ExperimentDetailView(RepoFileListMixin, ActiveStepMixin, MeasurementMixin, DocsMixin, DetailView):
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        context['steps'] = get_steps(experiment)
        return context


class ExperimentCreateView(View):
    def get(self, request, experiment_id=0):
        try:
            form = ExperimentForm()
            repository_list = get_user_repositories(request.user)
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id,
                                                                'repository_list': repository_list})
        except ValueError as a:
            messages.add_message(request, messages.INFO, 'Before creating an experiment, please sign in with GitHub')
            return redirect(to=reverse('view_my_profile'))

    def post(self, request, experiment_id=0):
        experiment = Experiment()
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            if form.cleaned_data['new_git_repo']:
                git_repo = create_new_github_repository_local(experiment.title, request.user, 'python', experiment)
                experiment.git_repo = git_repo
                experiment.save()
            return redirect(to=reverse('choose_experiment_steps', kwargs={'experiment_id': experiment.id}))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


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


class ChooseExperimentSteps(View):
    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        context = {}
        context['steps'] = ExperimentStep.objects.all()
        context['experiment_id'] = experiment_id
        return render(request, "ExperimentsManager/choose_experiment_steps.html", context)

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
        context['content_file'] = github_helper.view_file_in_repo(file_name)
        return render(request, 'ExperimentsManager/file_detail.html', context)


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)
    return render(request, 'ExperimentsManager/experiments_table.html', {'table': table})


@login_required
def complete_step_and_go_to_next(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    active_step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
    active_step.active = False
    active_step.completed = True
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
    content_file = github_helper.view_file_in_repo('README.md')
    md = Markdown()
    content_file = md.convert(content_file)
    return render(request, 'ExperimentsManager/experiment_readme.html', {'readme': content_file})


@login_required
def view_list_files_in_repo_folder(request, pk):
    if request.method == 'GET':
        folder_name = request.GET['folder_name']
        expirement = verify_and_get_experiment(request, experiment_id)
        data = list_files_in_repo_folder('gitrepository1', request.user.username, folder_name)
        return render(request, 'ExperimentsManager/folder_detail.html', {'contents': data, 'pk': pk})
