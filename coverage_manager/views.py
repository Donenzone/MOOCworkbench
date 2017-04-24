from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from coverage_manager.models import CodeCoverage
from coverage_manager.helpers.coveralls_helper import CoverallsHelper
from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.helper import get_github_helper
from helpers.helper import get_package_or_experiment


@login_required
def coveralls_enable(request):
    experiment = get_experiment_from_request_post(request)
    travis_instance = experiment.travis

    if travis_instance.enabled:
        existing_config = enable_coveralls(travis_instance)
        github_helper = get_github_helper(request, experiment)
        coveralls_helper = CoverallsHelper(github_helper.owner, github_helper.repo_name)
        if coveralls_helper.coverage_enabled_check():
            existing_config.badge_url = coveralls_helper.get_badge_url()
            existing_config.save()
            return JsonResponse({'enabled': True})
        else:
            return JsonResponse({'enabled': False, 'message': 'Invalid response from Coveralls. '
                                                              'Are you sure you flipped the switch on Coveralls?'})
    else:
        return JsonResponse({'enabled': False, 'message': 'First enable Travis CI builds!'})


@login_required
def coveralls_disable(request):
    experiment = get_experiment_from_request_post(request)
    travis_instance = experiment.travis

    current_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    if current_config:
        current_config = current_config[0]
        current_config.enabled = False
        current_config.save()

        return JsonResponse({'disabled': True})

    return JsonResponse({'disabled': False})


@login_required
def coveralls_status(request, object_id, object_type):
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    travis_instance = exp_or_package.travis
    context = {}
    current_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    context['object_id'] = exp_or_package.id
    context['configured'] = False
    context['travis'] = travis_instance.enabled
    if current_config:
        context['current_config'] = current_config[0]
        context['configured'] = context['current_config'].enabled
    return render(request, 'coverage_manager/coverage_status.html', context)


def coveralls_create(travis_instance):
    new_coveralls = CodeCoverage(travis_instance=travis_instance)
    new_coveralls.save()

    return new_coveralls


def get_experiment_from_request_post(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    return verify_and_get_experiment(request, experiment_id)


def enable_coveralls(travis_instance):
    """
    Checks if code coverage object exists. If so, sets the enabled 
    property to true, else creates a new one with default settings
    (where enabled is automatically true)
    :param travis_instance: The travis instance to check for
    :return: None
    """
    coverage_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    if coverage_config:
        coverage_config = coverage_config[0]
        coverage_config.enabled = True
        coverage_config.save()
    else:
        coverage_config = coveralls_create(travis_instance)
    return coverage_config

