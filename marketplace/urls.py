from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from requirements_manager.views import RequirementListView

from marketplace.views import *

urlpatterns = [
    url(r'^$', login_required(MarketplaceIndex.as_view()), name="marketplace_index"),
    url(r'^list/$', login_required(PackageListView.as_view()), name="package_list"),
    url(r'^new/$', login_required(ExternalPackageCreateView.as_view(success_url='/marketplace')), name="package_new"),
    url(r'^new-internal-package/(?P<experiment_id>\d+)/(?P<step_id>\d+)$', login_required(InternalPackageCreateView.as_view()), name="internalpackage_create"),
    url(r'^new/status$', package_status_create, name="package_status_create"),
    url(r'^view/(?P<pk>\d+)/$', package_detail, name="package_detail"),
    url(r'^view/i/(?P<pk>\d+)/$', login_required(InternalPackageDetailView.as_view()), name="internalpackage_detail"),
    url(r'^view/e/(?P<pk>\d+)/$', login_required(ExternalPackageDetailView.as_view()), name="externalpackage_detail"),
    url(r'^(?P<package_id>\d+)/version/new/$', login_required(PackageVersionCreateView.as_view()), name="packageversion_new"),
    url(r'^(?P<package_id>\d+)/internal/version/new/$', login_required(InternalPackageVersionCreateView.as_view()), name="internalpackageversion_new"),
    url(r'^(?P<package_id>\d+)/resource/new/$', login_required(PackageResourceCreateView.as_view()), name="packageresource_new"),
    url(r'^subscribe/(?P<package_id>\d+)/$', login_required(PackageSubscriptionView.as_view()), name="package_subscribe"),
    url(r'^dashboard/(?P<pk>\d+)/$', login_required(InternalPackageDashboard.as_view()), name="internalpackage_dashboard"),
    url(r'^edit/(?P<pk>\d+)/$', login_required(InternalPackageUpdateView.as_view()), name="internalpackage_update"),
    url(r'^install/(?P<pk>\d+)/$', internalpackage_install, name="internalpackage_install"),
    url(r'^my-packages/$', login_required(InternalPackageListView.as_view()), name="internalpackage_list"),
    url(r'^view-version/(?P<pk>\d+)/(?P<package_id>\d+)/$', login_required(PackageVersionDetailView.as_view()), name="packageversion_detail"),
    url(r'^packages/autocomplete/$', package_autocomplete, name="package_autocomplete"),
    url(r'^resources/list/(?P<pk>\d+)/$', login_required(PackageResourceListView.as_view()), name="packageresource_list"),
    url(r'^dependencies/(?P<pk>\d+)/(?P<object_type>\w+)/$', login_required(RequirementListView.as_view(template_name='marketplace/package_detail/package_dependencies.html')), name="package_dependencies"),
    url(r'^versions/(?P<pk>\d+)/$', login_required(PackageVersionListView.as_view()), name="packageversion_list"),
    url(r'^publish/checklist/(?P<pk>\d+)/$', internalpackage_publish_checklist, name="internalpackage_checklist"),
    url(r'^publish/(?P<pk>\d+)/$', internalpackage_publish, name="internalpackage_publish"),
    url(r'^remove-publish/(?P<pk>\d+)/$', internalpackage_remove, name="internalpackage_remove"),
]
