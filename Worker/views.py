from django.shortcuts import render
import requests
from .models import SubmittedExperiments, WorkerInformation
from MOOCworkbench.settings import MASTER_URL
from WorkerManager.models import Worker
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
# Create your views here.


def get_current_status():
    current_experiments = SubmittedExperiments.objects.filter(status=SubmittedExperiments.RUNNING)
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
        worker = WorkerInformation.objects.create(name=name, location=MASTER_URL)
        worker.save()
