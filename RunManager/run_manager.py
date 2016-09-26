from __future__ import absolute_import
from celery import task
from subprocess import Popen, PIPE, STDOUT
from Worker.tasks import *

dockerfile_str = '''
FROM python:3
COPY gitrepositories/{CURRENT_REPO} /repo
WORKDIR /repo
RUN pip install -r requirements.txt
'''


@task
def start_code_execution(submitted_experiment):
    setup_docker_image(submitted_experiment.repo_name)
    start_code_run()


def setup_docker_image(repo_name):
    print("Setting up Docker environment")
    create_docker_file(repo_name)
    p = Popen(['docker', 'build', '-t', 'moocworkbench', '.', '--tag', 'moocworkbench/mooc'],
              stdout=PIPE)
    print(p.stdout.read().decode('utf-8'))


def start_code_run(submitted_experiment):
    print("Starting code execution")
    p_run = Popen(['docker', 'run', 'moocworkbench/mooc', 'python', 'main.py'],
              stdout=PIPE)
    return_docker_output(submitted_experiment, iter(p_run.stdout.readline.decode('utf-8')))


def return_docker_output(submitted_experiment, iterator):
    for line in iterator:
        submitted_experiment.append_to_output(line)
        send_output_to_master(submitted_experiment.run_id, line)


def create_docker_file(repo_name):
    dockerfile = dockerfile_str.replace('{CURRENT_REPO}', repo_name)
    with open('Dockerfile', 'w+') as f:
        f.write(dockerfile)
