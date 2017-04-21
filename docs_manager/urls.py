from django.conf.urls import url
from docs_manager.views import DocExperimentView
from docs_manager.views import DocStatusView
from docs_manager.views import toggle_docs_status
from docs_manager.views import docs_generate
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^view/(?P<object_id>\d+)/(?P<object_type>\w+)/$', login_required(DocExperimentView.as_view()), name="docs_view"),
        url(r'^view/(?P<object_id>\d+)/(?P<object_type>\w+)/(?P<page_slug>[\w\-]+)/$', login_required(DocExperimentView.as_view()), name="docs_view"),
        url(r'^status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', login_required(DocStatusView.as_view()), name="docs_status"),
        url(r'^toggle-status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', toggle_docs_status, name="toggle_docs_status"),
        url(r'^rebuild/(?P<object_id>\d+)/(?P<object_type>\w+)/$', docs_generate, name="docs_generate"),
    ]
