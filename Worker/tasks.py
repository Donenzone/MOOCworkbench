from __future__ import absolute_import
from celery import task
from MOOCworkbench.settings import MASTER_URL
import requests
from .views import *
from celery.signals import celeryd_init
from helpers import url_helper

@task(ignore_result=True)
def report_status_to_master():
    status = get_current_status()
    r = requests.post(MASTER_URL, data={'status': status})

@celeryd_init.connect()
def configure_worker(conf=None, **kwargs):
    requests.post(url_helper.build_url(MASTER_URL, ['worker', 'registration'], 'POST'), data={'new': True})
