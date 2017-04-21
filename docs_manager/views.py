from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.decorators import login_required

from docs_manager.sphinx_helper import SphinxHelper
from experiments_manager.helper import get_steps, verify_and_get_experiment
from experiments_manager.mixins import ExperimentContextMixin
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from helpers.helper import get_package_or_experiment
from helpers.helper_mixins import ExperimentPackageTypeMixin


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


class DocStatusView(ExperimentPackageTypeMixin, View):
    def get(self, request, object_id, object_type):
        context = {}
        django_object = get_package_or_experiment(request, object_type, object_id)
        context['object'] = django_object
        context['docs'] = django_object.docs
        context['object_type'] = object_type
        return render(request, 'docs_manager/docs_status.html', context)


@login_required
def toggle_docs_status(request, object_id, object_type):
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    docs = exp_or_package.docs
    docs.enabled = not docs.enabled
    docs.save()

    if docs.enabled:
        github_helper = GitHubHelper(request.user, exp_or_package.git_repo.name)
        git_helper = GitHelper(github_helper)
        git_helper.clone_repository()

    return redirect(exp_or_package.get_absolute_url())


@login_required
def docs_generate(request, object_id, object_type):
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    github_helper = GitHubHelper(request.user, exp_or_package.git_repo.name)
    git_helper = GitHelper(github_helper)
    git_helper.pull_repository()
    folders = exp_or_package.get_docs_folder()
    sphinx_helper = SphinxHelper(exp_or_package, folders, github_helper.github_repository.owner.login)
    sphinx_helper.add_sphinx_to_repo()
    sphinx_helper.build_and_sync_docs()
    return redirect(exp_or_package.get_absolute_url())
