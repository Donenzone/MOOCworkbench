from ExperimentsManager.models import ChosenExperimentSteps, Experiment
from GitManager.github_helper import add_file_to_repository
from django.template.defaultfilters import slugify

def init_repo_boilerplate(experiment):
    create_readme_file(experiment)
    create_step_folders(experiment)
    create_requirements_file(experiment)
    create_data_folder(experiment)

def create_requirements_file(experiment):
    create_new_file_in_repo(experiment, 'requirements.txt', 'Added requirements file')

def create_step_folders(experiment):
    chosen_experiment_steps = ChosenExperimentSteps.objects.filter(experiment=experiment)
    for step in chosen_experiment_steps:
        name = slugify(step.step.step_name)
        commit_message = 'Create folder {0}'.format(name)
        add_file_to_repository(experiment.owner, experiment.git_repo.name, '__init__.py', commit_message, name)
        create_main_file(experiment, folder=name)

def create_main_file(experiment, folder):
    create_new_file_in_repo(experiment, 'main.py', commit_message='Added main.py file', folder=folder, contents='print("Hello, world!")')

def create_readme_file(experiment):
    create_new_file_in_repo(experiment, 'README.md', 'Added README file', contents='# Welcome to your experiment')

def create_data_folder(experiment):
    create_new_file_in_repo(experiment, '__init__.py', 'Added data folder', 'data')

def create_new_file_in_repo(experiment, file_name, commit_message, folder='', contents=''):
    add_file_to_repository(experiment.owner, experiment.git_repo.name, file_name, commit_message, contents=contents, folder=folder)
