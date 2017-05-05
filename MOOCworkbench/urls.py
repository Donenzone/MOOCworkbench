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
from django.contrib.auth.decorators import login_required

import notifications.urls

import user_manager.views
import git_manager.views

urlpatterns = [
    url(r'^$', user_manager.views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', user_manager.views.sign_in, name="sign_in"),
    url(r'^accounts/logout/$', user_manager.views.sign_out, name="sign_out"),
    url(r'^my-account/$', login_required(user_manager.views.DetailProfileView.as_view()), name="view_my_profile"),
    url(r'^accounts/edit/$', login_required(user_manager.views.EditProfileView.as_view()), name="edit_profile"),
    url(r'^accounts/register/$', user_manager.views.RegisterView.as_view(), name="register"),

    url(r'^experiments/', include('experiments_manager.urls')),
    url(r'^experiments/requirements/', include('requirements_manager.urls')),
    url(r'^marketplace/', include('marketplace.urls')),
    url(r'^builds/', include('build_manager.urls')),
    url(r'^coverage/', include('coverage_manager.urls')),
    url(r'^metrics/', include('quality_manager.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^github/', include('git_manager.urls')),
    url(r'^docs/', include('docs_manager.urls')),
    url(r'^schema/', include('dataschema_manager.urls')),

    # Installed apps URLs
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^wiki/', include('waliki.urls')),
]
