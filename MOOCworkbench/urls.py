"""MOOCworkbench URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
import ExperimentsManager.views
from ExperimentsManager.views import CreateExperimentView
from GitManager.views import GitRepositoryViewSet
import UserManager.views
import GitManager.views
from WorkerManager.views import *
from Worker.views import *
from django.contrib.auth.decorators import login_required
from WorkerManager import views

router = routers.DefaultRouter()
router.register(r'experiment', ExperimentsManager.views.ExperimentViewSet)
router.register(r'script', ExperimentsManager.views.ScriptViewSet)
router.register(r'git-repository', GitRepositoryViewSet)
router.register(r'user', UserManager.views.UserViewset)
router.register(r'workbench-user', UserManager.views.WorkbenchUserViewset)
router.register(r'workers', views.WorkerViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^accounts/login/$', UserManager.views.sign_in, name="sign_in"),
    url(r'^accounts/logout/$', UserManager.views.sign_out, name="sign_out"),
    url(r'^my-account/$', UserManager.views.view_my_profile, name="view_my_profile"),
    url(r'^accounts/edit/$', UserManager.views.edit_profile, name="edit_profile"),
    url(r'^accounts/register/$', UserManager.views.register, name="register"),

    url(r'^experiments/$', ExperimentsManager.views.index, name="experiments_index"),
    url(r'^experiments/new$', CreateExperimentView.as_view(), name="new_experiment"),
    url(r'^experiments/edit/(?P<experiment_id>\d+)$', CreateExperimentView.as_view(), name="edit_experiment"),
    url(r'^experiment/(?P<pk>[-\w]+)/$', ExperimentsManager.views.ExperimentDetailView.as_view(), name='experiment_detail'),
    url(r'^experiment/run/(?P<pk>[-\w]+)/$', ExperimentsManager.views.run_experiment_view, name='run_experiment'),
    url(r'^experiment/file/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_file_in_git_repository, name='file_detail'),
    url(r'^experiment/folder/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_list_files_in_repo_folder, name='folder_detail'),

    url(r'^$', UserManager.views.index, name="index"),

    url(r'^git/$', GitManager.views.index, name="git_index"),
    url(r'^github/$', GitManager.views.authorize_github, name="authorize_github"),
    url(r'^github-callback/$', GitManager.views.callback_authorization_github, name="callback_github"),

    url(r'^worker-manager/output/$', ReceiveWorkerOutputView.as_view(), name="worker_manager_output"),

    url(r'^worker/$', WorkerIndexView.as_view(), name="worker_index"),
    url(r'^workers/$', login_required(WorkerList.as_view()), name="worker_list"),


]

