from django.shortcuts import render
from experiments_manager.helper import verify_and_get_experiment
from build_manager.models import TravisInstance, TravisCiConfig
from build_manager.travis_ci_helper import TravisCiHelper
from git_manager.helper import get_github_helper
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


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



@login_required
def build_experiment_now(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)

    github_helper = get_github_helper(request, experiment)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.trigger_build_for_repo()

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
        context['reposlug'] = experiment.git_repo.name
        context['username'] = github_helper.github_repository.owner.login
    return render(request, 'build_manager/build_status.html', context)


@login_required
def get_log_from_last_build(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = get_github_helper(request, experiment)
    travis_helper = TravisCiHelper(github_helper)
    log = travis_helper.get_log_for_last_build()
    return JsonResponse({'log': log})


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
