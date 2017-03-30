from django.conf.urls import url
from BuildManager.views import build_experiment_now
from BuildManager.views import enable_ci_builds
from BuildManager.views import disable_ci_builds
from BuildManager.views import build_status

urlpatterns = [
    url(r'^enable-builds/$', enable_ci_builds, name="enable_ci_builds"),
    url(r'^disable-builds/$', disable_ci_builds, name="disable_ci_builds"),
    url(r'^build-experiment/$', build_experiment_now, name="build_experiment_now"),
    url(r'^build-status/(?P<experiment_id>[-\w]+)/$', build_status, name="build_status"),
]
