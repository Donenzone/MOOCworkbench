from django.shortcuts import reverse

from experiments_manager.helper import verify_and_get_experiment

from .models import Requirement


class RequirementWhatNowMixin(object):

    def what_to_do_now_req(self):
        req_message = "Add some packages you wish to use on the Manage Your Requirements tab"
        reqs_defined = False
        reqs_list = Requirement.objects.filter(experiment=self.experiment)
        if reqs_list:
            reqs_defined = True
        if not reqs_defined:
            return req_message


class RequirementSuccessUrlMixin(object):
    def get_success_url(self):
        if self.kwargs['object_type'] == self.EXPERIMENT_TYPE:
            experiment = verify_and_get_experiment(self.request, self.kwargs['object_id'])
            success_url = experiment.success_url_dict('#edit')['dependencies']
        elif self.kwargs['object_type']  == self.PACKAGE_TYPE:
            success_url = reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['object_id']})
        return success_url

