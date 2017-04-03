from django.conf.urls import url
from Feedback.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^task-active/(?P<task_id>[-\w]+)/$', set_task_active, name="set_task_active"),
    url(r'^my-tasks/$', login_required(UserTaskListView.as_view()), name="user_task_list"),
    url(r'^create-feedback/(?P<task_id>[-\w]+)/$', login_required(FeedbackCreateView.as_view()), name="create_feedback"),
    url(r'^create-feedback/$', login_required(FeedbackCreateView.as_view()), name="create_feedback"),
]
