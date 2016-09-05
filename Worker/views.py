from django.shortcuts import render
import requests
from .models import SubmittedExperiments, WorkerInformation
from WorkerManager.models import Worker
from django.views import View
# Create your views here.


def get_current_status():
    current_experiments = SubmittedExperiments.objects.filter(status=RUNNING)
    status = WorkerManager.AVAILABLE
    if current_experiments.count() is not 0:
        status = WorkerManager.BUSY
    return status

class ReceiveWorkerInformationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        WorkerInformation.objects.save(name=name)
