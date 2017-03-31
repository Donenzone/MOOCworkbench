from django.shortcuts import render
from django.views import View
from ExperimentsManager.models import Experiment
from ExperimentsManager.helper import verify_and_get_experiment
from BuildManager.models import TravisInstance, TravisCiConfig
from BuildManager.travis_ci_helper import TravisCiHelper
from GitManager.github_helper import GitHubHelper
from GitManager.helper import get_github_helper
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from travispy import TravisPy
from BuildManager.tasks import get_last_log_for_build_task
# Create your views here.

@login_required
def enable_ci_builds(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)

    existing_config = TravisInstance.objects.filter(experiment=experiment)
    if existing_config.count() is not 0:
        existing_config = existing_config[0]
        existing_config.enabled = True
        existing_config.save()
        enable_travis(request, experiment)
    else:
        create_new_ci_config(request, experiment)

    return JsonResponse({'enabled': True})


@login_required
def disable_ci_builds(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)

    current_config = TravisInstance.objects.get(experiment=experiment)
    current_config.enabled = False
    current_config.save()

    github_helper = get_github_helper(request, experiment)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.disable_travis_for_repository()

    return JsonResponse({'disabled': True})


def create_new_ci_config(request, experiment):
    new_ci_config = TravisCiConfig()
    new_ci_config.save()
    new_ci = TravisInstance(experiment=experiment, config=new_ci_config)
    new_ci.save()

    enable_travis(request, experiment)

    return new_ci

def enable_travis(request, experiment):
    github_helper = get_github_helper(request, experiment)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.enable_travis_for_repository()

@login_required
def build_experiment_now(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)

    github_helper = get_github_helper(request, experiment)
    trigger_build_for_repo(github_helper)

    return JsonResponse({'build_started': True})


@login_required
def build_status(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    context = {}
    current_config = TravisInstance.objects.filter(experiment=experiment)
    context['experiment_id'] = experiment.id
    context['configured'] = False
    if current_config.count() is not 0:
        context['current_config'] = current_config[0]
        context['configured'] = context['current_config'].enabled
        github_helper = get_github_helper(request, experiment)
        travis_helper = TravisCiHelper(github_helper)
        context['reposlug'] = github_helper.github_repository.name
        context['username'] = travis_helper.travis_user.login
    return render(request, 'BuildManager/build_status.html', context)

@login_required
def get_log_from_last_build(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = get_github_helper(request, experiment)
    travis_helper = TravisCiHelper(github_helper)
    log = travis_helper.get_log_for_last_build()
    return JsonResponse({'log': log})
