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
from ExperimentsManager.views import *
from GitManager.views import GitRepositoryViewSet
from RequirementsManager.views import *
from RequirementsManager.views import ExperimentRequirementListView, ExperimentRequirementCreateView
import UserManager.views
import GitManager.views
from WorkerManager.views import *
from Worker.views import *
from django.contrib.auth.decorators import login_required
from WorkerManager import views
from Marketplace.views import *
import notifications.urls

router = routers.DefaultRouter()
router.register(r'master/experiment-run', ExperimentsManager.views.ExperimentRunViewSet)
router.register(r'worker/experiment-run', ExperimentsManager.views.ExperimentWorkerRunViewSet)
router.register(r'git-repository', GitRepositoryViewSet)
router.register(r'user', UserManager.views.UserViewset)
router.register(r'workbench-user', UserManager.views.WorkbenchUserViewset)
router.register(r'master/workers', views.WorkerViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^accounts/login/$', UserManager.views.sign_in, name="sign_in"),
    url(r'^accounts/logout/$', UserManager.views.sign_out, name="sign_out"),
    url(r'^my-account/$', login_required(UserManager.views.DetailProfileView.as_view()), name="view_my_profile"),
    url(r'^accounts/edit/$', login_required(UserManager.views.EditProfileView.as_view()), name="edit_profile"),
    url(r'^accounts/register/$', UserManager.views.register, name="register"),

    url(r'^experiments/$', ExperimentsManager.views.index, name="experiments_index"),
    url(r'^experiments/new$', login_required(CreateExperimentView.as_view()), name="new_experiment"),
    url(r'^experiments/steps/(?P<experiment_id>\d+)$', ChooseExperimentSteps.as_view(), name="choose_experiment_steps"),

    url(r'^experiment/step/files$', get_git_list_for_step, name="get_git_list_for_step"),

    url(r'^experiments/next-step/(?P<experiment_id>\d+)$', complete_step_and_go_to_next, name="complete_step_and_go_to_next"),
    url(r'^experiments/edit/(?P<experiment_id>\d+)$', login_required(CreateExperimentView.as_view()), name="edit_experiment"),
    url(r'^experiment/(?P<pk>[-\w]+)/$', login_required(ExperimentsManager.views.ExperimentDetailView.as_view()), name='experiment_detail'),
    url(r'^experiment/run/(?P<pk>[-\w]+)/$', ExperimentsManager.views.run_experiment_view, name='run_experiment'),
    url(r'^experiment/file/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_file_in_git_repository, name='file_detail'),
    url(r'^experiment/folder/(?P<pk>[-\w]+)/$', ExperimentsManager.views.view_list_files_in_repo_folder, name='folder_detail'),

    url(r'^experiment/requirements/(?P<pk>\d+)/$', login_required(ExperimentRequirementListView.as_view()), name="experimentrequirements_list"),
    url(r'^experiment/requirements/(?P<experiment_id>\d+)/write$', write_requirements_file, name="write_requirements_file"),
    url(r'^experiment/add-requirement/(?P<experiment_id>\d+)/$', login_required(ExperimentRequirementCreateView.as_view()), name="add_experiment_requirement"),

    url(r'^$', UserManager.views.index, name="index"),

    url(r'^git/$', GitManager.views.index, name="git_index"),
    url(r'^worker-manager/output/$', ReceiveWorkerOutputView.as_view(), name="worker_manager_output"),
    url(r'^worker/$', WorkerIndexView.as_view(), name="worker_index"),
    url(r'^workers/$', login_required(WorkerList.as_view()), name="worker_list"),

    # Marketplace URLs
    url(r'^marketplace/$', login_required(MarketplaceIndex.as_view()), name="marketplace_index"),
    url(r'^marketplace/list$', login_required(PackageListView.as_view()), name="package_list"),
    url(r'^marketplace/new$', login_required(PackageCreateView.as_view(success_url='/marketplace')), name="package_new"),
    url(r'^marketplace/view/(?P<pk>[-\w]+)/$', login_required(PackageDetailView.as_view()), name="package_detail"),
    url(r'^marketplace/(?P<package_id>[-\w]+)/version/new/$', login_required(PackageVersionCreateView.as_view()), name="packageversion_new"),
    url(r'^marketplace/(?P<package_id>[-\w]+)/resource/new/$', login_required(PackageResourceCreateView.as_view()), name="packageresource_new"),
    url(r'^marketplace/subscribe/(?P<package_id>[-\w]+)/$', login_required(PackageSubscriptionView.as_view()), name="package_subscribe"),

    # Installed apps URLs
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^accounts/', include('allauth.urls')),
]
