from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import CreateView, DetailView, UpdateView, View
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from markdownx.utils import markdownify

from experiments_manager.models import ChosenExperimentSteps
from experiments_manager.helper import verify_and_get_experiment
from git_manager.repo_init import PackageGitRepoInit
from marketplace.models import Package, InternalPackage, ExternalPackage, PackageVersion, PackageResource
from marketplace.forms import InternalPackageForm
from helpers.helper_mixins import ExperimentPackageTypeMixin
from user_manager.models import get_workbench_user
from marketplace.helpers.helper import create_tag_for_package_version
from marketplace.helpers.helper import update_setup_py_with_new_version


class MarketplaceIndex(View):
    def get(self, request):
        context = {}
        context['new_packages'] = ExternalPackage.objects.all().order_by('-created')[:10]
        context['new_internal_packages'] = InternalPackage.objects.all().order_by('-created')[:10]
        context['recent_updates'] = PackageVersion.objects.all().order_by('-created')[:10]
        context['recent_resources'] = PackageResource.objects.all().order_by('-created')[:10]
        return render(request, 'marketplace/marketplace_index.html', context=context)


class PackageListView(ListView):
    model = Package


class ExternalPackageCreateView(CreateView):
    model = ExternalPackage
    fields = ['package_name', 'description', 'project_page', 'category', 'language']
    template_name = 'marketplace/package_form.html'

    def form_valid(self, form):
        form.instance.owner = get_workbench_user(self.request.user)
        return super(ExternalPackageCreateView, self).form_valid(form)


class ExternalPackageDetailView(DetailView):
    model = ExternalPackage

    def get_context_data(self, **kwargs):
        context = super(ExternalPackageDetailView, self).get_context_data(**kwargs)
        context['version_history'] = PackageVersion.objects.filter(package=self.kwargs['pk']).order_by('-created')[:5]
        resources = PackageResource.objects.filter(package=self.kwargs['pk']).order_by('-created')[:5]
        for resource in resources:
            resource.markdown = markdownify(resource.resource)
        context['resources'] = resources
        return context


class InternalPackageCreateView(ExperimentPackageTypeMixin, CreateView):
    model = InternalPackage
    fields = ['package_name', 'description', 'category', 'language']
    template_name = 'marketplace/package_form.html'

    def form_valid(self, form):
        step_id = self.kwargs['step_id']
        step_folder = ChosenExperimentSteps.objects.get(pk=step_id).folder_name()
        experiment_id = self.kwargs['experiment_id']
        experiment = verify_and_get_experiment(self.request, experiment_id)
        form.instance.owner = experiment.owner

        # save new internal package
        package_repo = PackageGitRepoInit(form.instance, experiment, step_folder)
        form.instance.git_repo = package_repo.init_repo_boilerplate()
        return super(InternalPackageCreateView, self).form_valid(form)


class InternalPackageDashboard(ExperimentPackageTypeMixin, View):
    def get(self, request, pk):
        package = get_object_or_404(InternalPackage, pk=pk)
        context = {}
        context['docs'] = package.docs
        context['object'] = package
        context['object_type'] = self.get_requirement_type(package)
        context['edit_form'] = InternalPackageForm(instance=package)
        return render(request, 'marketplace/internalpackage_dashboard.html', context)


class InternalPackageUpdateView(UpdateView):
    model = InternalPackage
    form_class = InternalPackageForm

    def get_success_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Package successfully updated')
        return super(InternalPackageUpdateView, self).form_valid(form)


class InternalPackageDetailView(DetailView):
    model = InternalPackage

    def get_context_data(self, **kwargs):
        context = super(InternalPackageDetailView, self).get_context_data(**kwargs)
        context['version_history'] = PackageVersion.objects.filter(package=self.kwargs['pk']).order_by('-created')[:5]
        resources = PackageResource.objects.filter(package=self.kwargs['pk']).order_by('-created')[:5]
        for resource in resources:
            resource.markdown = markdownify(resource.resource)
        context['resources'] = resources
        return context


class InternalPackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ['version_nr', 'changelog', 'pre_release']

    def form_valid(self, form):
        package = InternalPackage.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        response = super(InternalPackageVersionCreateView, self).form_valid(form)
        create_tag_for_package_version(package.pk)
        update_setup_py_with_new_version(package.pk)
        return response

    def get_success_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['package_id']})


class PackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ['version_nr', 'changelog', 'url']

    def form_valid(self, form):
        package = Package.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        return super(PackageVersionCreateView, self).form_valid(form)


class PackageResourceCreateView(CreateView):
    model = PackageResource
    fields = ['resource', 'url']

    def form_valid(self, form):
        package = Package.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        return super(PackageResourceCreateView, self).form_valid(form)


class PackageSubscriptionView(View):
    def get(self, request, *args, **kwargs):
        package_id = self.kwargs['package_id']
        package = Package.objects.get(id=package_id)
        workbench_user = get_workbench_user(request.user)
        if not workbench_user in package.subscribed_users.all():
            package.subscribed_users.add(workbench_user)
            package.save()
        else:
            package.subscribed_users.remove(workbench_user)
            package.save()
        messages.add_message(request, messages.INFO, 'Subscription preferences changed')
        return HttpResponseRedirect(redirect_to=reverse('package_detail', kwargs={'pk': package_id}))
