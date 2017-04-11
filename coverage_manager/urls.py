from django.conf.urls import url
from coverage_manager.views import coveralls_enable
from coverage_manager.views import coveralls_disable
from coverage_manager.views import coveralls_status

urlpatterns = [
    url(r'^enable-coverage/$', coveralls_enable, name="coveralls_enable"),
    url(r'^disable-coverage/$', coveralls_disable, name="coveralls_disable"),
    url(r'^coverage-status/(?P<experiment_id>\d+)/$', coveralls_status, name="coveralls_status"),
]
