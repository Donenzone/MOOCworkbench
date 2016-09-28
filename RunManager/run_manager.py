from __future__ import absolute_import
from subprocess import Popen, PIPE, STDOUT
import io

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
    return p


def start_code_run():
    print("Starting code execution")
    p_run = Popen(['docker', 'run', 'moocworkbench/mooc', 'python', 'main.py'],
              stdout=PIPE)
    return p_run


def create_docker_file(repo_name):
    dockerfile = dockerfile_str.replace('{CURRENT_REPO}', repo_name)
    with open('Dockerfile', 'w+') as f:
        f.write(dockerfile)
