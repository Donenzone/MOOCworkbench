from .models import SubmittedExperiments, WorkerInformation
from MOOCworkbench.settings import MASTER_URL
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .tasks import start_code_execution
from git import Repo
from django.shortcuts import HttpResponse
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveWorkerInformationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        worker = WorkerInformation.objects.create(name=name, location=MASTER_URL)
        worker.save()
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveNewExperiment(View):
    def post(self, request):
        print("New job received")
        if 'repo_name' in request.POST:
            repo_name = request.POST['repo_name']
        if 'git_url' in request.POST:
            repo_url = request.POST['git_url']
        if 'run_id' in request.POST:
            run_id = request.POST['run_id']

        submitted_experiment = SubmittedExperiments(experiment_git_url=repo_url, repo_name=repo_name, run_id=run_id)
        submitted_experiment.save()
        clone_repo_and_start_execution(submitted_experiment)
        return HttpResponse()


def clone_repo_and_start_execution(submitted_experiment):
    Repo.clone_from(submitted_experiment.experiment_git_url, to_path='RunManager/gitrepositories/{0}'.format(submitted_experiment.repo_name))
    start_code_execution.delay(submitted_experiment)