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
from ExperimentsManager.views import ExperimentViewSet, ScriptViewSet, index
from GitManager.views import GitRepositoryViewSet
from UserManager.views import WorkbenchUserViewset, sign_in, UserViewset

router = routers.DefaultRouter()
router.register(r'experiment', ExperimentViewSet)
router.register(r'script', ScriptViewSet)
router.register(r'git-repository', GitRepositoryViewSet)
router.register(r'user', UserViewset)
router.register(r'workbench-user', WorkbenchUserViewset)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^sign-in/$', sign_in),
    url(r'^$', index),
]
