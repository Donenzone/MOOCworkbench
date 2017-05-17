from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from experiments_manager.mixins import ExperimentContextMixin
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.helpers.git_helper import GitHelper
from helpers.helper import get_package_or_experiment
from helpers.helper_mixins import ExperimentPackageTypeMixin


class DocView(ExperimentContextMixin, View):
    def get(self, request, object_id, object_type, page_slug=None):
        context = super(DocView, self).get(request, object_type, object_id)
        language_helper = self.exp_or_package.language_helper()
        if page_slug:
            context['document'] = language_helper.get_document(page_slug)
        else:
            context['document'] = language_helper.get_document('index')
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
        git_helper.clone_or_pull_repository()

    return redirect(exp_or_package.get_absolute_url())


@login_required
def docs_generate(request, object_id, object_type):
    exp_or_package = get_package_or_experiment(request, object_type, object_id)
    if exp_or_package.docs.enabled:
        language_helper = exp_or_package.language_helper()
        language_helper.generate_documentation()
    else:
        messages.add_message(request, messages.WARNING,
                             'Before you can generate docs, first enable docs for your experiment.')
    return redirect(exp_or_package.get_absolute_url())
