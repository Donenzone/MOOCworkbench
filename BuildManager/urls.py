from django.conf.urls import url
from BuildManager.views import build_experiment_now
from BuildManager.views import create_new_ci_config
from BuildManager.views import build_status

urlpatterns = [
    url(r'^new-ci-config/$', create_new_ci_config, name="create_new_ci_config"),
    url(r'^build-experiment/$', build_experiment_now, name="build_experiment_now"),
    url(r'^build-status/(?P<experiment_id>[-\w]+)/$', build_status, name="build_status"),
]
