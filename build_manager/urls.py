"""Internal URLs for build_manager app"""

from django.conf.urls import url

from build_manager.views import (build_experiment_now, build_status,
                                 disable_ci_builds, enable_ci_builds,
                                 get_log_from_last_build)

urlpatterns = [
    url(r'^enable-builds/$', enable_ci_builds, name="enable_ci_builds"),
    url(r'^disable-builds/$', disable_ci_builds, name="disable_ci_builds"),
    url(r'^build-experiment/$', build_experiment_now, name="build_experiment_now"),
    url(r'^status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', build_status, name="build_status"),
    url(r'^last-log/(?P<object_id>\d+)/(?P<object_type>\w+)/$', get_log_from_last_build, name="last_build_log"),
]
