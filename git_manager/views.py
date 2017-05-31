import hmac
import json
import logging
from hashlib import sha1
from ipaddress import ip_address, ip_network

import requests
from django.conf import settings
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseServerError)
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from helpers.constants import WORKBENCH_COMMIT_MESSAGES

from .helpers.github_helper import GitHubHelper
from .tasks import task_process_git_push

logger = logging.getLogger(__name__)

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
            commit_message = event['head_commit']['message']
            if commit_message not in WORKBENCH_COMMIT_MESSAGES:
                for commit in event['commits']:
                    sha_hash_list.append(commit['id'])
                run_post_push_tasks(repo_name, sha_hash_list)
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)


def run_post_push_tasks(repository_name, sha_list):
    task_process_git_push.delay(repository_name, sha_list)
