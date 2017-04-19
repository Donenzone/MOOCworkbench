from django.conf.urls import url
from requirements_manager.views import write_requirements_file
from requirements_manager.views import RequirementListView, RequirementCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', login_required(RequirementListView.as_view()), name="requirements_list"),
    url(r'^(?P<experiment_id>\d+)/write$', write_requirements_file, name="requirements_write"),
    url(r'^(?P<experiment_id>\d+)/save/$', login_required(RequirementCreateView.as_view()), name="requirement_add"),
]
