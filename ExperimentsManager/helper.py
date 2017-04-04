from ExperimentsManager.models import Experiment
from ExperimentsManager.models import ChosenExperimentSteps
from BuildManager.models import TravisInstance
from RequirementsManager.models import ExperimentRequirement


def verify_and_get_experiment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    return experiment


def what_to_do_now(experiment):
    message_list = []

    message_list.append(what_to_do_now_ci(experiment))
    message_list.append(what_to_do_now_req(experiment))
    vcs_message = "Make sure to commit and push daily and in small pieces"
    message_list.append(vcs_message)
    return message_list


def what_to_do_now_ci(experiment):
    ci_message = "Enable Travis Builds on the Continuous Integration tab"
    ci_enabled = False
    ci_enabled_check = TravisInstance.objects.filter(experiment=experiment)
    if ci_enabled_check.count() is not 0:
        ci_enabled = ci_enabled_check[0].enabled
    if not ci_enabled:
        return ci_message


def what_to_do_now_req(experiment):
    req_message = "Add some packages you wish to use on the Manage Your Requirements tab"
    reqs_defined = False
    reqs_list = ExperimentRequirement.objects.filter(experiment=experiment)
    if reqs_list.count() is not 0:
        reqs_defined = True
    if not reqs_defined:
        return req_message


def get_files_in_repository(user, experiment, github_helper, step=None):
    if not step:
        step = ChosenExperimentSteps.objects.get(experiment=experiment, active=True)
    return github_helper.list_files_in_repo(step.folder_name())


def get_steps(experiment):
    return ChosenExperimentSteps.objects.filter(experiment=experiment).order_by('step_nr')
