from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from .models import Worker
from ExperimentsManager.models import ExperimentRun
import random
import string
import requests
from datetime import datetime
from helpers.url_helper import build_url
from helpers.ssh_helper import add_public_key_to_auth_keys, get_repo_url_for_worker
from django.core import serializers
from ExperimentsManager.consumers import Content
from WorkerHelper.serializer import serializer_factory
from rest_framework import generics, viewsets, mixins
# Create your views here.


def run_experiment(experiment_run):
    print("About to run experiment")
    run_worker = find_suitable_worker()
    if run_worker is not None:
        experiment_run.selected_worker = find_suitable_worker()
        experiment_run.save()
        experiment_run.submit()
    else:
        print("No suitable worker available")


# Finds a suitable worker available for the job
def find_suitable_worker():
    workers = Worker.objects.filter(status=Worker.AVAILABLE)
    if workers.count() is not 0:
        suitable_worker = workers[0]
        return suitable_worker
    else:
        return None


class WorkerPostView(generics.CreateAPIView):
    queryset = Worker.objects.all()
    serializer_class = serializer_factory(Worker)


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = serializer_factory(Worker)


class WorkerList(ListView):
    model = Worker


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveWorkerOutputView(View):
    def post(self, request):
        if 'complete' in request.POST:
            process_experiment_output(request.POST)
        else:
            run_id, line = None, None
            if 'run_id' in request.POST:
                run_id = request.POST['run_id']
            if 'line' in request.POST:
                line = request.POST['line']

            run = ExperimentRun.objects.get(id=run_id)
            run.append_to_output(line)

            # send output to client
            content = Content('worker')
            content.send(line)

        return HttpResponse()


def process_experiment_output(post_data):
    submitted_experiment = get_submitted_experiment(post_data['submitted_experiment'])
    experiment_run = ExperimentRun.objects.get(pk=submitted_experiment.run_id)

    worker = Worker.objects.get(pk=experiment_run.selected_worker.id)
    worker.status = Worker.AVAILABLE
    worker.save()

    experiment_run.status = submitted_experiment.status
    experiment_run.save()


def get_submitted_experiment(data):
    submitted_experiment = None
    for obj in serializers.deserialize("json", data):
        submitted_experiment = obj
    return submitted_experiment.object


def find_existing_worker_from_location(location):
    workers = Worker.objects.filter(location=location)
    if workers.count() is not 0:
        return workers[0]
    return None
