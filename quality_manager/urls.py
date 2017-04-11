from django.conf.urls import url
from quality_manager.views import DashboardView
from quality_manager.views import NrOfCommitsView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^dashboard/(?P<experiment_id>\d+)/$', login_required(DashboardView.as_view()), name="dashboard"),
    url(r'^vcs/overview/$', login_required(TemplateView.as_view(template_name="quality_manager/vcs_overview.html")), name="vcs_overview"),
    url(r'^vcs/raw/(?P<experiment_id>\d+)/$', login_required(NrOfCommitsView.as_view()), name="nr_of_commits"),
]
