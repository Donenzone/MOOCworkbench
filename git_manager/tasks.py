from datetime import datetime
import pytz

from MOOCworkbench.celery import app

from .helpers.helper import get_experiment_from_repo_name
from .helpers.github_helper import GitHubHelper
from .models import Commit


@app.task
def task_process_git_push(repository_name, sha_hash_list):
    experiment = get_experiment_from_repo_name(repository_name)
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
