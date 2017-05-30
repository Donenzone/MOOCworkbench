from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from docs_manager.views import (DocStatusView, DocView, docs_generate,
                                toggle_docs_status)

urlpatterns = [
        url(r'^view/(?P<object_id>\d+)/(?P<object_type>\w+)/$', login_required(DocView.as_view()), name="docs_view"),
        url(r'^view/(?P<object_id>\d+)/(?P<object_type>\w+)/(?P<page_slug>[\w\-]+)/$', login_required(DocView.as_view()), name="docs_view"),
        url(r'^status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', login_required(DocStatusView.as_view()), name="docs_status"),
        url(r'^toggle-status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', toggle_docs_status, name="toggle_docs_status"),
        url(r'^rebuild/(?P<object_id>\d+)/(?P<object_type>\w+)/$', docs_generate, name="docs_generate"),
    ]
