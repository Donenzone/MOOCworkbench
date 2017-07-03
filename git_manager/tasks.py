import logging
from datetime import datetime

import pytz

from dataschema_manager.tasks import task_read_data_schema
from docs_manager.tasks import task_generate_docs
from experiments_manager.models import Experiment
from marketplace.models import InternalPackage
from MOOCworkbench.celery import app
from quality_manager.tasks import task_complete_quality_check
from requirements_manager.tasks import task_update_requirements

from .helpers.github_helper import GitHubHelper
from .helpers.helper import get_exp_or_package_from_repo_name
from .models import Commit

logger = logging.getLogger(__name__)


@app.task
def task_process_git_push(repository_name, sha_list):
    """Processes a Git push and expects the repository name and a list of SHA hashes of the commit(s)
    If the git push belongs to an experiment, run all the connected tasks sequentially. Swallow any errors
    to ensure that if one task fails, other tasks can still be executed.
    In case of a package, only update the docs and requirements list in the workbench."""
    exp_or_package = get_exp_or_package_from_repo_name(repository_name)
    logger.debug('received and processing git commit for %s', exp_or_package)
    if isinstance(exp_or_package, Experiment):
        try:
            task_update_requirements(repository_name)
        except Exception as e:
            logger.error("task updating requirements failed for %s with %s", exp_or_package, e)
        try:
            task_read_data_schema(repository_name)
        except Exception as e:
            logger.error("task updating schema failed for %s with %s", exp_or_package, e)
        try:
            task_process_commit(repository_name, sha_list)
        except Exception as e:
            logger.error("task processing git push failed for %s with %s", exp_or_package, e)
        try:
            task_generate_docs(exp_or_package.get_object_type(), exp_or_package.pk)
        except Exception as e:
            logger.error("task generating docs failed for %s with %s", exp_or_package, e)
        try:
            active_step = exp_or_package.get_active_step()
            if active_step:
                task_complete_quality_check(active_step.id)
        except Exception as e:
            logger.error("task complete quality check failed for %s with %s", exp_or_package, e)
    elif isinstance(exp_or_package, InternalPackage):
        task_generate_docs.delay(exp_or_package.get_object_type(), exp_or_package.pk)
        task_update_requirements.delay(repository_name)


@app.task
def task_process_commit(repository_name, sha_hash_list):
    """Processes a list of git commits (sha hashes) for repository (repository_name),
    and creates for each git commit a Commit DB object with the associated information
    :param repository_name: Repository name of GitHub repo for which to process commits
    :param sha_hash_list: A list of SHA hashes of the commits to process"""
    experiment = get_exp_or_package_from_repo_name(repository_name)
    git_repo = experiment.git_repo
    github_helper = GitHubHelper(experiment.owner, repository_name)
    for sha_hash in sha_hash_list:
        existing = Commit.objects.filter(sha_hash=sha_hash)
        if not existing:
            commit = github_helper.get_commit(sha_hash)
            commit_obj = Commit()
            commit_obj.sha_hash = sha_hash
            commit_obj.commit_message = commit.commit._message.value
            timestamp = datetime.strptime(commit.last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            pytz.timezone('GMT').localize(timestamp)
            commit_obj.timestamp = timestamp
            commit_obj.additions = commit.stats.additions
            commit_obj.deletions = commit.stats.deletions
            commit_obj.total = commit.stats.total
            commit_obj.save()
            git_repo.commits.add(commit_obj)
            git_repo.save()
