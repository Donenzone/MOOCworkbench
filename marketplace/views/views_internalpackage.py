import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, UpdateView, View
from django.views.generic.list import ListView
from markdown2 import Markdown

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.mixins import ActiveExperimentsList
from experiments_manager.models import ChosenExperimentSteps
from git_manager.helpers.github_helper import GitHubHelper, get_github_helper
from git_manager.mixins.repo_file_list import get_files_for_repository
from helpers.helper_mixins import ExperimentPackageTypeMixin
from marketplace.forms import InternalPackageForm
from marketplace.helpers.helper import (create_tag_for_package_version,
                                        update_setup_py_with_new_version)
from marketplace.mixins import IsInternalPackageMixin, ObjectTypeIdMixin
from marketplace.models import InternalPackage, PackageResource, PackageVersion
from marketplace.tasks import (task_create_package_from_experiment,
                               task_publish_update_package,
                               task_remove_package,
                               task_create_package)
from requirements_manager.helper import add_internalpackage_to_experiment
from user_manager.models import get_workbench_user

logger = logging.getLogger(__name__)


class InternalPackageBaseView(ObjectTypeIdMixin, IsInternalPackageMixin):
    class Meta:
        abstract = True


class InternalPackageCreateView(ExperimentPackageTypeMixin, CreateView):
    model = InternalPackage
    form_class = InternalPackageForm
    template_name = 'marketplace/package_create/package_form.html'
    success_url = '/packages/new/status'

    def get_context_data(self, **kwargs):
        context = super(InternalPackageCreateView, self).get_context_data(**kwargs)
        logger.info('%s started on package creation for own code', self.request.user)
        return context

    def form_valid(self, form):
        form.instance.owner = get_workbench_user(self.request.user)
        form.instance.template_id = 1
        response = super(InternalPackageCreateView, self).form_valid(form)
        task_create_package.delay(form.instance.pk)
        return response


class InternalPackageCreateFromExperimentView(ExperimentPackageTypeMixin, CreateView):
    model = InternalPackage
    form_class = InternalPackageForm
    template_name = 'marketplace/package_create/package_form.html'
    success_url = '/packages/new/status'

    def get_context_data(self, **kwargs):
        context = super(InternalPackageCreateFromExperimentView, self).get_context_data(**kwargs)
        context['experiment_id'] = self.kwargs['experiment_id']
        context['step_id'] = self.kwargs['step_id']

        logger.info('%s started on package creation for %s', self.request.user, self.kwargs['experiment_id'])
        return context

    def form_valid(self, form):
        step_folder = self.get_step().location
        experiment = self.get_experiment()
        form.instance.owner = experiment.owner
        form.instance.template_id = 1
        response = super(InternalPackageCreateFromExperimentView, self).form_valid(form)
        task_create_package_from_experiment.delay(form.instance.pk, experiment.pk, step_folder)
        return response

    def get_experiment(self):
        experiment_id = self.kwargs['experiment_id']
        experiment = verify_and_get_experiment(self.request, experiment_id)
        return experiment

    def get_step(self):
        step_id = self.kwargs['step_id']
        step = ChosenExperimentSteps.objects.get(pk=step_id)
        return step


class InternalPackageListView(ListView):
    model = InternalPackage

    def get_queryset(self):
        qs = super(InternalPackageListView, self).get_queryset()
        return qs.filter(owner__user_id=self.request.user.id)


class InternalPackageDashboard(ExperimentPackageTypeMixin, View):
    def get(self, request, pk):
        package = get_object_or_404(InternalPackage, pk=pk)

        assert package.owner.user == self.request.user

        context = {'docs': package.docs,
                   'package': package,
                   'object_id': package.pk,
                   'object_type': package.get_object_type(),
                   'edit_form': InternalPackageForm(instance=package),
                   'dashboard_active': True,
                   'is_internal': True}
        return render(request, 'marketplace/package_detail/internalpackage_dashboard.html', context)


