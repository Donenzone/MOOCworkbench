from __future__ import absolute_import
from celery import task

@task
def get_status_of_task(x, y):
    return x + y
