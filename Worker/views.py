from .models import Worker
from ExperimentsManager.models import ExperimentRun
from django.views import View
from django.shortcuts import HttpResponse, render, redirect, reverse


class WorkerIndexView(View):
    def get(self, request):
        if 'accept' in request.GET:
            set_accept_incoming_status(request.GET['accept'])
            return redirect(to=reverse('worker_index'))
        return_dict = {}
        current_experiment = ExperimentRun.objects.filter(status=ExperimentRun.RUNNING)
        if current_experiment.count() is not 0:
            return_dict['current_experiment'] = current_experiment[0]
        else:
            return_dict['current_experiment'] = "No experiment"
        return_dict['past_experiments'] = ExperimentRun.objects.order_by('-created').all()[:10]
        return_dict['worker'] = Worker.objects.all()[0]
        return render(request, 'Worker/worker_index.html', return_dict)


def set_accept_incoming_status(status):
    try:
        status = int(status)
        worker = Worker.objects.all()[0]
        worker.status = Worker.AVAILABLE
        if status == Worker.NOT_AVAILABLE:
            worker.status = Worker.NOT_AVAILABLE
        worker.save()
    except Exception as e:
        print("Changing status failed: {0}".format(e))
