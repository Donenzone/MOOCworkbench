from MOOCworkbench.settings import DEBUG

from git_manager.views import create_new_github_repository
from git_manager.helpers.git_helper import GitHelper
from cookiecutter_manager.helpers.helper_cookiecutter import clone_cookiecutter_template

from .models import Experiment
from .models import ChosenExperimentSteps


def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment


def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')


def init_git_repo_for_experiment(experiment, cookiecutter):
    git_repo, github_helper = create_new_github_repository(experiment.title, experiment.owner.user)

    experiment.git_repo = git_repo
    experiment.save()

    git_helper = GitHelper(github_helper)
    git_helper.clone_repository()

    repo_dir = git_helper.repo_dir_of_user()
    repo_name = github_helper.repo_name

    clone_cookiecutter_template(cookiecutter, repo_dir, repo_name, experiment.owner, experiment.description)

    git_helper.commit('Cookiecutter template added')
    git_helper.push()




