from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Worker
import random
import string
# Create your views here.

# Finds a suitable worker available for the job
def find_suitable_worker():
    workers = Worker.objects.filter(status=Worker.AVAILABLE)
    if workers.count() is not 0:
        suitable_worker = workers[0]
        return suitable_worker
    else:
        return None

# Submits job to the worker
def submit_job_to_worker(worker, experiment):
    worker.submit(experiment)

# Registration for new worker available for work
@method_decorator(csrf_exempt, name='dispatch')
class WorkerManagerRegistrationView(View):
    def post(self, request):
        name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
        worker = Worker.objects.create(name=name, location='', status=Worker.AVAILABLE, communication_key=name)
        worker.save()
        return HttpResponse()
