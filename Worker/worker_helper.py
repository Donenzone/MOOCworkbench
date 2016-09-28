from WorkerManager.models import Worker
from django.db.models import Q
from .models import SubmittedExperiments, WorkerInformation


def get_current_status():
    worker_status = WorkerInformation.objects.all()[0].status
    if worker_status == WorkerInformation.DENY_INCOMING:
        return Worker.NOT_AVAILABLE
    else:
        current_experiments = SubmittedExperiments.objects.filter(Q(status=SubmittedExperiments.RUNNING)
                                                                | Q(status=SubmittedExperiments.CREATED))
        status = Worker.AVAILABLE
        if current_experiments.count() is not 0:
            status = Worker.BUSY
        return status


def get_worker_name():
    worker = WorkerInformation.objects.first()
    return worker.name
