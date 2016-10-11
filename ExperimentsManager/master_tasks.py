from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExperimentRun
from celery import task
from .serializer import serializer_experiment_run_factory
from rest_framework.renderers import JSONRenderer
from helpers.url_helper import build_url
import requests
from MOOCworkbench.settings import MASTER_URL


@receiver(post_save, sender=ExperimentRun)
def start_experiment_run(sender, instance, **kwargs):
    if instance.status is ExperimentRun.CANCELLED:
        send_updated_model_to_master.delay(instance)


@task
def send_updated_model_to_master(instance):
    serializer = serializer_experiment_run_factory(ExperimentRun)(instance)
    json = JSONRenderer().render(serializer.data)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    requests.post(build_url(MASTER_URL, ['api', 'worker', 'experiment-run', instance.pk], 'POST'), data=json, headers=headers)