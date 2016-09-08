from __future__ import absolute_import
from celery import task
from celery.decorators import periodic_task
from datetime import timedelta
from MOOCworkbench.settings import MASTER_URL, MASTER_URL
import requests
from .views import *
from celery.signals import celeryd_init
from helpers.url_helper import build_url
from helpers.ssh_helper import generate_ssh_private_public_key_pair

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
