import virtualenv
import os
import subprocess
import json

from quality_manager.measurements.measurement import MeasurementAbstraction
from quality_manager.models import RawMeasureResult, ExperimentMeasure
from quality_manager.models import ExperimentMeasureResult
from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper


class PyLintMeasurement(MeasurementAbstraction):
    def __init__(self, experiment_step):
        super().__init__(experiment_step)
        self.measurement = ExperimentMeasure.objects.get(name='Pylint static code analysis')
        self.raw_value_list =[]

    def measure(self):
        # clone git repository
        github_helper = GitHubHelper(self.experiment.owner, self.experiment.git_repo.name)
        git_helper = GitHelper(github_helper)
        git_helper.clone_repository()

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
        step_folder = '{0}{1}'.format(repo_dir, self.experiment_step.location)
        python_file_list = self.find_python_files_in_dir(step_folder)

        # run pylint on files
        pylint_results = []
        for python_file in python_file_list:
            p = subprocess.run(['pylint', '--output-format=json', python_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            pylint_results.append(p.stdout.decode('utf-8'))

        # parse pylint results
        self.raw_value_list = self.parse_pylint_results(pylint_results[0])
        self.result.result = ExperimentMeasureResult.HIGH

    def find_python_files_in_dir(self, dir_to_scan):
        python_list = []
        for file in os.listdir(dir_to_scan):
            if file.endswith(".py"):
                python_list.append(os.path.join(dir_to_scan, file))
        return python_list

    def parse_pylint_results(self, pylint_results):
        raw_value_list = []
        json_pylint = json.loads(pylint_results)
        for pylint in json_pylint:
            raw_value = RawMeasureResult(key='output', value=pylint)
            raw_value.save()
            raw_value_list.append(raw_value)
        return raw_value_list

    def save_and_get_result(self):
        self.result.measurement = self.measurement
        self.result.save()
        self.result.raw_values.set(self.raw_value_list)
        self.result.save()
        return self.result
