"""View functions for coverage_manager app"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from git_manager.helpers.github_helper import get_github_helper
from helpers.helper import get_package_or_experiment

from .helpers.coveralls_helper import CoverallsHelper, get_experiment_from_request_post, enable_coveralls
from .models import CodeCoverage

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@login_required
def coveralls_enable(request):
    """Enable coveralls for an experiment"""
    experiment = get_experiment_from_request_post(request)
    travis_instance = experiment.travis

    if travis_instance.enabled:
        existing_config = enable_coveralls(travis_instance)
        github_helper = get_github_helper(request, experiment)
        coveralls_helper = CoverallsHelper(github_helper.owner, github_helper.repo_name)
        if coveralls_helper.coverage_enabled_check():
            existing_config.save()
            logger.debug('enabled coveralls for: %s', experiment)
            return JsonResponse({'enabled': True})
        return JsonResponse({'enabled': False, 'message': 'Invalid response from Coveralls. '
                                                          'Are you sure you flipped the switch on Coveralls?'})
    logger.debug('tried to enable coveralls, travis was not enabled: %s, %s', experiment, travis_instance)
    return JsonResponse({'enabled': False, 'message': 'First enable Travis CI builds!'})


@login_required
def coveralls_disable(request):
    """Disable coveralls for an experiment"""
    experiment = get_experiment_from_request_post(request)
    travis_instance = experiment.travis

    current_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    if current_config:
        current_config = current_config[0]
        current_config.enabled = False
        current_config.save()

        logger.debug('disabled coveralls for: %s, %s', experiment, travis_instance)
        return JsonResponse({'disabled': True})

    return JsonResponse({'disabled': False})


@login_required
@csrf_exempt
def coveralls_filecoverage(request):
    """Get file coverage percentage for a specific file
    Make sure filename parameter is present in request.POST"""
    experiment = get_experiment_from_request_post(request)
    assert 'filename' in request.POST
    coverage = -1
    if experiment.travis.codecoverage_set.first().enabled:
        filename = request.POST['filename']
        github_helper = get_github_helper(request, experiment)
        coverage_helper = CoverallsHelper(github_helper.owner, github_helper.repo_name)
        coverage = coverage_helper.get_file_coverage(filename)
        logger.debug('coveralls file coverage for file %s with coverage %s: %s', filename, coverage, experiment)
    return JsonResponse({'coverage': coverage})


@login_required
def coveralls_status(request, object_id, object_type):
    """Get coveralls status for an experiment given an object_id (pk) and an object_type
    (ExperimentPackageType). Status is present in context dictionary."""
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    travis_instance = exp_or_package.travis
    context = {}
    current_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
    context['object_id'] = exp_or_package.id
    context['coverage_configured'] = False
    context['travis'] = travis_instance
    if current_config:
        context['current_config'] = current_config[0]
        context['coverage_configured'] = context['current_config'].enabled
    logger.debug('fetched coveralls status %s: %s', exp_or_package, context)
    return render(request, 'coverage_manager/coverage_status.html', context)
