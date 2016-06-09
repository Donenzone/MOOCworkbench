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
from ExperimentsManager.views import ExperimentViewSet, ScriptViewSet
from GitManager.views import GitRepositoryViewSet
import UserManager.views

router = routers.DefaultRouter()
router.register(r'experiment', ExperimentViewSet)
router.register(r'script', ScriptViewSet)
router.register(r'git-repository', GitRepositoryViewSet)
router.register(r'user', UserManager.views.UserViewset)
router.register(r'workbench-user', UserManager.views.WorkbenchUserViewset)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^accounts/login/$', UserManager.views.sign_in, name="sign_in"),
    url(r'^accounts/logout/$', UserManager.views.sign_out, name="sign_out"),
    url(r'^accounts/register/$', UserManager.views.register, name="register"),
    url(r'^$', UserManager.views.index, name="index"),
]
