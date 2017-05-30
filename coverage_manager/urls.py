from django.conf.urls import url

from coverage_manager.views import (coveralls_disable, coveralls_enable,
                                    coveralls_filecoverage, coveralls_status)

urlpatterns = [
    url(r'^enable-coverage/$', coveralls_enable, name="coveralls_enable"),
    url(r'^disable-coverage/$', coveralls_disable, name="coveralls_disable"),
    url(r'^coverage-status/(?P<object_id>\d+)/(?P<object_type>\w+)/$', coveralls_status, name="coveralls_status"),
    url(r'^file/$', coveralls_filecoverage, name="coveralls_filecoverage"),
]
