from .models import SubmittedExperiments, WorkerInformation
from MOOCworkbench.settings import MASTER_URL
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .tasks import clone_repo_and_start_execution
from django.shortcuts import HttpResponse, render, redirect, reverse
# Create your views here.


class WorkerIndexView(View):
    def get(self, request):
        if 'accept' in request.GET:
            self.set_accept_incoming_status(request.GET['accept'])
            return redirect(to=reverse('worker_index'))

        return_dict = {}
        current_experiment = SubmittedExperiments.objects.filter(status=SubmittedExperiments.RUNNING)
        if current_experiment.count() is not 0:
            return_dict['current_experiment'] = current_experiment[0]
        else:
            return_dict['current_experiment'] = "No experiment"
        return_dict['past_experiments'] = SubmittedExperiments.objects.order_by('-submit_date').all()[:10]
        return_dict['worker'] = WorkerInformation.objects.all()[0]
        return render(request, 'Worker/worker_index.html', return_dict)

    def set_accept_incoming_status(self, status):
        try:
            status = int(status)
            worker = WorkerInformation.objects.all()[0]
            worker.status = WorkerInformation.ACCEPT_INCOMING
            if status == WorkerInformation.DENY_INCOMING:
                worker.status = WorkerInformation.DENY_INCOMING
            worker.save()
        except Exception as e:
            print("Changing status failed: {0}".format(e))


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveWorkerInformationView(View):
    def post(self, request):
        if 'name' in request.POST:
            name = request.POST['name']
        delete_existing_worker()
        worker = WorkerInformation.objects.create(name=name, location=MASTER_URL)
        worker.save()
        return HttpResponse()


def delete_existing_worker():
    try:
        worker = WorkerInformation.objects.all()[0]
        worker.delete()
    except:
        pass


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveNewExperiment(View):
    def post(self, request):
        print("New job received")
        if 'repo_name' in request.POST:
            repo_name = request.POST['repo_name']
        if 'git_url' in request.POST:
            repo_url = request.POST['git_url']
        if 'run_id' in request.POST:
            run_id = request.POST['run_id']

        submitted_experiment = SubmittedExperiments(experiment_git_url=repo_url, repo_name=repo_name, run_id=run_id)
        submitted_experiment.save()
        clone_repo_and_start_execution.delay(submitted_experiment)
        return HttpResponse()