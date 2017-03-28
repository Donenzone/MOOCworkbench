from ExperimentsManager.models import ChosenExperimentSteps, Experiment
from GitManager.github_helper import GitHubHelper
from django.template.defaultfilters import slugify

class GitRepoInit(object):
    def __init__(self, experiment):
        self.github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
        self.experiment = experiment

    def init_repo_boilerplate():
        self.create_readme_file()
        self.create_step_folders()
        self.create_requirements_file()
        self.create_data_folder()

    def create_requirements_file():
        self.create_new_file_in_repo('requirements.txt', 'Added requirements file')

    def create_step_folders():
        chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=experiment)
        for step in chosen_experiment_steps:
            name = slugify(step.step.step_name)
            commit_message = 'Create folder {0}'.format(name)
            self.github_helper.add_file_to_repository('__init__.py', commit_message, name)
            self.create_main_file(name)

    def create_main_file(folder):
        self.create_new_file_in_repo('main.py', commit_message='Added main.py file', folder=folder, contents='print("Hello, world!")')

    def create_readme_file():
        self.create_new_file_in_repo('README.md', 'Added README file', contents='# Welcome to your experiment')

    def create_data_folder():
        self.create_new_file_in_repo('__init__.py', 'Added data folder', 'data')

    def create_new_file_in_repo(file_name, commit_message, folder='', contents=''):
        self.github_helper.add_file_to_repository(file_name, commit_message, contents=contents, folder=folder)
