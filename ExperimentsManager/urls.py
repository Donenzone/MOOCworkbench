from django.conf.urls import url
import ExperimentsManager.views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', ExperimentsManager.views.index, name="experiments_index"),
    url(r'^new$', login_required(ExperimentsManager.views.ExperimentCreateView.as_view()), name="new_experiment"),
    url(r'^steps/(?P<experiment_id>\d+)$', ExperimentsManager.views.ChooseExperimentSteps.as_view(), name="choose_experiment_steps"),
    url(r'^step/files$', ExperimentsManager.views.get_file_list_for_step, name="get_file_list_for_step"),
    url(r'^next-step/(?P<experiment_id>\d+)$', ExperimentsManager.views.complete_step_and_go_to_next, name="complete_step_and_go_to_next"),
    url(r'^edit/(?P<experiment_id>\d+)$', login_required(ExperimentsManager.views.ExperimentCreateView.as_view()), name="edit_experiment"),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)$', login_required(ExperimentsManager.views.ExperimentDetailView.as_view()), name='experiment_detail'),
    url(r'^file/(?P<experiment_id>\d+)/$', ExperimentsManager.views.view_file_in_git_repository, name='file_detail'),
    url(r'^readme/(?P<experiment_id>\d+)/$', ExperimentsManager.views.readme_of_experiment, name='view_readme'),
    url(r'^folder/(?P<pk>\d+)/$', ExperimentsManager.views.view_list_files_in_repo_folder, name='folder_detail'),
]
