from channels import Group
from json import dumps


class Content:
    def __init__(self, reply_channel):
        self.reply_channel = reply_channel

    def send(self, json):
        Group(self.reply_channel).send({
            'text': dumps(json)
        })

    def get_reply_channel(self):
        return self.reply_channel


def connect_worker_output(message, worker):
    Group('worker').add(message.reply_channel)


def disconnect_worker_output(message, worker):
    Group('worker').discard(message.reply_channel)