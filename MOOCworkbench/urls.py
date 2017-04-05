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
from GitManager.views import GitRepositoryViewSet
import UserManager.views
import GitManager.views
from django.contrib.auth.decorators import login_required
import notifications.urls

router = routers.DefaultRouter()
router.register(r'git-repository', GitRepositoryViewSet)
router.register(r'user', UserManager.views.UserViewset)
router.register(r'workbench-user', UserManager.views.WorkbenchUserViewset)

urlpatterns = [
    url(r'^$', UserManager.views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    #url(r'^api/', include(router.urls)),
    url(r'^accounts/login/$', UserManager.views.sign_in, name="sign_in"),
    url(r'^accounts/logout/$', UserManager.views.sign_out, name="sign_out"),
    url(r'^my-account/$', login_required(UserManager.views.DetailProfileView.as_view()), name="view_my_profile"),
    url(r'^accounts/edit/$', login_required(UserManager.views.EditProfileView.as_view()), name="edit_profile"),
    url(r'^accounts/register/$', UserManager.views.register, name="register"),

    url(r'^experiments/', include('ExperimentsManager.urls')),
    url(r'^experiments/requirements/', include('RequirementsManager.urls')),
    url(r'^marketplace/', include('Marketplace.urls')),
    url(r'^builds/', include('BuildManager.urls')),
    url(r'^metrics/', include('QualityManager.urls')),
    url(r'^feedback/', include('Feedback.urls')),
    url(r'^git/$', GitManager.views.index, name="git_index"),
    url(r'^docs/', include('DocsManager.urls')),

    #url(r'^worker-manager/output/$', ReceiveWorkerOutputView.as_view(), name="worker_manager_output"),
    #url(r'^worker/$', WorkerIndexView.as_view(), name="worker_index"),
    #url(r'^workers/$', login_required(WorkerList.as_view()), name="worker_list"),

    # Installed apps URLs
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^wiki/', include('waliki.urls')),
]
