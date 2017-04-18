from django.shortcuts import render
from marketplace.models import Package, InternalPackage, ExternalPackage, PackageVersion, PackageResource
from django.views.generic.list import ListView
from django.views.generic import CreateView, DetailView, View
from user_manager.models import get_workbench_user
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from markdownx.utils import markdownify
from git_manager.helpers.git_helper import GitHelper
from git_manager.helpers.github_helper import GitHubHelper
from git_manager.models import GitRepository
from experiments_manager.models import ChosenExperimentSteps
from experiments_manager.helper import verify_and_get_experiment


class MarketplaceIndex(View):
    def get(self, request):
        context = {}
        context['new_packages'] = Package.objects.all().order_by('-created')[:10]
        context['new_internal_packages'] = Package.objects.filter(internal_package=True).order_by('-created')[:10]
        context['recent_updates'] = PackageVersion.objects.all().order_by('-created')[:10]
        context['recent_resources'] = PackageResource.objects.all().order_by('-created')[:10]
        return render(request, 'marketplace/marketplace_index.html', context=context)


class PackageListView(ListView):
    model = Package


class ExternalPackageCreateView(CreateView):
    model = ExternalPackage
    fields = ['package_name', 'description', 'internal_package', 'project_page']
    template_name = 'marketplace/package_form.html'


class InternalPackageCreateView(CreateView):
    model = InternalPackage
    fields = ['package_name', 'description', 'category', 'language']
    template_name = 'marketplace/package_form.html'

    def form_valid(self, form):
        step_id = self.kwargs['step_id']
        step_folder = ChosenExperimentSteps.objects.get(pk=step_id).folder_name()
        experiment_id = self.kwargs['experiment_id']
        experiment = verify_and_get_experiment(self.request, experiment_id)

        # create new GitHub repository
        github_helper_package = GitHubHelper(experiment.owner, 'Data-gathering-package')#, create=True)

        # create git repository in DB
        repo = github_helper_package.github_repository
        git_repo_obj = GitRepository()
        git_repo_obj.name = repo.name
        git_repo_obj.owner = get_workbench_user(self.request.user)
        git_repo_obj.github_url = repo.html_url
        git_repo_obj.save()

        # clone current experiment
        github_helper_experiment = GitHubHelper(experiment.owner, experiment.git_repo.name)
        git_helper = GitHelper(github_helper_experiment)
        #git_helper.clone_repository()

        # take code from module and commit it to new repo
        git_helper.filter_and_checkout_subfolder(step_folder)
        new_remote = github_helper_package.get_clone_url()
        git_helper.set_remote(new_remote)
        git_helper.push_changes()

        # save new internal package
        form.instance.repo = git_repo_obj
        return super(InternalPackageCreateView, self).form_valid(form)


class PackageDetailView(DetailView):
    model = Package

    def get_context_data(self, **kwargs):
        context = super(PackageDetailView, self).get_context_data(**kwargs)
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
