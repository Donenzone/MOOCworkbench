from celery.task import periodic_task

from experiments_manager.consumers import \
    send_exp_package_creation_status_update
from experiments_manager.models import Experiment
from git_manager.utils.repo_init import PackageGitRepoInit
from MOOCworkbench.celery import app

from .models import InternalPackage, update_all_versions


@periodic_task(run_every=30)
def task_check_for_new_package_version():
    update_all_versions()

@app.task
def task_create_package(internalpackage_id):
    package = InternalPackage.objects.get(pk=internalpackage_id)
    username = package.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    package_repo = PackageGitRepoInit(package, username)
    if not package_repo.existing_repo:
        package.git_repo = package_repo.init_repo_boilerplate()
    package.save()
    redirect_url = package.get_absolute_url()
    send_exp_package_creation_status_update(username, 7, completed=True, redirect_url=redirect_url)

@app.task
def task_create_package_from_experiment(internalpackage_id, experiment_id, step_folder):
    package = InternalPackage.objects.get(pk=internalpackage_id)
    experiment = Experiment.objects.get(pk=experiment_id)
    username = experiment.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    package_repo = PackageGitRepoInit(package, username, experiment, step_folder)
    if not package_repo.existing_repo:
        package.git_repo = package_repo.init_repo_boilerplate()
    package.save()
    redirect_url = package.get_absolute_url()
    send_exp_package_creation_status_update(username, 7, completed=True, redirect_url=redirect_url)


@app.task
def task_publish_update_package(internalpackage_id):
    package = InternalPackage.objects.get(pk=internalpackage_id)
    language_helper = package.language_helper()
    language_helper.publish_package()


@app.task
def task_remove_package(internalpackage_id):
    package = InternalPackage.objects.get(pk=internalpackage_id)
    language_helper = package.language_helper()
    language_helper.remove_package()
