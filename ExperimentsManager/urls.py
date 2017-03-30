from django.conf.urls import url
import ExperimentsManager.views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^experiments/$', ExperimentsManager.views.index, name="experiments_index"),
    url(r'^experiments/new$', login_required(ExperimentsManager.views.CreateExperimentView.as_view()), name="new_experiment"),
    url(r'^experiments/steps/(?P<experiment_id>\d+)$', ExperimentsManager.views.ChooseExperimentSteps.as_view(), name="choose_experiment_steps"),
    url(r'^experiment/step/files$', ExperimentsManager.views.get_git_list_for_step, name="get_git_list_for_step"),
    url(r'^experiments/next-step/(?P<experiment_id>\d+)$', ExperimentsManager.views.complete_step_and_go_to_next, name="complete_step_and_go_to_next"),
    url(r'^experiments/edit/(?P<experiment_id>\d+)$', login_required(ExperimentsManager.views.CreateExperimentView.as_view()), name="edit_experiment"),
    url(r'^experiment/(?P<pk>[-\w]+)/$', login_required(ExperimentsManager.views.ExperimentDetailView.as_view()), name='experiment_detail'),
    url(r'^experiment/run/(?P<pk>[-\w]+)/$', ExperimentsManager.views.run_experiment_view, name='run_experiment'),
    url(r'^experiment/file/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_file_in_git_repository, name='file_detail'),
    url(r'^experiment/folder/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_list_files_in_repo_folder, name='folder_detail'),


]
