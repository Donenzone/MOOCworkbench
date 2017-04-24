from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from quality_manager.views import DashboardView
from quality_manager.views import NrOfCommitsView
from quality_manager.views import VcsOverviewView
from quality_manager.views import refresh_measurements


urlpatterns = [
    url(r'^dashboard/(?P<experiment_id>\d+)/$', login_required(DashboardView.as_view()), name="dashboard"),
    url(r'^vcs/overview/(?P<experiment_id>\d+)/$', login_required(VcsOverviewView.as_view()), name="vcs_overview"),
    url(r'^vcs/raw/(?P<experiment_id>\d+)/$', login_required(NrOfCommitsView.as_view()), name="nr_of_commits"),
    url(r'^refresh/(?P<experiment_id>\d+)/$', refresh_measurements, name="measurements_refresh"),
]
