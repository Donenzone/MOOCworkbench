from django.apps import AppConfig
from celery import current_app
from celery.bin import worker


class WorkerConfig(AppConfig):
    name = 'Worker'
    verbose_name = "Worker"
    app = current_app._get_current_object()
    worker = worker.worker(app=app)

    def ready(self):
        options = {
            'broker': 'redis://localhost:6379/0',
            'loglevel': 'INFO',
            'traceback': True,
        }

        self.worker.run(**options)