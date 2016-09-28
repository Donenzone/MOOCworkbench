from __future__ import absolute_import
from celery import task
from celery.decorators import periodic_task
from datetime import timedelta
from MOOCworkbench.settings import MASTER_URL, WORKER_URL
import requests
from .worker_helper import get_current_status, get_worker_name
from celery.signals import celeryd_init
from helpers.url_helper import build_url
from helpers.ssh_helper import generate_ssh_private_public_key_pair
from RunManager.run_manager import setup_docker_image, start_code_run
from helpers.dir_helpers import *
from git import Repo
from django.core import serializers
import io

@task
def clone_repo_and_start_execution(submitted_experiment):
    remove_if_existing_worker_repository(submitted_experiment.repo_name)
    Repo.clone_from(submitted_experiment.experiment_git_url, to_path=get_worker_repository_folder_path(submitted_experiment.repo_name))
    start_code_execution(submitted_experiment)
    print(submitted_experiment)
    send_completion_information_to_master(submitted_experiment)


@periodic_task(run_every=timedelta(seconds=30))
def report_status_to_master():
    status = get_current_status()
    data = {'status': status, 'name': get_worker_name()}
    requests.post(build_url(MASTER_URL, ['worker-manager', 'status-report'], 'POST'), data=data)


@celeryd_init.connect()
def configure_worker(conf=None, **kwargs):
    ssh_pub_key = generate_ssh_private_public_key_pair()
    data = {'new': True, 'location': WORKER_URL, 'ssh': ssh_pub_key}
    requests.post(build_url(MASTER_URL, ['worker-manager', 'registration'], 'POST'), data=data)


@task
def start_code_execution(submitted_experiment):
    proc = setup_docker_image(submitted_experiment.repo_name)
    return_docker_output(submitted_experiment, proc)
    proc = start_code_run()
    return_docker_output(submitted_experiment, proc)


@task
def return_docker_output(submitted_experiment, proc):
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        submitted_experiment.append_to_output(line)
        send_output_to_master(submitted_experiment.run_id, line)


def send_output_to_master(run_id, line):
    data = {'run_id': run_id, 'line': line}
    requests.post(build_url(MASTER_URL, ['worker-manager', 'output'], 'POST'), data=data)


def send_completion_information_to_master(submitted_experiment):
    final_object = serializers.serialize('json', [submitted_experiment])
    data = {'submitted_experiment': final_object, 'complete': True}
    requests.post(build_url(MASTER_URL, ['worker-manager', 'output'], 'POST'), data=data)
