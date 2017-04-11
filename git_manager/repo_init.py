from experiments_manager.models import ChosenExperimentSteps, Experiment
from git_manager.github_helper import GitHubHelper
from django.template.defaultfilters import slugify
import os

class GitRepoInit(object):
    TEMPLATE_FOLDER = 'codetemplates/'
    PROJECTNAME_VAR = 'PROJECTNAME'
    STEPFOLDER_VAR = 'STEPFOLDER'
    AUTHOR_VAR = 'AUTHOR'

    def __init__(self, experiment, type='python'):
        self.github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
        self.experiment = experiment
        self.template_type_folder = '{0}{1}/'.format(self.TEMPLATE_FOLDER, type)

    def init_repo_boilerplate(self):
        self.create_readme_file()
        self.create_requirements_and_init_file()
        self.create_travis_file()
        self.create_settings_file()
        self.create_test_runner_file()
        self.create_data_folder()
        self.create_step_folders()

    def create_requirements_and_init_file(self):
        self.create_new_file_in_repo('requirements.txt', 'Added requirements file')
        self.create_new_file_in_repo('__init__.py', 'Added init file')

    def create_step_folders(self):
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=self.experiment)
        for step in chosen_experiment_steps:
            name = step.folder_name()
            commit_message = 'Create folder {0}'.format(name)
            self.github_helper.add_file_to_repository('__init__.py', commit_message, name)
            self.create_main_and_test_file(name)

    def create_main_and_test_file(self, folder):
        main_contents = self.get_file_contents('main.py', part_of_step=True, folder=folder)
        project_name = self.github_helper.github_repository.name
        main_contents = self.replace_variable_in_file(main_contents, self.PROJECTNAME_VAR, project_name)
        main_contents = self.replace_variable_in_file(main_contents, self.STEPFOLDER_VAR, folder)
        main_contents = self.replace_variable_in_file(main_contents, self.AUTHOR_VAR, str(self.experiment.owner))
        self.create_new_file_in_repo('main.py', commit_message='Added main.py file', folder=folder, contents=main_contents)
        self.create_new_file_in_repo('tests.py', commit_message='Added test.py file', folder=folder, contents=self.get_file_contents('tests.py', part_of_step=True, folder=folder))

    def create_travis_file(self):
        self.create_new_file_in_repo('.travis.yml', 'Added Travis CI config', contents=self.get_file_contents('.travis.yml'))

    def create_settings_file(self):
        self.create_new_file_in_repo('settings.py', 'Added settings.py', contents=self.get_file_contents('settings.py'))

    def create_test_runner_file(self):
        self.create_new_file_in_repo('test_runner.py', 'Added test_runner.py', contents=self.get_file_contents('test_runner.py'))

    def create_readme_file(self):
        self.create_new_file_in_repo('README.md', 'Added README file', contents=self.get_file_contents('README.md'))

    def create_data_folder(self):
        self.create_new_file_in_repo('__init__.py', 'Added data folder', 'data')

    def create_new_file_in_repo(self, file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)

    def get_file_contents(self, filename, part_of_step=False, folder=None):
        if part_of_step:
            path = '{0}{1}steps/{2}'.format(self.get_script_path(), self.template_type_folder, filename)
        else:
            path = '{0}{1}{2}'.format(self.get_script_path(), self.template_type_folder, filename)
        file_to_open = open(path,'r')

        contents = file_to_open.read()
        if folder:
            contents = self.replace_folder_in_file(contents, folder)
        return contents

    def replace_folder_in_file(self, contents, folder):
        return contents.replace('{0}', folder)

    def replace_variable_in_file(self, contents, variable, value):
        variable_name = '{{{0}}}'.format(variable)
        print(variable_name)
        return contents.replace(variable_name, value)

    def get_script_path(self):
        return '{0}/'.format(os.path.dirname(os.path.realpath(__file__)))
