import json

from channels import Group
from channels.auth import channel_session_user_from_http


@channel_session_user_from_http
def ws_connect(message):
    user = message.user.username
    Group(user).add(message.reply_channel)
    Group(user).send({'text': json.dumps({'connected': True})})


def send_message_to_group(user, message):
    Group(user).send({
        "text": json.dumps(message)
    })


def send_message(user, priority, contents):
    send_message_to_group(user, {'priority': priority, 'contents': contents})


def send_exp_package_creation_status_update(user, progress_nr, completed=False, redirect_url=None, error=None):
    message_dict = {}
    message_dict['completed'] = completed
    message_dict['progress_nr'] = progress_nr
    if redirect_url:
        message_dict['redirect_url'] = redirect_url
    if error:
        message_dict['error'] = error
    send_message_to_group(user, message_dict)
