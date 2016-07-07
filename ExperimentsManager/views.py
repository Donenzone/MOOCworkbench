from django.shortcuts import render, redirect
from rest_framework import viewsets
from ExperimentsManager.serializer import *
from django.contrib.auth.decorators import login_required
from .tables import ExperimentTable
from .forms import ExperimentForm
from django.views.generic.detail import DetailView
from django.utils import timezone
from GitManager.views import get_user_repositories, create_new_repository

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
        return context


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)
    return render(request, 'experiments_table.html', {'table': table})


@login_required
def new_edit_experiment(request, experiment_id=0):
    if request.method == 'GET':
        form = ExperimentForm()
        repository_list = get_user_repositories(request.user)
        return render(request, "edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})
    if request.method == 'POST':
        experiment = Experiment()

        if int(experiment_id) != 0:
            experiment = Experiment.objects.get(id=experiment_id)

        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            if form.cleaned_data['new_git_repo']:
                create_new_repository(experiment.title, request.user.username, 'python')
            experiment.owner = WorkbenchUser.objects.get(user=request.user)

            experiment.save()
            return redirect(to=index)
        else:
            return render(request, "edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id})
