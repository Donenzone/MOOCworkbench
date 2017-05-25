import hmac
from hashlib import sha1
import json

import requests
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes

from requirements_manager.tasks import task_update_requirements
from dataschema_manager.tasks import task_read_data_schema
from docs_manager.tasks import task_generate_docs
from quality_manager.tasks import task_complete_quality_check
from git_manager.helpers.helper import get_experiment_from_repo_name

from .helpers.github_helper import GitHubHelper
from .tasks import task_process_git_push


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
    github_helper = GitHubHelper(user, title, create=True)
    return github_helper


# source: https://gist.github.com/vitorfs/145a8b8f0865cb65ee915e0c846fc303
@require_POST
@csrf_exempt
def webhook_receive(request):
    # Verify if request came from GitHub
    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        # Deploy some code for example
        event = json.loads(str(request.body, encoding='utf8'))
        repo_name = event['repository']['name']
        sha_hash_list = []
        if 'commits' in event:
            for commit in event['commits']:
                sha_hash_list.append(commit['id'])
            run_post_push_tasks(repo_name, sha_hash_list)
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)


def run_post_push_tasks(repository_name, sha_list):
    experiment = get_experiment_from_repo_name(repository_name)
    task_update_requirements.delay(repository_name)
    task_read_data_schema.delay(repository_name)
    task_process_git_push.delay(repository_name, sha_list)
    active_step = experiment.get_active_step()
    task_generate_docs.delay(experiment.get_object_type(), experiment.pk)
    if active_step:
        task_complete_quality_check.delay(active_step.id)

