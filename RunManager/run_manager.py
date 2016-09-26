from __future__ import absolute_import
from celery import task
from subprocess import Popen, PIPE, STDOUT

dockerfile_str = '''
FROM python:3
COPY RunManager/gitrepositories/{CURRENT_REPO} /repo
WORKDIR /repo
RUN pip install -r requirements.txt
'''


def setup_docker_image(repo_name):
    print("Setting up Docker environment")
    create_docker_file(repo_name)
    p = Popen(['docker', 'build', '.', '--tag', 'moocworkbench/mooc'],
              stdout=PIPE)
    return iter(p.stdout.readline())


def start_code_run():
    print("Starting code execution")
    p_run = Popen(['docker', 'run', 'moocworkbench/mooc', 'python', 'main.py'],
              stdout=PIPE)
    return iter(p_run.stdout.readline())


def create_docker_file(repo_name):
    dockerfile = dockerfile_str.replace('{CURRENT_REPO}', repo_name)
    with open('Dockerfile', 'w+') as f:
        f.write(dockerfile)
