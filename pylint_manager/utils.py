import virtualenv
import os
import subprocess
import json
import shutil

from django.db.models import Q

from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper

from .models import PylintScan, PylintResult, PylintScanResult


def run_pylint(experiment):
    # clone git repository
    active_step = experiment.get_active_step()
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    git_helper = GitHelper(github_helper)
    git_helper.clone_or_pull_repository()

    # virtualenv create
    repo_dir = git_helper.repo_dir
    venv_dir = os.path.join(repo_dir, ".venv")
    virtualenv.create_environment(venv_dir)

    # install requirements
    requirements_location = '{0}/requirements.txt'.format(repo_dir)
    active_this = '{0}/.venv/bin/activate_this.py'.format(repo_dir)
    subprocess.call(['python3', active_this])
    subprocess.call(['pip3', 'install', '-r', requirements_location])

    # find python files in src/ folders
    step_folder = '{0}{1}'.format(repo_dir, active_step.location)
    python_file_list = find_python_files_in_dir(step_folder)

    # run pylint on files
    pylint_results = []
    for python_file in python_file_list:
        p = subprocess.run(['pylint', '--output-format=json', python_file],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        pylint_results.append(p.stdout.decode('utf-8'))

    pylint_scan_result_object = PylintScanResult()
    pylint_scan_result_object.for_project = experiment.pylint
    pylint_scan_result_object.save()

    parse_pylint_results(pylint_results, pylint_scan_result_object)

    results_errors = PylintResult.objects.filter(for_result=pylint_scan_result_object, pylint_type='e').count()
    pylint_scan_result_object.nr_of_errors = results_errors
    results_warnings = PylintResult.objects.filter(for_result=pylint_scan_result_object, pylint_type='w').count()
    pylint_scan_result_object.nr_of_warnings = results_warnings
    results_other_issues = PylintResult.objects.filter(~Q(pylint_type='e'), ~Q(pylint_type='w'),
                                            for_result=pylint_scan_result_object).count()
    pylint_scan_result_object.nr_of_other_issues = results_other_issues
    pylint_scan_result_object.save()


def find_python_files_in_dir(dir_to_scan):
    python_list = []
    for file in os.listdir(dir_to_scan):
        if file.endswith(".py"):
            python_list.append(os.path.join(dir_to_scan, file))
    return python_list


def parse_pylint_results(pylint_results, pylint_scan_result_object):
    if pylint_results:
        json_pylint = json.loads(pylint_results[0])
        for pylint in json_pylint:
            result = PylintResult()
            result.for_result = pylint_scan_result_object
            result.pylint_type = pylint['type'][0]
            result.message = pylint['message']
            result.line_nr = pylint['line']
            result.file_path = pylint['path']
            result.save()