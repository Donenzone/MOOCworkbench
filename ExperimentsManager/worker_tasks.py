from RunManager.run_manager import setup_docker_image, start_code_run
from helpers.dir_helpers import *
from git import Repo
from .serializer import serializer_experiment_run_factory
from celery import task
from helpers.url_helper import build_url
import requests
import io
from MOOCworkbench.settings import MASTER_URL
from .models import ExperimentWorkerRun
from django.db.models.signals import post_save
from django.dispatch import receiver
from MOOCworkbench.settings import MASTER_OR_WORKER, WORKER
from RunManager.run_manager import setup_docker_image, start_code_run
from helpers.dir_helpers import *
from git import Repo
from django.core import serializers


@receiver(post_save, sender=ExperimentWorkerRun)
def start_experiment_run(sender, instance, **kwargs):
    if MASTER_OR_WORKER is WORKER and instance.status is not ExperimentWorkerRun.RUNNING: # then after a POST run the experiment
        clone_repo_and_start_execution.delay(instance)
    elif MASTER_OR_WORKER is WORKER and instance.status is ExperimentWorkerRun.CANCELLED:
        pass # cancel the current run
    elif MASTER_OR_WORKER is WORKER and instance.status is  ExperimentWorkerRun.SUCCESS:
        send_completion_information_to_master.delay(instance) # post updated results to master

@task
def clone_repo_and_start_execution(submitted_experiment):
    remove_if_existing_worker_repository(submitted_experiment.repo_name)
    Repo.clone_from(submitted_experiment.experiment_git_url, to_path=get_worker_repository_folder_path(submitted_experiment.repo_name))
    start_code_execution(submitted_experiment)
    print(submitted_experiment)
    send_completion_information_to_master(submitted_experiment)


@task
def send_completion_information_to_master(submitted_experiment):
    json = serializer_experiment_run_factory(ExperimentWorkerRun)(submitted_experiment)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    requests.post(build_url(MASTER_URL, ['api', 'master', 'experiment-run', submitted_experiment.id], 'POST'), data=json, headers=headers)


def send_output_to_master(run_id, line):
    data = {'run_id': run_id, 'line': line}
    requests.post(build_url(MASTER_URL, ['worker-manager', 'output'], 'POST'), data=data)


@task
def return_docker_output(submitted_experiment, proc):
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        submitted_experiment.append_to_output(line)
        send_output_to_master(submitted_experiment.run_id, line)


@task
def start_code_execution(submitted_experiment):
    proc = setup_docker_image(submitted_experiment.repo_name)
    return_docker_output(submitted_experiment, proc)
    proc = start_code_run()
    return_docker_output(submitted_experiment, proc)