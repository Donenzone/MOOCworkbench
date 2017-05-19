from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from requirements_manager.views import RequirementListView
from dataschema_manager.views import DataSchemaOverview
from quality_manager.views import DashboardView

import experiments_manager.views

urlpatterns = [
    url(r'^$', experiments_manager.views.index, name="experiments_index"),
    url(r'^new$', login_required(experiments_manager.views.ExperimentCreateView.as_view()), name="experiment_new"),
    url(r'^new/status$', experiments_manager.views.experiment_status_create, name="experiment_status_create"),
    url(r'^new/enable-builds/(?P<pk>\d+)', experiments_manager.views.experiment_first_time, name="experiment_first_time"),
    url(r'^steps/(?P<experiment_id>\d+)$', experiments_manager.views.ChooseExperimentSteps.as_view(), name="experimentsteps_choose"),
    url(r'^step/files$', experiments_manager.views.FileListForStep.as_view(), name="file_list_for_step"),
    url(r'^next-step/(?P<experiment_id>\d+)$', experiments_manager.views.complete_step_and_go_to_next, name="complete_step_and_go_to_next"),
    url(r'^edit/(?P<experiment_id>\d+)$', login_required(experiments_manager.views.ExperimentCreateView.as_view()), name="experiment_edit"),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)$', login_required(experiments_manager.views.ExperimentDetailView.as_view()), name='experiment_detail'),
    url(r'^publish/(?P<pk>\d+)/(?P<slug>[-\w]+)/step-1$', experiments_manager.views.experiment_publish, name='experiment_publish'),
    url(r'^publish/(?P<pk>\d+)/(?P<slug>[-\w]+)/step-2$', experiments_manager.views.experiment_generate_uuid_and_make_public, name='experiment_publish_2'),
    url(r'^readonly/(?P<unique_id>[-\w]+)$', experiments_manager.views.ExperimentReadOnlyView.as_view(), name='experiment_readonly'),
    url(r'^file/(?P<experiment_id>\d+)/$', login_required(experiments_manager.views.FileViewGitRepository.as_view()), name='file_detail'),
    url(r'^readme/(?P<experiment_id>\d+)/$', experiments_manager.views.readme_of_experiment, name='experiment_readme'),
    url(r'^dependencies/(?P<pk>\d+)/(?P<object_type>[-\w]+)/$',
        login_required(RequirementListView.as_view(template_name='experiments_manager/experiment_detail/experiment_dependencies.html')),
        name='experiment_dependencies'),
    url(r'^overview/(?P<experiment_id>\d+)$',
        login_required(DataSchemaOverview.as_view(template_name='experiments_manager/experiment_detail/experiment_schema.html')),
        name="experiment_schema"),
    url(r'^dashboard/(?P<experiment_id>\d+)/$',
        login_required(DashboardView.as_view(template_name='experiments_manager/experiment_detail/experiment_dashboard.html')),
        name="experiment_dashboard"),
    url(r'^issues/(?P<experiment_id>\d+)/$', experiments_manager.views.experiment_issues,
            name="experiment_issues"),
    url(r'^single-issues/(?P<experiment_id>\d+)/(?P<issue_nr>\d+)$', experiments_manager.views.experiment_single_issue,
            name="experiment_single_issue"),
    url(r'^score-card/(?P<pk>\d+)/(?P<slug>[-\w]+)$', experiments_manager.views.experimentstep_scorecard,
        name='experimentstep_scorecard'),

]
