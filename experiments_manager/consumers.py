import json

from channels.auth import channel_session_user_from_http
from channels import Group


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