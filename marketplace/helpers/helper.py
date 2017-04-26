from marketplace.models import PackageVersion, InternalPackage
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.helper import get_file_from_code_template
from helpers.helper import replace_variable_in_file
from git_manager.helpers.helper import CodeTemplateTypes


def create_tag_for_package_version(package_version_id):
    package_version = PackageVersion.objects.get(pk=package_version_id)
    internalpackage = InternalPackage.objects.get(pk=package_version.package.pk)
    github = GitHubHelper(internalpackage.owner, internalpackage.git_repo.name)
    github.create_release(package_version.version_nr, package_version.version_nr, package_version.changelog, package_version.pre_release)


def update_setup_py_with_new_version(package_version_id):
    package_version = PackageVersion.objects.get(pk=package_version_id)
    internal_package = InternalPackage.objects.get(pk=package_version.package.pk)
    github = GitHubHelper(internal_package.owner, internal_package.git_repo.name)
    setup_py_template = get_file_from_code_template(CodeTemplateTypes.PACKAGE_TYPE, 'setup.py_template')
    setup_py = build_setup_py(internal_package, setup_py_template, package_version)
    github.update_file('setup.py', contents=setup_py, commit_message="Updated setup.py for new version")


def build_setup_py(internal_package, setup_py_template, package_version=None):
    version = '0.1' if not package_version else package_version.version_nr
    var_list = []
    var_list.append((SetupPyVariables.PACKAGE_NAME_VAR, internal_package.package_name))
    var_list.append((SetupPyVariables.VERSION_VAR, version))
    var_list.append((SetupPyVariables.AUTHOR_VAR, str(internal_package.owner.user)))
    var_list.append((SetupPyVariables.DESCRIPTION_VAR, internal_package.description))
    var_list.append((SetupPyVariables.URL_VAR, 'http://test'))
    var_list.append((SetupPyVariables.AUTHOR_MAIL, internal_package.owner.user.email))
    var_list.append((SetupPyVariables.LICENSE_VAR, 'No License'))
    var_list.append((SetupPyVariables.PACKAGE_VAR, internal_package.python_package_name))
    for var in var_list:
        setup_py_template = replace_variable_in_file(setup_py_template, var[0], var[1])
    return setup_py_template


class SetupPyVariables(object):
    PACKAGE_NAME_VAR = 'PACKAGE_NAME'
    VERSION_VAR = 'VERSION'
    AUTHOR_VAR = 'AUTHOR'
    DESCRIPTION_VAR = 'DESCRIPTION'
    URL_VAR = 'URL'
    AUTHOR_MAIL = 'AUTHOR_EMAIL'
    LICENSE_VAR = 'LICENSE'
    PACKAGE_VAR = 'PACKAGE'