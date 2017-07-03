import shutil

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.models import Experiment
from marketplace.models import InternalPackage
from MOOCworkbench.settings import ALLOWED_HOSTS, BASE_DIR

from .helper_mixins import ExperimentPackageTypeMixin


def get_package_or_experiment(request, object_type, object_id):
    """Gets either a package or an experiment
    :param request: Request object of view
    :param object_type: One of the options from ExperimentPackageTypeMixin
    :param object_id: PK of the object

    :return: Returns package, or returns experiment, for experiment the owner is first checked"""
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        return verify_and_get_experiment(request, object_id)
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        return InternalPackage.objects.get(id=object_id)


def get_package_or_experiment_with_context(context, request, object_type, object_id):
    """Gets package or experiment and adds it to the context object with key object"""
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        context['object'] = verify_and_get_experiment(request, object_id)
        return context
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        context['package'] = InternalPackage.objects.get(id=object_id)
        context['object'] = InternalPackage.objects.get(id=object_id)
        return context


def get_package_or_experiment_without_request(object_type, object_id):
    """If no request object is available, use this function to retrieve package or experiment"""
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        return Experiment.objects.get(pk=object_id)
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        return InternalPackage.objects.get(id=object_id)


def get_absolute_path():
    return BASE_DIR


def get_absolute_url(to):
    return 'https://{0}{1}'.format(ALLOWED_HOSTS[0], to)