class InternalPackageUpdateView(UpdateView):
    model = InternalPackage
    form_class = InternalPackageForm

    def get_success_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        assert form.instance.owner.user == self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Package successfully updated')
        return super(InternalPackageUpdateView, self).form_valid(form)


class InternalPackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ['version_nr', 'changelog', 'pre_release']
    template_name = 'marketplace/package_detail/packageversion_form.html'

    def get_context_data(self, **kwargs):
        context = super(InternalPackageVersionCreateView, self).get_context_data(**kwargs)
        context['package'] = InternalPackage.objects.get(id=self.kwargs['package_id'])
        return context

    def form_valid(self, form):
        package = InternalPackage.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        assert form.instance.package.owner.user == self.request.user
        form.instance.added_by = get_workbench_user(self.request.user)
        response = super(InternalPackageVersionCreateView, self).form_valid(form)
        create_tag_for_package_version(form.instance.id)
        update_setup_py_with_new_version(form.instance.id)
        task_publish_update_package.delay(package.pk)
        return response

    def get_success_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['package_id']})


@login_required
def internalpackage_publish(request, pk):
    package = InternalPackage.objects.get(id=pk)
    assert package.owner.user == request.user
    task_publish_update_package.delay(package.pk)
    logger.info('%s published the package %s', request.user, package)
    return redirect(to=package.get_absolute_url())


@login_required
def internalpackage_publish_checklist(request, pk):
    package = InternalPackage.objects.get(id=pk)
    assert package.owner.user == request.user
    dependencies_defined = package.requirements.count() != 0
    getting_started_guide = PackageResource.objects.filter(package=package.id, title='Getting started')
    getting_started = False
    if getting_started_guide:
        getting_started_guide = getting_started_guide[0]
        getting_started = len(getting_started_guide.resource) != 0
    return render(request, 'marketplace/package_publish.html', {'object': package,
                                                                'dependencies_defined': dependencies_defined,
                                                                'getting_started': getting_started})


@login_required
def internalpackage_remove(request, pk):
    package = InternalPackage.objects.get(id=pk)
    assert package.owner.user == request.user
    task_remove_package.delay(package.pk)
    logger.info("%s removed the package %s", request.user, package)
    messages.add_message(request, messages.INFO, "Removing package...")
    return redirect(to=package.success_url_dict()['dashboard'])


class InternalPackageDetailView(InternalPackageBaseView, ActiveExperimentsList, DetailView):
    model = InternalPackage
    template_name = 'marketplace/package_detail/package_detail.html'

    def get_context_data(self, **kwargs):
        self.object_type = ExperimentPackageTypeMixin.PACKAGE_TYPE
        context = super(InternalPackageDetailView, self).get_context_data(**kwargs)
        github_helper = get_github_helper(self.request, context['package'])
        package_id = self.kwargs['pk']
        context['version_history'] = PackageVersion.objects.filter(package=package_id).order_by('-created')[:5]
        context['index_active'] = True
        context['git_list'] = get_files_for_repository(github_helper, self.object)
        if InternalPackage.objects.filter(pk=self.object.pk):
            context['readme'] = self.readme_file_of_package()
        return context

    def readme_file_of_package(self):
        internalpackage = InternalPackage.objects.get(id=self.kwargs['pk'])
        github_helper = GitHubHelper(internalpackage.owner, internalpackage.git_repo.name)
        readme = github_helper.view_file('README.md')
        md = Markdown()
        content_file = md.convert(readme)
        return content_file


@login_required
def internalpackage_install(request, pk):
    internal_package = InternalPackage.objects.get(pk=pk)
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)
    result = add_internalpackage_to_experiment(internal_package, experiment)
    if result:
        logger.info('%s installed the package %s in experiment %s', request.user, internal_package, experiment)
        messages.add_message(request, messages.SUCCESS, 'Added package to your experiment')
        return JsonResponse({'added': True})
    else:
        messages.add_message(request, messages.ERROR, 'Could not add package to your experiment')
        return JsonResponse({'added': False})

