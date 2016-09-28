from .models import SubmittedExperiments, WorkerInformation
from MOOCworkbench.settings import MASTER_URL
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .tasks import clone_repo_and_start_execution
from django.shortcuts import HttpResponse
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveWorkerInformationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        delete_existing_worker()
        worker = WorkerInformation.objects.create(name=name, location=MASTER_URL)
        worker.save()
        return HttpResponse()


def delete_existing_worker():
    try:
        worker = WorkerInformation.objects.all()[0]
        worker.delete()
    except:
        pass


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
        clone_repo_and_start_execution.delay(submitted_experiment)
        return HttpResponse()