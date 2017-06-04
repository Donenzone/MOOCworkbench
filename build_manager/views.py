"""Views for build_manager, that manages CI config for experiments"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from travispy.errors import TravisError

from build_manager.travis_ci_helper import TravisCiHelper
from git_manager.helpers.github_helper import get_github_helper
from helpers.helper import get_package_or_experiment
from quality_manager.tasks import task_ci_quality_check

from .helper import get_exp_or_package_from_request, enable_travis

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@login_required
def enable_ci_builds(request):
    """Enable CI builds for experiment
    Expects object_id and object_type in request.POST"""
    exp_or_package = get_exp_or_package_from_request(request)

    existing_config = exp_or_package.travis
    existing_config.enabled = True
    existing_config.save()
    enable_travis(request, exp_or_package)

    logger.debug('enabled CI builds for: %s', exp_or_package)

    return JsonResponse({'enabled': True})


@login_required
def disable_ci_builds(request):
    """Disable CI builds for experiment
    Expects object_id and object_type in request.POST"""
    exp_or_package = get_exp_or_package_from_request(request)

    current_config = exp_or_package.travis
    current_config.enabled = False
    current_config.save()

    github_helper = get_github_helper(request, exp_or_package)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.disable_travis_for_repository()

    logger.debug('disabled CI builds for: %s', exp_or_package)

    return JsonResponse({'disabled': True})


@login_required
def build_experiment_now(request):
    """Start a build for an experiment in CI now"""
    exp_or_package = get_exp_or_package_from_request(request)

    github_helper = get_github_helper(request, exp_or_package)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.trigger_build_for_repo()

    logger.debug('building experiment now for %s', exp_or_package)

    return JsonResponse({'build_started': True})


@login_required
def build_status(request, object_id, object_type):
    """Get the build status for an experiment"""
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    context = {}
    current_config = exp_or_package.travis
    context['object_id'] = exp_or_package.id
    context['object_type'] = object_type
    context['configured'] = False
    if current_config:
        context['current_config'] = current_config
        context['configured'] = context['current_config'].enabled
        github_helper = get_github_helper(request, exp_or_package)
        context['reposlug'] = exp_or_package.git_repo.name
        context['github_username'] = github_helper.github_repository.owner.login

    logger.debug('build status for %s with config %s', exp_or_package, context)
    return render(request, 'build_manager/build_status.html', context)


@login_required
def get_log_from_last_build(request, object_id, object_type):
    """Get log from last build given object_id and object_type
    If no log exists, return error message"""
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    github_helper = get_github_helper(request, exp_or_package)
    travis_helper = TravisCiHelper(github_helper)
    try:
        log = travis_helper.get_log_for_last_build()
        logger.debug('fetched log for last build for %s', exp_or_package)
        return JsonResponse({'log': log})
    except TravisError:
        return JsonResponse({'log': 'Failed to retrieve log'})
