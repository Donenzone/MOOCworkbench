from django.shortcuts import render
from django.views import View
from ExperimentsManager.models import Experiment
from ExperimentsManager.helper import verify_and_get_experiment
from BuildManager.models import TravisInstance, TravisCiConfig
from BuildManager.utils import trigger_build_for_repo
from BuildManager.utils import enable_travis_for_repository
from BuildManager.utils import get_repo_slug
from GitManager.github_helper import GitHubHelper
from GitManager.helper import get_github_helper
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from travispy import TravisPy
# Create your views here.

@login_required
def create_new_ci_config(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)

    new_ci_config = TravisCiConfig()
    new_ci_config.save()
    new_ci = TravisInstance(experiment=experiment, config=new_ci_config)
    new_ci.save()

    github_helper = get_github_helper(request, experiment)
    enable_travis_for_repository(github_helper)

    return JsonResponse({'enabled': True})


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
    configured = False
    if current_config.count() is not 0:
        current_config = current_config[0]
        configured = True
        github_helper = get_github_helper(request, experiment)
        t = TravisPy.github_auth(github_helper.socialtoken)
        travis_user = t.user()
        reposlug = github_helper.github_repository.name
        username = travis_user.login
    context = {'configured': configured, 'current_config': current_config, 'experiment_id': experiment.id,
               'reposlug': reposlug, 'username': username}
    return render(request, 'BuildManager/build_status.html', context)
