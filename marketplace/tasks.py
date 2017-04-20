from celery.decorators import periodic_task
from datetime import timedelta
from marketplace.models import update_all_versions
from MOOCworkbench.celery import app


@periodic_task(run_every=timedelta(hours=24))
def check_for_new_package_version():
    update_all_versions()

