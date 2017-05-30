from helpers.helper import get_package_or_experiment


def get_exp_or_package_from_request(request):
    assert 'object_id' in request.POST
    assert 'object_type' in request.POST
    object_id = request.POST['object_id']
    object_type = request.POST['object_type']
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    return exp_or_package

