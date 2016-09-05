from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOCworkbench.settings')
from django.conf import settings

app = Celery('MOOCworkbench', broker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings')
app.conf.update(CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
