from MOOCworkbench.celery import app
from git_manager.utils.repo_init import PackageGitRepoInit
from experiments_manager.models import Experiment
from experiments_manager.consumers import send_exp_package_creation_status_update

from .models import update_all_versions, InternalPackage


@app.task
def task_check_for_new_package_version():
    update_all_versions()


@app.task
def task_create_package_from_experiment(internalpackage_id, experiment_id, step_folder):
    package = InternalPackage.objects.get(pk=internalpackage_id)
    experiment = Experiment.objects.get(pk=experiment_id)
    username = experiment.owner.user.username
    send_exp_package_creation_status_update(username, 1)
    package_repo = PackageGitRepoInit(package, experiment, step_folder, username)
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