from django.conf.urls import url

from .views import webhook_receive

urlpatterns = [
    url(r'^receive/$', webhook_receive, name="webhook_receive"),
]
