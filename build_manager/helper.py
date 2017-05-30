"""Helper module for build_manager with function to get exp or package from request"""
from build_manager.travis_ci_helper import TravisCiHelper
from git_manager.helpers.helper import get_github_helper
from helpers.helper import get_package_or_experiment


def get_exp_or_package_from_request(request):
    """Get experiment or internalpackage from request.
    Request.POST should contain object_id (pk) and object_type (ExperimentPackageType)"""
    assert 'object_id' in request.POST
    assert 'object_type' in request.POST
    object_id = request.POST['object_id']
    object_type = request.POST['object_type']
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    return exp_or_package


def enable_travis(request, exp_or_package):
    """Enable travis for experiment or internalpackage"""
    github_helper = get_github_helper(request, exp_or_package)
    travis_ci_helper = TravisCiHelper(github_helper)
    travis_ci_helper.enable_travis_for_repository()
