from django.conf.urls import url
from Feedback.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^task-active/(?P<task_id>[-\w]+)/$', set_task_active, name="set_task_active"),
]
