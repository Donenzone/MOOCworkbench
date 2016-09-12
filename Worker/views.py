from django.shortcuts import render
import requests
from .models import SubmittedExperiments, WorkerInformation
from MOOCworkbench.settings import MASTER_URL
from WorkerManager.models import Worker
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.db.models import Q
from helpers.ssh_helper import add_public_key_to_auth_keys, clone_repo_via_ssh
# Create your views here.


def get_current_status():
    current_experiments = SubmittedExperiments.objects.filter(Q(status=SubmittedExperiments.RUNNING)
                                                            | Q(status=SubmittedExperiments.PENDING))
    status = Worker.AVAILABLE
    if current_experiments.count() is not 0:
        status = Worker.BUSY
    return status

def get_worker_name():
    worker = WorkerInformation.objects.first()
    return worker.name

@method_decorator(csrf_exempt, name='dispatch')
class ReceiveWorkerInformationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        if 'repo_url' in request.POST:
            repo_url = request.POST['repo_url']
        worker = WorkerInformation.objects.create(name=name, location=MASTER_URL)
        worker.save()
        clone_repo_via_ssh('/home/jochem/Development/MOOCworkbench/gitrepositories/jochem/Test', 'Test')


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveNewExperiment(View):
    def post(self, request):
        print("New job received")
        if 'repo_name' in request.POST:
            repo_name = request.POST['repo_name']
        if 'git_url' in request.POST:
            repo_url = request.POST['git_url']
            Repo.clone_from(repo_url, to_path='gitrepositories/{0}'.format(repo_name))
