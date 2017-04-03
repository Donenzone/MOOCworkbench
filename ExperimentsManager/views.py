from ExperimentsManager.serializer import *
from ExperimentsManager.tables import ExperimentTable
from ExperimentsManager.forms import ExperimentForm
from ExperimentsManager.models import *
from django.views.generic.detail import DetailView
from django.utils import timezone
from GitManager.views import *
from django.views import View
from ExperimentsManager.serializer import serializer_experiment_run_factory
from UserManager.models import get_workbench_user
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.http import HttpResponseRedirect, JsonResponse
from ExperimentsManager.tasks import initialize_repository
from QualityManager.utils import get_measurement_messages_for_experiment
from django.contrib.auth.decorators import login_required
import json
from ExperimentsManager.helper import verify_and_get_experiment
import markdown
from django.contrib import messages
from BuildManager.models import TravisInstance
from RequirementsManager.models import ExperimentRequirement

class ExperimentDetailView(DetailView):
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        experiment = Experiment.objects.get(id=self.kwargs['pk'])
        github_helper = GitHubHelper(self.request.user, experiment.git_repo.name)
        context['steps'] = get_steps(experiment)
        context['git_list'] = get_git_list(self.request.user, experiment, github_helper)
        context['measurements'] = get_measurement_messages_for_experiment(experiment)
        context['what_now_list'] = what_to_do_now(experiment)
        return context

def get_git_list(user, experiment, github_helper, step=None):
    if not step:
        step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
    return github_helper.list_files_in_repo(step.folder_name())

def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')

def what_to_do_now(experiment):
    message_list = []
    
    message_list.append(what_to_do_now_ci(experiment))

    message_list.append(what_to_do_now_req(experiment))

    vcs_message = "Make sure to commit and push daily and in small pieces"
    message_list.append(vcs_message)
    return message_list

def what_to_do_now_ci(experiment):
    ci_message = "Enable Travis Builds on the Continuous Integration tab"
    ci_enabled = False
    ci_enabled_check = TravisInstance.objects.filter(experiment=experiment)
    if ci_enabled_check.count() is not 0:
        ci_enabled = ci_enabled_check[0].enabled
    if not ci_enabled:
        return ci_message

def what_to_do_now_req(experiment):
    req_message = "Add some packages you wish to use on the Manage Your Requirements tab"
    reqs_defined = False
    reqs_list = ExperimentRequirement.objects.filter(experiment=experiment)
    if reqs_list.count() is not 0:
        reqs_defined = True
    if not reqs_defined:
        return req_message

@login_required
def get_git_list_for_step(request):
    assert 'experiment_id' in request.GET
    assert 'step_id' in request.GET

    step_id = request.GET['step_id']
    experiment_id = request.GET['experiment_id']
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user

    step = ChosenExperimentSteps.objects.get(id=step_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    file_list = get_git_list(request.user, experiment, github_helper, step)
    return_dict = []
    for content_file in file_list:
        return_dict.append((content_file.name, content_file.type))
    return JsonResponse({'files': return_dict})

@login_required
def complete_step_and_go_to_next(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    if experiment.owner.user == request.user:
        active_step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
        active_step.active = False
        active_step.completed = True
        active_step.save()
        next_step_nr = active_step.step_nr + 1
        next_step = ChosenExperimentSteps.objects.filter(experiment=experiment, step_nr=next_step_nr)
        if next_step.count() != 0:
            next_step = next_step[0]
            next_step.active = True
            next_step.save()
            return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id}))
        else:
            return JsonResponse({'completed': True})

@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)

    return render(request, 'ExperimentsManager/experiments_table.html', {'table': table})


class CreateExperimentView(View):
    def get(self, request, experiment_id=0):
        try:
            form = ExperimentForm()
            repository_list = get_user_repositories(request.user)
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id,
                                                                'repository_list': repository_list})
        except ValueError as a:
            messages.add_message(request, messages.INFO, 'Before creating an experiment, please sign in with GitHub')
            return redirect(to=reverse('view_my_profile'))

    def post(self, request, experiment_id=0):
        experiment = Experiment()

        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            if form.cleaned_data['new_git_repo']:
                git_repo = create_new_github_repository_local(experiment.title, request.user, 'python', experiment)
                experiment.git_repo = git_repo
                experiment.save()
            elif request.POST['github'] is not '':
                git_repo = GitRepository()
                git_repo.title = experiment.title
                git_repo.git_url = request.POST['github']
                git_repo.owner = experiment.owner
                git_repo.save()
                experiment.git_repo = git_repo
            return redirect(to=reverse('choose_experiment_steps', kwargs={'experiment_id': experiment.id}))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "ExperimentsManager/edit_new_experiment.html", {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})

class ChooseExperimentSteps(View):
    def get(self, request, experiment_id):
        experiment = Experiment.objects.get(id=experiment_id)
        assert request.user == experiment.owner.user
        context = {}
        context['steps'] = ExperimentStep.objects.all()
        context['experiment_id'] = experiment_id
        return render(request, "ExperimentsManager/choose_experiment_steps.html", context)

    def post(self, request, experiment_id):
        experiment = Experiment.objects.get(id=experiment_id)
        workbench_user =  get_workbench_user(request.user)
        if experiment.owner == workbench_user:
            step_list = []
            step_json_list = json.loads(request.POST['steplist'])
            counter = 1
            delete_existing_chosen_steps(experiment)
            for step in step_json_list:
                step = int(step)
                step = ExperimentStep.objects.get(id=step)
                chosen_experiment_step = ChosenExperimentSteps(experiment=experiment, step=step, step_nr=counter)
                if counter == 1:
                    chosen_experiment_step.active = True
                chosen_experiment_step.save()
                counter += 1
            initialize_repository.delay(experiment_id)
            url = reverse('experiment_detail', kwargs={'pk': experiment_id})
            return JsonResponse({'url': url})


@login_required
def view_file_in_git_repository(request, experiment_id):
    if request.method == 'GET':
        file_name = request.GET['file_name']
        experiment = verify_and_get_experiment(request, experiment_id)
        github_helper = GitHubHelper(request.user, experiment.git_repo.name)
        content_file = github_helper.view_file_in_repo(file_name)
        return render(request, 'ExperimentsManager/file_detail.html', {'content_file': content_file, 'name': file_name})


@login_required
def readme_of_experiment(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    content_file = github_helper.view_file_in_repo('README.md')
    content_file = markdown.markdown(content_file)
    return render(request, 'ExperimentsManager/experiment_readme.html', {'readme': content_file})


@login_required
def view_list_files_in_repo_folder(request, pk):
    if request.method == 'GET':
        folder_name = request.GET['folder_name']
        expirement = Experiment.objects.get(id=pk)
        data = list_files_in_repo_folder('gitrepository1', request.user.username, folder_name)
        print(data)
        return render(request, 'ExperimentsManager/folder_detail.html', {'contents': data, 'pk': pk})
