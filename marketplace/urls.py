from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from marketplace.views import *

urlpatterns = [
    url(r'^$', login_required(MarketplaceIndex.as_view()), name="marketplace_index"),
    url(r'^list/$', login_required(PackageListView.as_view()), name="package_list"),
    url(r'^new/$', login_required(ExternalPackageCreateView.as_view(success_url='/marketplace')), name="package_new"),
    url(r'^new-internal-package/(?P<experiment_id>\d+)/(?P<step_id>\d+)$', login_required(InternalPackageCreateView.as_view()), name="internalpackage_create"),
    url(r'^view/(?P<pk>\d+)/$', login_required(PackageDetailView.as_view()), name="package_detail"),
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
]
