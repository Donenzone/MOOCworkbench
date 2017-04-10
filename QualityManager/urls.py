from django.conf.urls import url
from QualityManager.views import dashboard

urlpatterns = [
    url(r'^dashboard/(?P<experiment_id>[-\w]+)/$', dashboard, name="dashboard"),
]
