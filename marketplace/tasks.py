import logging

from celery.task import periodic_task

from django.shortcuts import reverse

from experiments_manager.consumers import \
    send_exp_package_creation_status_update, send_message
from experiments_manager.models import Experiment
from git_manager.utils.repo_init import PackageGitRepoInit
from MOOCworkbench.celery import app

from .models import InternalPackage, update_all_versions

logger = logging.getLogger(__name__)


@periodic_task(run_every=30)
def task_check_for_new_package_version():
    """Task to iterate all external packages,
    and check PyPi for new versions, and add those automatically"""
    update_all_versions()


@app.task
def task_create_package(internalpackage_id):
    """Task to create a new empty internal package
    :param internalpackage_id: The PK for an existing internal package"""
    package = InternalPackage.objects.get(pk=internalpackage_id)
    username = package.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    create_package(package, username)


@app.task
def task_create_package_from_experiment(internalpackage_id, experiment_id, step_folder):
    """Task to create an internal package based off of an experiment and step
    :param internalpackage_id: The PK for an existing internalpackage
    :param experiment_id: The PK for the experiment
    :param step_folder: The string for the relevant folder to filter and add to the new package"""
    package = InternalPackage.objects.get(pk=internalpackage_id)
    experiment = Experiment.objects.get(pk=experiment_id)
    username = experiment.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    create_package(package, username, experiment, step_folder)


def create_package(package, username, experiment=None, step_folder=None):
    """Create a package from an InternalPackage object and the username
    Optionally provide the experiment with the step_folder to place code in that folder into
    this new package
    :param package: existing InternalPackage object
    :param username: Username for who to create this package
    :param experiment: Optional experiment for which to take existing code
    :param step_folder: Optional folder location in the experiment with the code to take"""
    try:
        package_repo = PackageGitRepoInit(package, username, experiment, step_folder)
        if not package_repo.existing_repo:
            package.git_repo = package_repo.init_repo_boilerplate()
        package.save()
        redirect_url = package.get_absolute_url()
        send_exp_package_creation_status_update(username, 7, completed=True, redirect_url=redirect_url)
    except Exception as e:
        logger.error("package creation of %s failed for %s with error %s", package, username, e)
        error = "Package creation failed. Undoing changes..."
        redirect_url = reverse('internalpackage_create')
        package.delete()
        send_exp_package_creation_status_update(username, 7, completed=False, redirect_url=redirect_url, error=error)


@app.task
def task_publish_update_package(internalpackage_id):
    """Task to publish and/or update an existing internal package"""
    package = InternalPackage.objects.get(pk=internalpackage_id)
    language_helper = package.language_helper()
    language_helper.publish_package()


@app.task
def task_remove_package(internalpackage_id):
    """Task to remove a published internal package"""
    package = InternalPackage.objects.get(pk=internalpackage_id)
    language_helper = package.language_helper()
    language_helper.remove_package()
    send_message(package.owner.user.username, 'success', 'Package removed successfully')
