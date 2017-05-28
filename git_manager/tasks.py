from datetime import datetime
import pytz
import logging

from MOOCworkbench.celery import app
from requirements_manager.tasks import task_update_requirements
from dataschema_manager.tasks import task_read_data_schema
from docs_manager.tasks import task_generate_docs
from quality_manager.tasks import task_complete_quality_check

from .helpers.helper import get_exp_or_package_from_repo_name
from .helpers.github_helper import GitHubHelper
from .models import Commit


logger = logging.getLogger(__name__)


@app.task
def task_process_git_push(repository_name, sha_list):
    exp_or_package = get_exp_or_package_from_repo_name(repository_name)
    try:
        task_update_requirements(repository_name)
    except Exception as e:
        logger.error("task updating requirements failed for %s with %s", exp_or_package, e)
    try:
        task_read_data_schema(repository_name)
    except Exception as e:
        logger.error("task updating schema failed for %s with %s", exp_or_package, e)
    try:
        task_process_git_push(repository_name, sha_list)
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



@app.task
def task_process_commit(repository_name, sha_hash_list):
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
