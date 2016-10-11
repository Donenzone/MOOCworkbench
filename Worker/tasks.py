from __future__ import absolute_import
from celery.decorators import periodic_task
from datetime import timedelta
from MOOCworkbench.settings import MASTER_URL, WORKER_URL
import requests
from celery.signals import celeryd_init
from helpers.url_helper import build_url
from helpers.ssh_helper import generate_ssh_private_public_key_pair
from RunManager.run_manager import setup_docker_image, start_code_run
from helpers.dir_helpers import *
from git import Repo
from django.core import serializers
from WorkerHelper.serializer import serializer_factory
from .models import Worker
import string, random
from rest_framework.renderers import JSONRenderer



@periodic_task(run_every=timedelta(seconds=30), queue="default")
def report_status_to_master():
    existing_worker = Worker.objects.first()
    update_worker_information(existing_worker)


@celeryd_init.connect()
def configure_worker(conf=None, **kwargs):
    ssh_pub_key = generate_ssh_private_public_key_pair()

    existing_worker = Worker.objects.all()
    if existing_worker.count() is not 0:
        existing_worker = existing_worker.first()
        existing_worker.communication_key = ssh_pub_key
        existing_worker.save()

        if update_worker_information(existing_worker) == 404:
            create_new_worker(existing_worker)
    else:

        name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
        worker = Worker(name=name, location=WORKER_URL, status=Worker.AVAILABLE, communication_key=ssh_pub_key)
        worker.save()

        create_new_worker(worker)


def update_worker_information(existing_worker):
    serializer = serializer_factory(Worker)(existing_worker)
    json = JSONRenderer().render(serializer.data)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.put(build_url(MASTER_URL, ['api', 'workers', existing_worker.name], 'POST'), data=json, headers=headers)
    return r.status_code


def create_new_worker(worker):
    serializer = serializer_factory(Worker)(worker)
    json = JSONRenderer().render(serializer.data)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    requests.post(build_url(MASTER_URL, ['api', 'workers'], 'POST'), data=json, headers=headers)
