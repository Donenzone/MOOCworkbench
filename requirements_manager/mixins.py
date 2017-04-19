from requirements_manager.models import Requirement


class RequirementWhatNowMixin(object):

    def what_to_do_now_req(self):
        req_message = "Add some packages you wish to use on the Manage Your Requirements tab"
        reqs_defined = False
        reqs_list = Requirement.objects.filter(experiment=self.experiment)
        if reqs_list:
            reqs_defined = True
        if not reqs_defined:
            return req_message
