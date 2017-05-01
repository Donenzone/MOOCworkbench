from markdownx.utils import markdownify
from dal import autocomplete

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, View
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required

from experiments_manager.helper import verify_and_get_experiment
from experiments_manager.models import ChosenExperimentSteps
from experiments_manager.mixins import ActiveExperimentsList
from git_manager.utils.repo_init import PackageGitRepoInit
from helpers.helper_mixins import ExperimentPackageTypeMixin
from marketplace.forms import InternalPackageForm
from marketplace.helpers.helper import create_tag_for_package_version
from marketplace.helpers.helper import update_setup_py_with_new_version
from marketplace.models import Package, InternalPackage, ExternalPackage, PackageVersion, PackageResource
from user_manager.models import get_workbench_user
from requirements_manager.helper import add_internalpackage_to_experiment


class MarketplaceIndex(View):
    def get(self, request):
        context = {}
        context['new_packages'] = ExternalPackage.objects.all().order_by('-created')[:5]
        context['new_internal_packages'] = InternalPackage.objects.all().order_by('-created')[:5]
        context['recent_updates'] = PackageVersion.objects.all().order_by('-created')[:5]
        context['recent_resources'] = PackageResource.objects.all().order_by('-created')[:5]
        return render(request, 'marketplace/marketplace_index.html', context=context)


class PackageListView(ListView):
    model = Package


class ExternalPackageCreateView(CreateView):
    model = ExternalPackage
    fields = ['name', 'description', 'project_page', 'category', 'language']
    template_name = 'marketplace/package_form.html'

    def form_valid(self, form):
        form.instance.owner = get_workbench_user(self.request.user)
        return super(ExternalPackageCreateView, self).form_valid(form)


class ExternalPackageDetailView(ActiveExperimentsList, DetailView):
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
    form_class = InternalPackageForm
    template_name = 'marketplace/package_form.html'

    def get_context_data(self, **kwargs):
        context = super(InternalPackageCreateView, self).get_context_data(**kwargs)
        context['experiment_id'] = self.kwargs['experiment_id']
        context['step_id'] = self.kwargs['step_id']
        return context

    def form_valid(self, form):
        step_folder = self.get_step().location
        experiment = self.get_experiment()
        form.instance.owner = experiment.owner

        # save new internal package
        package_repo = PackageGitRepoInit(form.instance, experiment, step_folder)
        form.instance.git_repo = package_repo.init_repo_boilerplate()
        return super(InternalPackageCreateView, self).form_valid(form)

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


class InternalPackageDetailView(ActiveExperimentsList, DetailView):
    model = InternalPackage

    def get_context_data(self, **kwargs):
        context = super(InternalPackageDetailView, self).get_context_data(**kwargs)
        package_id = self.kwargs['pk']
        context['version_history'] = PackageVersion.objects.filter(package=package_id).order_by('-created')[:5]
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
        create_tag_for_package_version(form.instance.id)
        update_setup_py_with_new_version(form.instance.id)
        return response

    def get_success_url(self):
        return reverse('internalpackage_dashboard', kwargs={'pk': self.kwargs['package_id']})


class PackageVersionDetailView(DetailView):
    model = PackageVersion

    def get_queryset(self):
        qs = super(PackageVersionDetailView, self).get_queryset()
        package_id = self.kwargs['package_id']
        return qs.filter(package_id=package_id)


class PackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ['version_nr', 'changelog', 'url']

    def form_valid(self, form):
        package = Package.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        return super(PackageVersionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('package_detail', kwargs={'pk': self.kwargs['package_id']})


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
        messages.add_message(request, messages.SUCCESS, 'Subscription preferences changed')
        return HttpResponseRedirect(redirect_to=reverse('package_detail', kwargs={'pk': package_id}))


@login_required
def internalpackage_install(request, pk):
    internal_package = InternalPackage.objects.get(pk=pk)
    assert 'experiment_id' in request.POST
    experiment_id = request.POST['experiment_id']
    experiment = verify_and_get_experiment(request, experiment_id)
    result = add_internalpackage_to_experiment(internal_package, experiment)
    if result:
        messages.add_message(request, messages.SUCCESS, 'Added package to your experiment')
        return JsonResponse({'added': True})
    else:
        messages.add_message(request, messages.ERROR, 'Could not add package to your experiment')
        return JsonResponse({'added': False})


@login_required
def package_autocomplete(request):
    if 'query' in request.POST:
        query = request.POST['query']
        packages = Package.objects.filter(name__icontains=query)
    else:
        packages = Package.objects.all()[:50]
    result_list = [x.name for x in packages]
    return JsonResponse({'results': result_list})
