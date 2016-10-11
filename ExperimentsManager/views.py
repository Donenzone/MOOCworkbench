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
        context['git_list'] = list_files_in_repo(experiment.title, self.request.user.username)
        context['commit_list'] = commits_in_repository(experiment.title, self.request.user.username)
        return context


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


class CreateExperimentView(View):
    def get(self, request, experiment_id=0):
        form = ExperimentForm()
        repository_list = get_user_repositories(request.user)
        return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id,
                                                            'repository_list': repository_list})

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
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


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
