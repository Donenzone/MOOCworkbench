from .models import Worker
from ExperimentsManager.models import ExperimentRun
from MOOCworkbench.settings import MASTER_URL
from django.views import View
from .tasks import clone_repo_and_start_execution
from django.shortcuts import HttpResponse, render, redirect, reverse
from WorkerHelper.serializer import serializer_factory
from rest_framework import generics
# Create your views here.


class WorkerIndexView(View):
    def get(self, request):
        if 'accept' in request.GET:
            self.set_accept_incoming_status(request.GET['accept'])
            return redirect(to=reverse('worker_index'))

        return_dict = {}
        current_experiment = ExperimentRun.objects.filter(status=ExperimentRun.RUNNING)
        if current_experiment.count() is not 0:
            return_dict['current_experiment'] = current_experiment[0]
        else:
            return_dict['current_experiment'] = "No experiment"
        return_dict['past_experiments'] = ExperimentRun.objects.order_by('-submit_date').all()[:10]
        return_dict['worker'] = ExperimentRun.objects.all()[0]
        return render(request, 'Worker/worker_index.html', return_dict)

    def set_accept_incoming_status(self, status):
        try:
            status = int(status)
            worker = Worker.objects.all()[0]
            worker.status = Worker.ACCEPT_INCOMING
            if status == Worker.DENY_INCOMING:
                worker.status = Worker.DENY_INCOMING
            worker.save()
        except Exception as e:
            print("Changing status failed: {0}".format(e))
