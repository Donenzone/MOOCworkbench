from django.conf.urls import url
import experiments_manager.views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', experiments_manager.views.index, name="experiments_index"),
    url(r'^new$', login_required(experiments_manager.views.ExperimentCreateView.as_view()), name="experiment_new"),
    url(r'^steps/(?P<experiment_id>\d+)$', experiments_manager.views.ChooseExperimentSteps.as_view(), name="experimentsteps_choose"),
    url(r'^step/files$', experiments_manager.views.FileListForStep.as_view(), name="file_list_for_step"),
    url(r'^next-step/(?P<experiment_id>\d+)$', experiments_manager.views.complete_step_and_go_to_next, name="complete_step_and_go_to_next"),
    url(r'^edit/(?P<experiment_id>\d+)$', login_required(experiments_manager.views.ExperimentCreateView.as_view()), name="experiment_edit"),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)$', login_required(experiments_manager.views.ExperimentDetailView.as_view()), name='experiment_detail'),
    url(r'^file/(?P<experiment_id>\d+)/$', login_required(experiments_manager.views.FileViewGitRepository.as_view()), name='file_detail'),
    url(r'^readme/(?P<experiment_id>\d+)/$', experiments_manager.views.readme_of_experiment, name='readme_view'),
    url(r'^score-card/(?P<pk>\d+)/(?P<slug>[-\w]+)$', experiments_manager.views.experimentstep_scorecard,
        name='experimentstep_scorecard'),

]
