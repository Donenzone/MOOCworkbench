from RequirementsManager.mixins import RequirementWhatNowMixin
from BuildManager.mixins import BuildWhatNowMixin

class WhatNow(BuildWhatNowMixin, RequirementWhatNowMixin):
    def __init__(self, experiment):
        self.messages = []
        self.experiment = experiment

    def what_to_do_now(self):
        message_list = []
        message_list.append(self.what_to_do_now_ci())
        message_list.append(self.what_to_do_now_req())
        vcs_message = "Make sure to commit and push daily and in small pieces"
        message_list.append(vcs_message)
        return message_list
