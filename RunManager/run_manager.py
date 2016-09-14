from __future__ import absolute_import
from celery import task
from shutil import copyfile
import fileinput
from docker import Client
from io import BytesIO
import os
from subprocess import Popen, PIPE

dockerfile_str = '''
FROM python:3
COPY gitrepositories/{CURRENT_REPO} /repo
WORKDIR /repo
RUN pip install -r requirements.txt
'''

@task
def setup_docker_image(path_to_repo, repo_name):
    print("Setting up Docker environment")
    create_docker_file(repo_name)
    p = Popen(['docker', 'build', '-t', 'moocworkbench', '.', '--tag', 'moocworkbench/mooc'],
              stdout=PIPE)
    print(p.stdout.read().decode('utf-8'))


def start_code_run():
    print("Starting code execution")
    p_run = Popen(['docker', 'run', 'moocworkbench/mooc', 'python', 'main.py'],
              stdout=PIPE)
    print(p_run.stdout.read().decode('utf-8'))


def create_docker_file(repo_name):
    dockerfile = dockerfile_str.replace('{CURRENT_REPO}', repo_name)
    with open('Dockerfile', 'w+') as f:
        f.write(dockerfile)
