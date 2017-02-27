from __future__ import absolute_import
from celery import task
from celery.decorators import periodic_task
from datetime import timedelta, datetime
from .models import Worker


@periodic_task(run_every=timedelta(seconds=120))
def check_for_disconnected_workers():
    two_minutes_ago = datetime.now() - timedelta(seconds=120)
    unknown_workers = Worker.objects.filter(last_ping___lte=two_minutes_ago)

    for worker in unknown_workers:
        worker.status = Worker.UNKNOWN
        worker.save()