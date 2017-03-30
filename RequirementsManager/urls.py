from django.conf.urls import url
from RequirementsManager.views import write_requirements_file
from RequirementsManager.views import ExperimentRequirementListView, ExperimentRequirementCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', login_required(ExperimentRequirementListView.as_view()), name="experimentrequirements_list"),
    url(r'^(?P<experiment_id>\d+)/write$', write_requirements_file, name="write_requirements_file"),
    url(r'^(?P<experiment_id>\d+)/$', login_required(ExperimentRequirementCreateView.as_view()), name="add_experiment_requirement"),
]
