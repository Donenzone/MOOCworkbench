from django.conf.urls import url
from build_manager.views import build_experiment_now
from build_manager.views import enable_ci_builds
from build_manager.views import disable_ci_builds
from build_manager.views import build_status
from build_manager.views import get_log_from_last_build

urlpatterns = [
    url(r'^enable-builds/$', enable_ci_builds, name="enable_ci_builds"),
    url(r'^disable-builds/$', disable_ci_builds, name="disable_ci_builds"),
    url(r'^build-experiment/$', build_experiment_now, name="build_experiment_now"),
    url(r'^build-status/(?P<experiment_id>\d+)/$', build_status, name="build_status"),
    url(r'^build/last-log/(?P<experiment_id>\d+)/$', get_log_from_last_build, name="last_build_log"),
]
