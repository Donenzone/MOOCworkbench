from WorkerManager.models import Worker
from django.db.models import Q
from .models import Worker
from ExperimentsManager.models import ExperimentRun


def get_current_status():
    worker_status = Worker.objects.all()[0].status
    if worker_status == Worker.DENY_INCOMING:
        return Worker.NOT_AVAILABLE
    else:
        current_experiments = ExperimentRun.objects.filter(Q(status=Worker.RUNNING)
                                                    | Q(status=Worker.CREATED))
        status = Worker.AVAILABLE
        if current_experiments.count() is not 0:
            status = Worker.BUSY
        return status


def get_worker_name():
    worker = Worker.objects.first()
    return worker.name
