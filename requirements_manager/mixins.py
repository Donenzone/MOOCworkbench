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


class RequirementTypeMixin(object):
    EXPERIMENT_TYPE = 'experiment'
    PACKAGE_TYPE = 'package'
    requirement_types = {'Experiment': EXPERIMENT_TYPE, 'InternalPackage': PACKAGE_TYPE}

    def get_requirement_type(self, django_object):
        return self.requirement_types[django_object.__class__.__name__]
