from __future__ import absolute_import
import os
from celery import Celery
from MOOCworkbench.settings import MASTER_OR_WORKER, WORKER
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOCworkbench.settings')
from kombu import Queue, Exchange

CELERY_ROUTES = {'Worker.tasks.check_for_disconnected_workers': {'queue': 'master'}}

app = Celery('MOOCworkbench', broker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings')
app.conf.update(CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',)
#app.select_queues()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
