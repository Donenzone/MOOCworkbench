from django.conf.urls import url
from marketplace.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', login_required(marketplaceIndex.as_view()), name="marketplace_index"),
    url(r'^list$', login_required(PackageListView.as_view()), name="package_list"),
    url(r'^new$', login_required(PackageCreateView.as_view(success_url='/marketplace')), name="package_new"),
    url(r'^view/(?P<pk>[-\w]+)/$', login_required(PackageDetailView.as_view()), name="package_detail"),
    url(r'^(?P<package_id>[-\w]+)/version/new/$', login_required(PackageVersionCreateView.as_view()), name="packageversion_new"),
    url(r'^(?P<package_id>[-\w]+)/resource/new/$', login_required(PackageResourceCreateView.as_view()), name="packageresource_new"),
    url(r'^subscribe/(?P<package_id>[-\w]+)/$', login_required(PackageSubscriptionView.as_view()), name="package_subscribe"),
]
