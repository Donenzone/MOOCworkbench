import requirements

from helpers.helper import get_package_or_experiment_without_request

from .models import Requirement


def build_requirements_file(object_id, object_type):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    requirements_txt = ''
    for requirement in exp_or_package.requirements.all():
        requirements_txt += '{0}\n'.format(str(requirement))
    return requirements_txt


def parse_requirements_file(exp_or_package, requirements_file):
    for req in requirements.parse(requirements_file):
        requirement = Requirement()
        requirement.package_name = req.name
        if req.specs:
            requirement.version = req.specs[0][1]
        requirement.save()

        exp_or_package.requirements.add(requirement)
        exp_or_package.save()
