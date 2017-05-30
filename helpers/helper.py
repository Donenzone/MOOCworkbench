import shutil

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.models import Experiment
from marketplace.models import InternalPackage
from MOOCworkbench.settings import ALLOWED_HOSTS, BASE_DIR

from .helper_mixins import ExperimentPackageTypeMixin


def get_package_or_experiment(request, object_type, object_id):
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        return verify_and_get_experiment(request, object_id)
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        return InternalPackage.objects.get(id=object_id)


def get_package_or_experiment_with_context(context, request, object_type, object_id):
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        context['object'] = verify_and_get_experiment(request, object_id)
        return context
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        context['package'] = InternalPackage.objects.get(id=object_id)
        return context


def get_package_or_experiment_without_request(object_type, object_id):
    if object_type == ExperimentPackageTypeMixin.EXPERIMENT_TYPE:
        return Experiment.objects.get(pk=object_id)
    elif object_type == ExperimentPackageTypeMixin.PACKAGE_TYPE:
        return InternalPackage.objects.get(id=object_id)


def replace_variable_in_file(contents, variable, value):
    variable_name = '{{{0}}}'.format(variable)
    return contents.replace(variable_name, value)


def get_absolute_path():
    return BASE_DIR


def get_absolute_url(to):
    return 'https://{0}{1}'.format(ALLOWED_HOSTS[0], to)
