from django.conf.urls import url
from QualityManager.views import overview_metrics

urlpatterns = [
    url(r'^overview/(?P<experiment_id>[-\w]+)/$', overview_metrics, name="overview_metrics"),
]
