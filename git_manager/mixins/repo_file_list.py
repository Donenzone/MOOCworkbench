from django.template.defaultfilters import slugify

from pylint_manager.helper import return_result_summary_for_file

from git_manager.helpers.github_helper import GitHubHelper
from experiments_manager.models import Experiment


class ContentFile(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path


def get_files_for_steps(experiment, only_active=False):
    steps = []
    for step in experiment.chosenexperimentsteps_set.all():
        if not only_active or only_active and step.active:
            location = step.location
            if _is_folder(location):
                files = _get_files_in_repository(experiment.owner.user, experiment.git_repo.name, location)
            else:
                files = [ContentFile(name=location, path=location)]
            step.files = files
        steps.append(step)
    return steps


def get_files_for_repository(exp_or_package):
        location = _folder_location(exp_or_package)

        if _is_folder(location):
            return _files_in_folder(location, exp_or_package)
        else:
            return _single_file(location, exp_or_package)


def _files_in_folder(location, exp_or_package):
    content_files = _get_files_in_repository(exp_or_package.owner, exp_or_package.git_repo.name, location)
    if isinstance(exp_or_package, Experiment):
        files = _add_static_results_to_files(exp_or_package, content_files)
    else:
        files = content_files
    return files


def _folder_location(exp_or_package):
    if isinstance(exp_or_package, Experiment):
        return exp_or_package.get_active_step().location
    return '/'


def _single_file(location, context, exp_or_package):
    git_file = ContentFile(name=location, path=location)
    git_file.pylint_results = return_result_summary_for_file(exp_or_package,
                                                             git_file.path)
    return [git_file]


def _add_static_results_to_files(experiment, content_files):
    for git_file in content_files:
        git_file.pylint_results = return_result_summary_for_file(experiment,
                                                                 git_file.path)
        git_file.slug = slugify(git_file.name)
    return content_files


def _get_files_in_repository(owner, repo_name, folder_name):
    github_helper = GitHubHelper(owner, repo_name)
    return github_helper.list_files_in_folder(folder_name)


def _is_folder(location):
    return not '.' in location
