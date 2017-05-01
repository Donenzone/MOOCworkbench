from git_manager.helpers.github_helper import GitHubHelper
from helpers.helper import get_absolute_path


def get_github_helper(request, exp_or_package):
    assert exp_or_package.owner.user == request.user
    return GitHubHelper(request.user, exp_or_package.git_repo.name)


class TemplateHelper(object):
    TEMPLATE_FOLDER = '/codetemplates/'


class CodeTemplateTypes(object):
    PACKAGE_TYPE = 'pip'
    PYTHON_TYPE = 'python'


def get_file_from_code_template(type, file_name, folder=None):
    template_type_folder = '{0}{1}/'.format(TemplateHelper.TEMPLATE_FOLDER, type)
    if folder:
        path = '{0}{1}{2}{3}'.format(get_absolute_path(), template_type_folder, folder, file_name)
    else:
        path = '{0}{1}{2}'.format(get_absolute_path(), template_type_folder, file_name)
    file_to_open = open(path, 'r')
    contents = file_to_open.read()
    file_to_open.close()
    return contents



