from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.decorators import login_required

from docs_manager.models import Docs
from docs_manager.sphinx_helper import SphinxHelper
from experiments_manager.helper import get_steps, verify_and_get_experiment
from experiments_manager.mixins import ExperimentContextMixin
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper


class DocExperimentView(ExperimentContextMixin, View):

    def get(self, request, experiment_id, page_slug=None):
        context = super(DocExperimentView, self).get(request, experiment_id)
        steps = get_steps(self.experiment)
        github_helper = GitHubHelper(request.user, self.experiment.git_repo.name)
        sphinx_helper = SphinxHelper(self.experiment, steps, github_helper.owner)
        if page_slug:
            context['document'] = sphinx_helper.get_document(page_slug)
        else:
            context['document'] = sphinx_helper.get_document('index')
        return render(request, 'docs_manager/docs_template.html', context)


class DocStatusView(ExperimentContextMixin, View):

    def get(self, request, experiment_id):
        context = super(DocStatusView, self).get(request, experiment_id)
        experiment = verify_and_get_experiment(request, experiment_id)
        context['docs'] = self.get_docs(experiment)
        return render(request, 'docs_manager/docs_status.html', context)

    def get_docs(self, experiment):
        docs = experiment.docs
        if docs:
            return docs
        else:
            docs = Docs()
            docs.save()

            experiment.docs = docs
            experiment.save()
            return docs


@login_required
def toggle_docs_status(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    docs = experiment.docs
    docs.enabled = not docs.enabled
    docs.save()

    if docs.enabled:
        github_helper = GitHubHelper(request.user, experiment.git_repo.name)
        git_helper = GitHelper(github_helper)
        git_helper.clone_repository()

    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))


@login_required
def docs_generate(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    github_helper = GitHubHelper(request.user, experiment.git_repo.name)
    git_helper = GitHelper(github_helper)
    git_helper.pull_repository()
    steps = get_steps(experiment)
    sphinx_helper = SphinxHelper(experiment, steps, github_helper.github_repository.owner.login)
    sphinx_helper.add_sphinx_to_repo()
    sphinx_helper.build_and_sync_docs()
    return redirect(to=reverse('experiment_detail', kwargs={'pk': experiment_id, 'slug': experiment.slug()}))
