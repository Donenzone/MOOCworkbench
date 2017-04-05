from django.conf.urls import url
from DocsManager.views import view_doc_of_experiment
from DocsManager.views import docs_status
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^view/(?P<experiment_id>\d+)/$', view_doc_of_experiment, name="view_doc_of_experiment"),
        url(r'^view/(?P<experiment_id>\d+)/(?P<page_slug>[\w\-]+)/$', view_doc_of_experiment, name="view_doc_of_experiment"),
        url(r'^status/(?P<experiment_id>\d+)/$', docs_status, name="docs_status"),
    ]
