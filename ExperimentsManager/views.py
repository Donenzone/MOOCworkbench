from django.shortcuts import render, redirect
from rest_framework import viewsets
from ExperimentsManager.serializer import *
from django.contrib.auth.decorators import login_required
from .tables import ExperimentTable
from .forms import ExperimentForm
from django.views.generic.detail import DetailView
from django.utils import timezone
from GitManager.views import *
from django.views import View
from MOOCworkbench.celery import app
from WorkerManager.views import run_experiment
# Create your views here.

class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all().order_by('-created')
    serializer_class = ExperimentSerializer


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = Script.objects.all().order_by('-created')
    serializer_class = ScriptSerializer


class ExperimentDetailView(DetailView):
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['git_list'] = list_files_in_repo('gitrepository1', self.request.user.username)
        context['commit_list'] = commits_in_repository('gitrepository1', self.request.user.username)
        return context


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)
    return render(request, 'experiments_table.html', {'table': table})


@login_required
def run_experiment_view(request, pk):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiment = Experiment.objects.get(pk=pk)
    run_experiment(experiment, owner)
    return render(request, 'experiment_run.html', {'status': 'Started'})


class CreateExperimentView(View):
    def get(self, request, experiment_id=0):
        form = ExperimentForm()
        repository_list = get_user_repositories(request.user)
        return render(request, "edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})

    def post(self, request, experiment_id=0):
        experiment = Experiment()

        if int(experiment_id) != 0:
            experiment = Experiment.objects.get(id=experiment_id)

        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            if form.cleaned_data['new_git_repo']:
                create_new_repository(experiment.title, request.user, 'python', experiment)
            elif request.POST['github'] is not '':
                git_repo = GitRepository()
                git_repo.title = experiment.title
                git_repo.git_url = request.POST['github']
                git_repo.owner = experiment.owner
                git_repo.save()
                experiment.git_repo = git_repo
            return redirect(to=index)
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


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
