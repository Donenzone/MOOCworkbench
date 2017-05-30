from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus
from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper
from helpers.helper import get_package_or_experiment
from helpers.helper_mixins import ExperimentPackageTypeMixin

from .tasks import task_generate_docs


class DocView(View):
    def get(self, request, object_id, object_type, page_slug=None):
        exp_or_package = get_package_or_experiment(request, object_type, object_id)
        language_helper = exp_or_package.language_helper()
        if page_slug:
            location = language_helper.get_document(page_slug)
        else:
            location = language_helper.get_document('index')
        return redirect(to=location)


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
    send_message(exp_or_package.owner.user.username, MessageStatus.INFO,
                 'Task to regenerate documentation started.')
    task_generate_docs.delay(object_type, object_id)
    return JsonResponse({})
