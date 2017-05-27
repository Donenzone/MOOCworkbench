from markdownx.utils import markdownify

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, View
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required

from experiments_manager.mixins import ActiveExperimentsList
from helpers.helper_mixins import ExperimentPackageTypeMixin
from user_manager.models import get_workbench_user
from recommendations.utils import recommend

from ..models import Package, InternalPackage, ExternalPackage, PackageVersion, PackageResource
from .views_internalpackage import InternalPackageBaseView
from ..tasks import task_check_for_new_package_version
from ..mixins import IsInternalPackageMixin, ObjectTypeIdMixin


class MarketplaceIndex(View):
    def get(self, request):
        context = {}
        context['new_packages'] = ExternalPackage.objects.all().order_by('-created')[:5]
        context['new_internal_packages'] = InternalPackage.objects.all().order_by('-created')[:5]
        context['recent_updates'] = PackageVersion.objects.all().order_by('-created')[:5]
        context['recent_resources'] = PackageResource.objects.all().order_by('-created')[:5]
        return render(request, 'marketplace/marketplace_index.html', context=context)


class ExternalPackageCreateView(CreateView):
    model = ExternalPackage
    fields = ['name', 'description', 'project_page', 'category', 'language']
    template_name = 'marketplace/package_create/package_form.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalPackageCreateView, self).get_context_data(**kwargs)
        context['external'] = True
        return context

    def form_valid(self, form):
        form.instance.owner = get_workbench_user(self.request.user)
        return super(ExternalPackageCreateView, self).form_valid(form)


class PackageListView(ListView):
    model = Package


@login_required
def package_detail(request, pk):
    if InternalPackage.objects.filter(pk=pk):
        return redirect(to=reverse('internalpackage_detail', kwargs={'pk': pk}))
    else:
        return redirect(to=reverse('externalpackage_detail', kwargs={'pk': pk}))


class ExternalPackageDetailView(InternalPackageBaseView, ActiveExperimentsList, DetailView):
    model = ExternalPackage
    template_name = 'marketplace/package_detail/package_detail.html'

    def get_context_data(self, **kwargs):
        self.object_type = ExperimentPackageTypeMixin.PACKAGE_TYPE
        context = super(ExternalPackageDetailView, self).get_context_data(**kwargs)
        package_id = self.kwargs['pk']
        context['version_history'] = PackageVersion.objects.filter(package=package_id).order_by('-created')[:5]
        task_check_for_new_package_version.delay()
        context['index_active'] = True
        return context


class PackageVersionListView(InternalPackageBaseView, ListView):
    model = PackageVersion
    template_name = 'marketplace/package_detail/packageversion_list.html'

    def get_queryset(self):
        qs = super(PackageVersionListView, self).get_queryset()
        package_id = self.kwargs['pk']
        return qs.filter(package_id=package_id)

    def get_context_data(self, **kwargs):
        context = super(PackageVersionListView, self).get_context_data(**kwargs)
        context['versions_active'] = True
        return context


class PackageVersionDetailView(DetailView):
    model = PackageVersion
    template_name = 'marketplace/packageversion_detail.html'

    def get_queryset(self):
        qs = super(PackageVersionDetailView, self).get_queryset()
        package_id = self.kwargs['package_id']
        return qs.filter(package_id=package_id)


class PackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ['version_nr', 'changelog', 'url']
    template_name = 'marketplace/package_detail/packageversion_form.html'

    def form_valid(self, form):
        package = Package.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        return super(PackageVersionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('package_detail', kwargs={'pk': self.kwargs['package_id']})


class PackageResourceCreateView(CreateView):
    model = PackageResource
    fields = ['title', 'resource', 'url']

    def get_context_data(self, **kwargs):
        context = super(PackageResourceCreateView, self).get_context_data(**kwargs)
        context['package'] = Package.objects.get(id=self.kwargs['package_id'])
        return context

    def form_valid(self, form):
        package = Package.objects.get(id=self.kwargs['package_id'])
        form.instance.package = package
        form.instance.added_by = get_workbench_user(self.request.user)
        return super(PackageResourceCreateView, self).form_valid(form)


class PackageResourceDetailView(ObjectTypeIdMixin, IsInternalPackageMixin, DetailView):
    model = PackageResource
    template_name = 'marketplace/packageresource_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PackageResourceDetailView, self).get_context_data(**kwargs)
        context['package'] = self.object.package
        context['resources_active'] = True
        return context


class PackageResourceListView(InternalPackageBaseView, ListView):
    model = PackageResource
    paginate_by = 10
    template_name = 'marketplace/package_detail/packageresource_list.html'

    def get_queryset(self):
        package_id = self.kwargs['pk']
        return PackageResource.objects.filter(package__id=package_id)

    def get_context_data(self, **kwargs):
        context = super(PackageResourceListView, self).get_context_data(**kwargs)
        context['object'] = Package.objects.get(pk=self.kwargs['pk'])
        context['resources_active'] = True
        return context


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
def package_autocomplete(request):
    if 'query' in request.POST:
        query = request.POST['query']
        packages = Package.objects.filter(name__icontains=query)
    else:
        packages = Package.objects.all()[:50]
    result_list = [x.name for x in packages]
    return JsonResponse({'results': result_list})


@login_required
def package_status_create(request):
    return render(request, 'marketplace/package_create/package_status_create.html', {})


@login_required
def recommend_package(request, pk):
    package = Package.objects.get(id=pk)
    workbench_user = get_workbench_user(request.user)
    return recommend(package, workbench_user)


@login_required
def recommend_packageresource(request, pk):
    resource = PackageResource.objects.get(id=pk)
    workbench_user = get_workbench_user(request.user)
    return recommend(resource, workbench_user)


@login_required
def markdownify_text(request):
    if request.POST and 'markdown' in request.POST:
        markdown = request.POST.get('markdown')
        markdown = markdownify(markdown)
        return JsonResponse({'markdown': markdown})
