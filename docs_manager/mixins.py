from experiments_manager.helper import verify_and_get_experiment
from docs_manager.models import Docs


class DocsMixin(object):
    def get_context_data(self, **kwargs):
        context = super(DocsMixin, self).get_context_data(**kwargs)
        context['docs'] = self.object.docs
        return context

