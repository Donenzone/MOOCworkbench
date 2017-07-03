import logging

from helpers.helper import get_absolute_path

from ..models import GitRepository
from .github_helper import GitHubHelper


logger = logging.getLogger(__name__)


def get_exp_or_package_from_repo_name(repo_name):
    """Helper function to retrieve experiment or InternalPackage DB object based on repository name
    Useful for tasks that do not have a session or other information"""
    git_repo = GitRepository.objects.filter(name=repo_name)
    if git_repo:
        git_repo = git_repo[0]
        if git_repo.experiment_set:
            experiment = git_repo.experiment_set.first()
            return experiment
        elif git_repo.internalpackage_set:
            package = git_repo.internalpackage_set.first()
            return package


def create_new_github_repository(title, user):
    """Creates a new GitHub repository with title for user
    :param title: Title of new GitHub repository
    :param user: User or WorkbenchUser object for whom to create repository
    :return: initialized GitHubHelper and True if succeeded, else returns existing repository"""
    try:
        github_helper = GitHubHelper(user, title, create=True)
        return github_helper, True
    except Exception as e:
        logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', user,
                     title, e)
        return _get_existing_repository(title, user)


def _get_existing_repository(title, user):
    """Gets an existing repository, if it exists
    :param title: Title of GitHub repository to check for existence
    :param user: User or WorkbenchUser object for which to create repository
    :return: Return GitHubHelper if repo exists, with False because this function is called from Create,
    if no repo exists, return None, False"""
    try:
        github_helper = GitHubHelper(user, title)
        return github_helper, False
    except Exception as e:
        logger.error('GitHubHelper could not be initialized for %s (%s) with error: %s', user,
                     title, e)
        return None, False

