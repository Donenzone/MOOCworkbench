import os
import shutil
import subprocess

from django.conf import settings

from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper

PACKAGES_DIR = os.path.join(settings.PROJECT_ROOT, 'packages')


def internalpackage_publish_update(package):
    """Publishes an internalpackage, or, if it is already published, publishes a new version.
    This function is for Python only and publishes packages on the PyPi server.
    :param package: The package to publish or update"""
    # clone/pull repository
    # copy repository to packages
    package_location = os.path.join(PACKAGES_DIR, package.git_repo.name)
    if not os.path.exists(package_location):
        github_helper = GitHubHelper(package.owner, package.git_repo.name)
        git_helper = GitHelper(github_helper)
        git_helper.clone_or_pull_repository()
        shutil.copytree(git_helper.repo_dir, package_location)
    else:
        subprocess.call(['git', 'pull'], cwd=package_location)
    subprocess.call(['./shell_scripts/publish_package.sh', package_location])


def internalpackage_rename(package, old_name):
    """Rename an internalpackage, consists of removing the old one
    and re-publishing the one with the new name."""
    internalpackage_remove(old_name)
    internalpackage_publish_update(package)


def internalpackage_remove(package_name):
    """Removes an internal package by deleting the folder on the PyPi packages dir
    :param package_name: String of package to remove"""
    dst_dir = os.path.join(PACKAGES_DIR, package_name)
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
