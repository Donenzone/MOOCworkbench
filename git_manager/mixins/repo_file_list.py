from django.template.defaultfilters import slugify

from experiments_manager.models import Experiment
from pylint_manager.helper import return_result_summary_for_file


class ContentFile(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path


def get_files_for_steps(experiment, github_helper, only_active=False):
    """Get all the files per experiment step
    For each step, the folder is retrieved and the files in that folder are returned
    and attached as an attribute to that step
    :param experiment: The experiment for which to get the files
    :param github_helper: GitHub helper object for the experiment
    :param only_active: Boolean indicates if files should only be retrieved for the active step, or for all steps"""
    steps = []
    for step in experiment.chosenexperimentsteps_set.all():
        if not only_active or only_active and step.active:
            location = step.location
            if _is_folder(location):
                files = _get_files_in_repository(github_helper, location,
                                                 _add_static_results_to_files, experiment)
            else:
                files = [ContentFile(name=location, path=location)]
            step.files = files
        steps.append(step)
    return steps


def get_files_for_repository(github_helper, exp_or_package):
    """Get all the files for an experiment or package"""
    location = _folder_location(exp_or_package)
    if _is_folder(location):
        return _files_in_folder(github_helper, exp_or_package, location)
    else:
        return _single_file(location, exp_or_package)


def _files_in_folder(github_helper, exp_or_package, location):
    """Retrieve the files in a folder for an experiment or package
    :param location: The path for which to get the files
    :param exp_or_package: Experiment or package in which to find the files"""
    if isinstance(exp_or_package, Experiment):
        files = _get_files_in_repository(github_helper, location,
                                         _add_static_results_to_files, exp_or_package)
    else:
        files = _get_files_in_repository(github_helper, location,
                                         _add_github_url_to_files, github_helper)
    return files


def _folder_location(exp_or_package):
    """Get the folder location for an experiment or package
    For an experiment, get the active step location, else return the base path
    """
    if isinstance(exp_or_package, Experiment):
        return exp_or_package.get_active_step().location
    return '/'


def _single_file(location, exp_or_package):
    git_file = ContentFile(name=location, path=location)
    git_file.pylint_results = return_result_summary_for_file(exp_or_package,
                                                             git_file.path)
    return [git_file]


def _add_static_results_to_files(content_files, experiment):
    for git_file in content_files:
        git_file.pylint_results = return_result_summary_for_file(experiment,
                                                                 git_file.path)
        git_file.slug = slugify(git_file.name)
    return content_files


def _add_github_url_to_files(content_files, github_helper):
    for git_file in content_files:
        git_file.github_url = 'https://github.com/{0}/{1}/blob/master/{2}'.format(github_helper.owner,
                                                                                  github_helper.repo_name,
                                                                                  git_file.name)
    return content_files


def _get_files_in_repository(github_helper, folder_name, static_file_func=None, exp_or_package=None):
    return github_helper.list_files_in_folder(folder_name, static_file_func, exp_or_package)


def _is_folder(location):
    return not '.' in location
