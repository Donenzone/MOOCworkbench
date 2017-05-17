from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.forms import ExperimentSelectForm


class ExperimentContextMixin(object):
    def get(self, request, object_id):
        self.experiment = verify_and_get_experiment(request, object_id)
        context = {}
        context['object'] = self.experiment
        context['object_id'] = self.experiment.id
        return context


class ActiveExperimentsList(object):
    def get_context_data(self, **kwargs):
        context = super(ActiveExperimentsList, self).get_context_data(**kwargs)
        context['experiment_select_form'] = ExperimentSelectForm(user_id=self.request.user.id)
        return context
