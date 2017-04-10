from django.conf.urls import url
from DocsManager.views import DocExperimentView
from DocsManager.views import DocStatusView
from DocsManager.views import toggle_docs_status
from DocsManager.views import generate_docs
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^view/(?P<experiment_id>\d+)/$', login_required(DocExperimentView.as_view()), name="view_doc_of_experiment"),
        url(r'^view/(?P<experiment_id>\d+)/(?P<page_slug>[\w\-]+)/$', login_required(DocExperimentView.as_view()), name="view_doc_of_experiment"),
        url(r'^status/(?P<experiment_id>\d+)/$', login_required(DocStatusView.as_view()), name="docs_status"),
        url(r'^toggle-status/(?P<experiment_id>\d+)/$', toggle_docs_status, name="toggle_docs_status"),
        url(r'^rebuild/(?P<experiment_id>\d+)/$', generate_docs, name="generate_docs"),
    ]
