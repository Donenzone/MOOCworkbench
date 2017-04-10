from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from DocsManager.sphinx_helper import SphinxHelper
from ExperimentsManager.helper import get_steps
from django.contrib.auth.decorators import login_required
from GitManager.github_helper import GitHubHelper
from DocsManager.models import Docs
from GitManager.clone_module import pull_git_repository, clone_git_repository
from django.views import View
from ExperimentsManager.mixins import ExperimentContextMixin

class DocExperimentView(ExperimentContextMixin, View):

    def get(self, request, experiment_id, page_slug=None):
        context = super(DocViewExperiment, self).get(request, experiment_id)
        steps = get_steps(self.experiment)
        github_helper = GitHubHelper(request.user, self.experiment.git_repo.name)
        sphinx_helper = SphinxHelper(self.experiment, steps, github_helper.github_repository.owner.login)
        if page_slug:
            context['document'] = sphinx_helper.get_document(page_slug)
        else:
            context['document'] = sphinx_helper.get_document('index')
        return render(request, 'DocsManager/docs_template.html', context)


class DocStatusView(ExperimentContextMixin, View):

    def get(self, request, experiment_id):
        context = super(DocStatusView, self).get(request, experiment_id)
        context['docs'] = self.get_docs()
        return render(request, 'DocsManager/docs_status.html', context)

    def get_docs(self):
        docs = Docs.objects.filter(experiment=self.experiment)
        if docs.count() is not 0:
            return docs[0]
        else:
            docs = Docs(experiment=self.experiment)
            docs.save()
            return docs


@login_required
def toggle_docs_status(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    docs = Docs.objects.get(experiment=experiment)
    docs.enabled = not docs.enabled
    docs.save()

    if docs.enabled:
        github_helper = GitHubHelper(request.user, experiment.git_repo.name)
        clone_git_repository(github_helper)

    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))


@login_required
def generate_docs(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    pull_git_repository(github_helper)
    steps = get_steps(experiment)
    sphinx_helper = SphinxHelper(experiment, steps, github_helper.github_repository.owner.login)
    sphinx_helper.add_sphinx_to_repo()
    sphinx_helper.build_and_sync_docs()
    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))
