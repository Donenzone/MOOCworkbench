from django.shortcuts import render, HttpResponse
from django.views import View
from .models import Worker
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
class WorkerManagerRegistrationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        if 'location' in request.POST:
            location = request.POST['location']
        if 'status' in request.POST:
            status = request.POST['status']
        if 'communication_key' in request.POST:
            communication_key = request.POST['communication_key']
        Worker.objects.save(name=name, location=name, status=status, communication_key=communication_key)
        return HttpResponse()
