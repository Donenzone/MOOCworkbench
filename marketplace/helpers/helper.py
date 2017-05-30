from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.helper import (CodeTemplateTypes,
                                        get_file_from_code_template)
from helpers.helper import replace_variable_in_file
from marketplace.models import InternalPackage, PackageVersion


def create_tag_for_package_version(package_version_id):
    package_version = PackageVersion.objects.get(pk=package_version_id)
    internalpackage = InternalPackage.objects.get(pk=package_version.package.pk)
    github = GitHubHelper(internalpackage.owner, internalpackage.git_repo.name)
    github.create_release(package_version.version_nr, package_version.version_nr, package_version.changelog, package_version.pre_release)


def update_setup_py_with_new_version(package_version_id):
    package_version = PackageVersion.objects.get(pk=package_version_id)
    internal_package = InternalPackage.objects.get(pk=package_version.package.pk)
    gh_helper = GitHubHelper(internal_package.owner, internal_package.git_repo.name)
    setup_py = gh_helper.view_file('setup.py')
    setup_py = update_setup_py_new_version(package_version.version_nr, setup_py)
    gh_helper.update_file('setup.py', contents=setup_py, commit_message="Updated setup.py for new version")


def update_setup_py_new_version(version_nr, setup_py):
    new_setup_py = ''
    for line in setup_py.split('\n'):
        if '__version__ =' in line:
            new_setup_py += '__version__ = \'{0}\'\n'.format(version_nr)
        else:
            new_setup_py += '{0}\n'.format(line)
    return new_setup_py


class SetupPyVariables(object):
    PACKAGE_NAME_VAR = 'PACKAGE_NAME'
    VERSION_VAR = 'VERSION'
    AUTHOR_VAR = 'AUTHOR'
    DESCRIPTION_VAR = 'DESCRIPTION'
    URL_VAR = 'URL'
    AUTHOR_MAIL = 'AUTHOR_EMAIL'
    LICENSE_VAR = 'LICENSE'
    PACKAGE_VAR = 'PACKAGE'
