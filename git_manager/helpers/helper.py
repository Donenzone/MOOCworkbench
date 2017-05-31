import logging

from helpers.helper import get_absolute_path

from ..models import GitRepository
from .github_helper import GitHubHelper


logger = logging.getLogger(__name__)



class TemplateHelper(object):
    TEMPLATE_FOLDER = '/codetemplates/'


class CodeTemplateTypes(object):
    PACKAGE_TYPE = 'pip'
    PYTHON_TYPE = 'python'


def get_file_from_code_template(type, file_name, folder=None):
    template_type_folder = '{0}{1}/'.format(TemplateHelper.TEMPLATE_FOLDER, type)
    if folder:
        path = '{0}{1}{2}{3}'.format(get_absolute_path(), template_type_folder, folder, file_name)
    else:
        path = '{0}{1}{2}'.format(get_absolute_path(), template_type_folder, file_name)
    file_to_open = open(path, 'r')
    contents = file_to_open.read()
    file_to_open.close()
    return contents


def get_exp_or_package_from_repo_name(repo_name):
    git_repo = GitRepository.objects.filter(name=repo_name)
    if git_repo:
        git_repo = git_repo[0]
        if git_repo.experiment_set:
            experiment = git_repo.experiment_set.first()
            return experiment
        elif git_repo.internalpackage_set:
            package = git_repo.internalpackage_set.first()
            return package


def get_user_repositories(user):
    github_helper = GitHubHelper(user)
    github_api = github_helper.github_object
    if github_api:
        repo_list = []
        for repo in github_api.get_user().get_repos(type='owner'):
            repo_list.append((repo.name, repo.clone_url))
        return repo_list
    return []


def create_new_github_repository(title, user):
    try:
        github_helper = GitHubHelper(user, title, create=True)
        return github_helper, True
    except Exception as e:
        logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', user,
                     title, e)
        return get_existing_repository(title, user)


def get_existing_repository(title, user):
    try:
        github_helper = GitHubHelper(user, title)
        return github_helper, False
    except Exception as e:
        logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', user,
                     title, e)
        return None, False

