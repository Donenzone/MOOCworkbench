from django.shortcuts import render
from marketplace.models import Package, InternalPackage, ExternalPackage, PackageVersion, PackageResource
from django.views.generic.list import ListView
from django.views.generic import CreateView, DetailView, View
from user_manager.models import get_workbench_user
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from markdownx.utils import markdownify
from experiments_manager.models import ChosenExperimentSteps
from experiments_manager.helper import verify_and_get_experiment


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
    fields = ['package_name', 'description', 'project_page']
    template_name = 'marketplace/package_form.html'


class InternalPackageCreateView(CreateView):
    model = InternalPackage
    fields = ['package_name', 'description', 'category', 'language']
    template_name = 'marketplace/package_form.html'

    def form_valid(self, form):
        response = super(InternalPackageCreateView, self).form_valid(form)
        print(response)
        step_id = self.kwargs['step_id']
        step_folder = ChosenExperimentSteps.objects.get(pk=step_id).folder_name()
        experiment_id = self.kwargs['experiment_id']
        experiment = verify_and_get_experiment(self.request, experiment_id)

        # save new internal package
        form.instance.repo = git_repo_obj
        return


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
