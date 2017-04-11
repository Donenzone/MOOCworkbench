from experiments_manager.helper import verify_and_get_experiment
from docs_manager.models import Docs


class DocsMixin(object):
    def get_context_data(self, **kwargs):
        context = super(DocsMixin, self).get_context_data(**kwargs)
        experiment = verify_and_get_experiment(self.request, self.kwargs['pk'])
        context['docs'] = self._get_docs(experiment)
        return context

    def _get_docs(self, experiment):
        docs = Docs.objects.filter(experiment=experiment)
        if docs.count() is not 0:
            return docs[0]
