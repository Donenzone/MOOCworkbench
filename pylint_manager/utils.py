import json
import os
import re
import shutil
import subprocess

from django.db.models import Q
from rpy2.robjects.packages import importr

from git_manager.helpers.git_helper import GitHelper, clean_up_after_git_helper
from git_manager.helpers.github_helper import GitHubHelper
from MOOCworkbench.settings import PROJECT_ROOT

from .models import PylintResult, PylintScan, PylintScanResult


def static_analysis_prepare(experiment):
    # clone git repository
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    git_helper = GitHelper(github_helper)
    git_helper.clone_or_pull_repository()
    return git_helper


def run_rlint(experiment):
    git_helper = static_analysis_prepare(experiment)
    repo_dir = git_helper.repo_dir
    active_step = experiment.get_active_step()

    old_active_dir = os.getcwd()
    os.chdir(repo_dir + '/src/')
    utils = importr('utils')
    utils.install_packages('lintr', repos='http://cran.us.r-project.org')
    lintr = importr('lintr')
    results = lintr.lint(active_step.main_module)

    pylint_scan_result_object = PylintScanResult()
    pylint_scan_result_object.for_project = experiment.pylint
    pylint_scan_result_object.save()

    for result in str(results).split('\n'):
        pylint_result = parse_rlint_results(result, '/src/make_dataset.R')
        if pylint_result:
            pylint_result.for_result = pylint_scan_result_object
            pylint_result.save()
    clean_up_after_git_helper(git_helper)
    os.chdir(old_active_dir)


def parse_rlint_results(result_line, filename):
    output = re.match(r"^(.*).R:(\d+):(\d+):\s(style|warning|error):(.*)$", result_line)
    if output:
        result = PylintResult()
        result.file_path = filename
        result.line_nr = output.group(2)
        result.pylint_type = output.group(4)[0]
        result.message = output.group(5)
        return result


def run_pylint(experiment):
    git_helper = static_analysis_prepare(experiment)
    active_step = experiment.get_active_step()
    repo_dir = git_helper.repo_dir

    step_folder_relative = make_relative_path(active_step.location)
    step_folder = os.path.join(repo_dir, step_folder_relative)
    subprocess.call(['./shell_scripts/run_pylint.sh', repo_dir, step_folder_relative], cwd=PROJECT_ROOT)

    with open(os.path.join(step_folder, 'pylint_results.json'), 'r') as pylint_file:
        pylint_results = pylint_file.read()
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

    clean_up_after_git_helper(git_helper)


def make_relative_path(location):
    if location.startswith('/'):
        return location[1:]
    return location


def parse_pylint_results(pylint_results, pylint_scan_result_object):
    print(pylint_results)
    json_pylint = json.loads(pylint_results)
    for pylint in json_pylint:
        result = PylintResult()
        result.for_result = pylint_scan_result_object
        result.pylint_type = pylint['type'][0]
        result.message = pylint['message']
        result.line_nr = pylint['line']
        result.file_path = pylint['path']
        result.save()
