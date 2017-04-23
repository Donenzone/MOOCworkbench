from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from feedback.views import set_task_active
from feedback.views import UserTaskListView
from feedback.views import FeedbackCreateView

urlpatterns = [
    url(r'^task-active/(?P<task_id>[-\w]+)/$', set_task_active, name="task_active"),
    url(r'^my-tasks/$', login_required(UserTaskListView.as_view()), name="task_list"),
    url(r'^create-feedback/(?P<task_id>[-\w]+)/$', login_required(FeedbackCreateView.as_view()), name="feedback_create"),
    url(r'^create-feedback/$', login_required(FeedbackCreateView.as_view()), name="feedback_create"),
]
