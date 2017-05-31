import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.helper import get_user_repositories
from user_manager.models import get_workbench_user

from ..forms import ExperimentForm
from ..helper import verify_and_get_experiment
from ..mixins import ExperimentContextMixin
from ..models import *
from ..tasks import initialize_repository


class StepOneExperimentCreateView(View):
    def get(self, request, experiment_id=0):
        try:
            form = ExperimentForm()
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_create/experiment_new.html", {'form': form,
                                                                                                 'experiment_id': experiment_id,
                                                                                                 'repository_list': repository_list})
        except ValueError as a:
            messages.add_message(request, messages.INFO, 'Before creating an experiment, please connect with GitHub')
            return redirect(to=reverse('view_my_profile'))

    def post(self, request, experiment_id=0):
        experiment = Experiment()
        data = request.POST.copy()
        data['owner'] = get_workbench_user(request.user).id
        form = ExperimentForm(data, instance=experiment)
        if form.is_valid():
            cookiecutter = form.cleaned_data['template']
            experiment.language = cookiecutter.language
            experiment.owner = WorkbenchUser.objects.get(user=request.user)
            experiment.save()
            initialize_repository.delay(experiment.id, cookiecutter.id)
            return redirect(to=reverse('experiment_status_create'))
        else:
            repository_list = get_user_repositories(request.user)
            return render(request, "experiments_manager/experiment_create/experiment_new.html",
                          {'form': form, 'experiment_id': experiment_id, 'repository_list': repository_list})


@login_required
def step_two_experiment_status_create(request):
    return render(request, 'experiments_manager/experiment_create/experiment_status_create.html', {})


class StepThreeChooseExperimentSteps(ExperimentContextMixin, View):
    def get(self, request, experiment_id):
        context = super(StepThreeChooseExperimentSteps, self).get(request, experiment_id)
        context['steps'] = ExperimentStep.objects.all()
        return render(request, "experiments_manager/experiment_create/experimentsteps_choose.html", context)

    def post(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        step_json_list = json.loads(request.POST['steplist'])
        counter = 1
        if step_json_list:
            delete_existing_chosen_steps(experiment)
            cookiecutter = experiment.template
            for step in step_json_list:
                step = int(step)
                step = ExperimentStep.objects.get(id=step)
                chosen_experiment_step = ChosenExperimentSteps(experiment=experiment, step=step, step_nr=counter)
                if counter == 1:
                    chosen_experiment_step.active = True
                    chosen_experiment_step.started_at = datetime.now()
                cookiecutter_location = cookiecutter.folder_file_locations.get(step=step)
                chosen_experiment_step.location = cookiecutter_location.location
                chosen_experiment_step.main_module = cookiecutter_location.main_module
                chosen_experiment_step.save()
                counter += 1
            url = reverse('experiment_first_time', kwargs={'pk': experiment.id})
            return JsonResponse({'url': url})
        else:
            return JsonResponse({'message': 'Choose at least one step'})


@login_required
def step_four_experiment_first_time(request, pk):
    experiment = verify_and_get_experiment(request, pk)
    context = {}
    gh_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    context['object'] = experiment
    context['object_type'] = ExperimentPackageTypeMixin.EXPERIMENT_TYPE
    context['object_id'] = experiment.pk
    context['configured'] = experiment.travis.enabled
    context['github_username'] = gh_helper.owner
    context['reposlug'] = experiment.git_repo.name
    context['travis'] = experiment.travis
    if experiment.travis.codecoverage_set:
        context['coverage_configured'] = experiment.travis.codecoverage_set.first().enabled
    return render(request, 'experiments_manager/experiment_create/experiment_enable_builds.html', context)
