from WorkerManager.models import Worker
from django.db.models import Q
from .models import Worker
from ExperimentsManager.models import ExperimentRun


def get_worker_name():
    worker = Worker.objects.first()
    return worker.name
