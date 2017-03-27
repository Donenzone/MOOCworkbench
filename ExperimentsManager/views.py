from ExperimentsManager.serializer import *
from .tables import ExperimentTable
from .forms import ExperimentForm
from .models import *
from django.views.generic.detail import DetailView
from django.utils import timezone
from GitManager.views import *
from django.views import View
from WorkerManager.views import run_experiment
from .serializer import serializer_experiment_run_factory
from UserManager.models import get_workbench_user
import json
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.http import HttpResponseRedirect, JsonResponse
from .tasks import initialize_repository
from django.template.defaultfilters import slugify
# Create your views here.


class ExperimentRunViewSet(viewsets.ModelViewSet):
    queryset = ExperimentRun.objects.all()
    serializer_class = serializer_experiment_run_factory(ExperimentRun)


class ExperimentWorkerRunViewSet(viewsets.ModelViewSet):
    queryset = ExperimentWorkerRun.objects.all()
    serializer_class = serializer_experiment_run_factory(ExperimentWorkerRun)


class ExperimentDetailView(DetailView):
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        experiment = Experiment.objects.get(id=self.kwargs['pk'])
        context['steps'] = get_steps(experiment)
        context['git_list'] = get_git_list(self.request.user, experiment)
        context['commit_list'] = commits_in_repository(experiment.title, self.request.user.username)
        return context

def get_git_list(user, experiment, step=None):
    if not step:
        step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
    name = slugify(step.step.step_name)
    return list_files_in_repo(user, experiment.git_repo.name, name)

def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')


@login_required
def get_git_list_for_step(request):
    assert 'experiment_id' in request.GET
    assert 'step_id' in request.GET

    step_id = request.GET['step_id']
    experiment_id = request.GET['experiment_id']
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user

    step = ChosenExperimentSteps.objects.get(id=step_id)
    file_list = get_git_list(request.user, experiment, step)
    return_dict = []
    for content_file in file_list:
        return_dict.append((content_file.name, content_file.type))
    return JsonResponse({'files': return_dict})

@login_required
def complete_step_and_go_to_next(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    if experiment.owner.user == request.user:
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
            return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id}))
        else:
            return JsonResponse({'completed': True})

@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)

    return render(request, 'ExperimentsManager/experiments_table.html', {'table': table})


@login_required
def run_experiment_view(request, pk):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiment = Experiment.objects.get(pk=pk)
    experiment_run = ExperimentRun(experiment=experiment, owner=owner)
    experiment_run.save()
    run_experiment(experiment_run)
    return render(request, 'ExperimentsManager/experiment_run.html', {'status': 'Started'})


@login_required
def cancel_experiment_run(request, pk):
    experiment_run = ExperimentRun.objects.get(pk=pk)
    experiment_run.status = ExperimentRun.CANCELLED
    experiment_run.save()


class CreateExperimentView(View):
    def get(self, request, experiment_id=0):
        form = ExperimentForm()
        repository_list = get_user_repositories(request.user)
        return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id,
                                                            'repository_list': repository_list})

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
            elif request.POST['github'] is not '':
                git_repo = GitRepository()
                git_repo.title = experiment.title
                git_repo.git_url = request.POST['github']
                git_repo.owner = experiment.owner
                git_repo.save()
                experiment.git_repo = git_repo
            return redirect(to=reverse('choose_experiment_steps', kwargs={'experiment_id': experiment.id}))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})

class ChooseExperimentSteps(View):
    def get(self, request, experiment_id):
        experiment = Experiment.objects.get(id=experiment_id)
        assert request.user == experiment.owner.user
        context = {}
        context['steps'] = ExperimentStep.objects.all()
        context['experiment_id'] = experiment_id
        return render(request, "ExperimentsManager/choose_experiment_steps.html", context)

    def post(self, request, experiment_id):
        experiment = Experiment.objects.get(id=experiment_id)
        workbench_user =  get_workbench_user(request.user)
        if experiment.owner == workbench_user:
            step_list = []
            step_json_list = json.loads(request.POST['steplist'])
            counter = 1
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
            url = reverse('experiment_detail', kwargs={'pk': experiment_id})
            return JsonResponse({'url': url})


@login_required
def view_file_in_git_repository(request, pk):
    if request.method == 'GET':
        file_name = request.GET['file_name']
        expirement = Experiment.objects.get(id=pk)
        data = view_file_in_repo('gitrepository1', file_name, request.user.username)
        return render(request, 'ExperimentsManager/file_detail.html', {'contents': data, 'name': file_name})


@login_required
def view_list_files_in_repo_folder(request, pk):
    if request.method == 'GET':
        folder_name = request.GET['folder_name']
        expirement = Experiment.objects.get(id=pk)
        data = list_files_in_repo_folder('gitrepository1', request.user.username, folder_name)
        print(data)
        return render(request, 'ExperimentsManager/folder_detail.html', {'contents': data, 'pk': pk})
