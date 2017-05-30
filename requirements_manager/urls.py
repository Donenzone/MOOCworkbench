from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import (RequirementCreateView, RequirementListView,
                    RequirementUpdateView, remove_experiment_requirement,
                    write_requirements_file)

urlpatterns = [
    url(r'^(?P<pk>\d+)/(?P<object_type>\w+)/$', login_required(RequirementListView.as_view()), name="requirements_list"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/write$', write_requirements_file, name="requirements_write"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/save/$', login_required(RequirementCreateView.as_view()), name="requirement_add"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/edit/(?P<pk>\d+)$', login_required(RequirementUpdateView.as_view()),
        name="requirement_edit"),
    url(r'^(?P<object_id>\d+)/(?P<object_type>\w+)/delete/$', remove_experiment_requirement,
        name="requirement_delete"),
]
