import os
import shutil
import subprocess

from django.conf import settings

from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper

PACKAGES_DIR = os.path.join(settings.PROJECT_ROOT, 'packages')


def internalpackage_publish_update(package):
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
    # clone/pull repository
    github_helper = GitHubHelper(package.owner, package.git_repo.name)
    git_helper = GitHelper(github_helper)
    git_helper.clone_or_pull_repository()

    old_name = '{0}.zip'.format(old_name)
    # copy repository to packages
    old_dst_dir = os.path.join(PACKAGES_DIR, old_name)
    if os.path.exists(old_dst_dir):
        shutil.rmtree(old_dst_dir)
    internalpackage_publish_update(package)


def internalpackage_remove(package):
    package_file_name = '{0}.zip'.format(package.git_repo.name)
    dst_dir = os.path.join(PACKAGES_DIR, package_file_name)
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
