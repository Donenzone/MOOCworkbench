from __future__ import absolute_import
from celery import task
from shutil import copyfile
import fileinput
from docker import Client
from io import BytesIO

dockerfile_str = '''
FROM python:3
COPY home/jochem/Development/MOOCworkbench/RunManager/gitrepositories/{CURRENT_REPO} /repo
WORKDIR /repo
RUN pip install -r requirements.txt
'''

@task
def start_code_run(path_to_repo, repo_name):
    print("About to start execution of script")
    print("Setting up Docker environment")
    dockerfile = BytesIO(create_docker_file(repo_name).encode('utf-8'))
    cli = Client(base_url='unix://var/run/docker.sock')
    response = [line for line in cli.build(fileobj=dockerfile, rm=True,  tag='moocworkbench/volume')]
    for line in response:
        print(line)
    print(path_to_repo)


def create_docker_file(repo_name):
    return dockerfile_str.replace('{CURRENT_REPO}', repo_name)

start_code_run('/gitrepositories/my-first-repo', 'my-first-repo')