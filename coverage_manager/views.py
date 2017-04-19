from django.shortcuts import render
from django.http import JsonResponse
from coverage_manager.models import CodeCoverage
from build_manager.models import TravisInstance
from django.contrib.auth.decorators import login_required
from experiments_manager.helper import verify_and_get_experiment
from git_manager.helpers.helper import get_github_helper
from coverage_manager.helpers.coveralls_helper import CoverallsHelper


@login_required
def coveralls_enable(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)
    travis_instance = experiment.travis

    if travis_instance.enabled:
        existing_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
        if existing_config:
            existing_config = existing_config[0]
            existing_config.enabled = True
            existing_config.save()
        else:
            coveralls_create(travis_instance)

        github_helper = get_github_helper(request, experiment)
        coveralls_helper = CoverallsHelper(github_helper.owner, github_helper.repo_name)
        if coveralls_helper.coverage_enabled_check():
            existing_config.badge_url = coveralls_helper.get_badge_url()
            existing_config.save()
            return JsonResponse({'enabled': True})
        else:
            return JsonResponse({'enabled': False, 'message': 'Invalid response from Coveralls. Are you sure you flipped the switch on Coveralls?'})
    else:
        return JsonResponse({'enabled': False, 'message': 'First enable Travis CI builds!'})


@login_required
def coveralls_disable(request):
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)
    travis_instance = experiment.travis

    current_config = CodeCoverage.objects.get(travis_instance=travis_instance)
    current_config.enabled = False
    current_config.save()

    return JsonResponse({'disabled': True})


@login_required
def coveralls_status(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    travis_instance = experiment.travis
    context = {}
    if travis_instance:
        current_config = CodeCoverage.objects.filter(travis_instance=travis_instance)
        context['experiment_id'] = experiment.id
        context['configured'] = False
        context['travis'] = travis_instance.enabled
        if current_config:
            context['current_config'] = current_config[0]
            context['configured'] = context['current_config'].enabled
    else:
        context['travis'] = False
    return render(request, 'coverage_manager/coverage_status.html', context)


def coveralls_create(travis_instance):
    new_coveralls = CodeCoverage(travis_instance=travis_instance)
    new_coveralls.save()

    return new_coveralls
