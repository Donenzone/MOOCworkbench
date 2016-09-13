from __future__ import absolute_import
from celery import task


@task
def start_code_run(path_to_repo):
    print("About to start execution of script")
    print("Setting up code execution environment")
    # Make sure the output folder exists and is clean
    # Start script in own thread
    # Monitor execution of the script, and kill of required
    print(path_to_repo)
