from experiments_manager.models import ChosenExperimentSteps
from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.forms import ExperimentSelectForm


class ActiveStepMixin(object):
    def step(self, experiment):
        return ChosenExperimentSteps.objects.get(experiment=experiment, active=True)


class ExperimentContextMixin(object):
    def get(self, request, experiment_id):
        self.experiment = verify_and_get_experiment(request, experiment_id)
        context = {}
        context['experiment'] = self.experiment
        return context


class ActiveExperimentsList(object):
    def get_context_data(self, **kwargs):
        context = super(ActiveExperimentsList, self).get_context_data(**kwargs)
        context['experiment_select_form'] = ExperimentSelectForm(user_id=self.request.user.id)
        return context
