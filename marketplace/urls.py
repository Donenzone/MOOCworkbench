from django.conf.urls import url
from marketplace.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', login_required(MarketplaceIndex.as_view()), name="marketplace_index"),
    url(r'^list/$', login_required(PackageListView.as_view()), name="package_list"),
    url(r'^new/$', login_required(ExternalPackageCreateView.as_view(success_url='/marketplace')), name="package_new"),
    url(r'^new-internal-package/(?P<experiment_id>\d+)/(?P<step_id>\d+)$', login_required(InternalPackageCreateView.as_view()), name="internal_package_new"),
    url(r'^view/(?P<pk>\d+)/$', login_required(PackageDetailView.as_view()), name="package_detail"),
    url(r'^(?P<package_id>\d+)/version/new/$', login_required(PackageVersionCreateView.as_view()), name="packageversion_new"),
    url(r'^(?P<package_id>\d+)/resource/new/$', login_required(PackageResourceCreateView.as_view()), name="packageresource_new"),
    url(r'^subscribe/(?P<package_id>\d+)/$', login_required(PackageSubscriptionView.as_view()), name="package_subscribe"),
]
