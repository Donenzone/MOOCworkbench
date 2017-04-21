from helpers.helper import get_package_or_experiment_without_request


def build_requirements_file(object_id, object_type):
    exp_or_package = get_package_or_experiment_without_request(object_type, object_id)
    requirements_txt = ''
    for requirement in exp_or_package.requirements.all():
        requirements_txt += '{0}\n'.format(str(requirement))
    return requirements_txt
