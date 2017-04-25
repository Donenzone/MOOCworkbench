from django.conf.urls import url
from requirements_manager.views import write_requirements_file
from requirements_manager.views import RequirementListView, RequirementCreateView
from requirements_manager.views import remove_experiment_requirement
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^(?P<pk>\d+)/(?P<object_type>\w+)/$', login_required(RequirementListView.as_view()), name="requirements_list"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/write$', write_requirements_file, name="requirements_write"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/save/$', login_required(RequirementCreateView.as_view()), name="requirement_add"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/delete/$', remove_experiment_requirement, name="requirement_delete"),
]
