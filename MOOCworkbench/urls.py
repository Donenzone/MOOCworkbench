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

import notifications.urls
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView

import user_manager.views

urlpatterns = [
    url(r'^$', user_manager.views.index, name="index"),
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html'), name="login"),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(success_url_allowed_hosts='/'), name="logout"),
    url(r'^accounts/edit/$', login_required(user_manager.views.EditProfileView.as_view()), name="edit_profile"),
    url(r'^accounts/register/$', user_manager.views.RegisterView.as_view(), name="register"),
    url(r'^my-account/$', login_required(user_manager.views.DetailProfileView.as_view()), name="view_my_profile"),
    url(r'^user/(?P<username>[-\w]+)$', login_required(user_manager.views.WorkbenchUserDetailView.as_view()),
        name="view_profile"),

    url('^reset-password/$', auth_views.PasswordResetView.as_view(
        template_name='user_manager/password_reset/password_reset.html'),
        name="password_reset"),
    url('^reset-password/done$', auth_views.PasswordResetDoneView.as_view(
        template_name='user_manager/password_reset/password_reset_done.html'),
        name="password_reset_done"),
    url('^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user_manager/password_reset/password_reset_confirm.html'),
        name="password_reset_confirm"),
    url('^reset-password/complete$', auth_views.PasswordResetCompleteView.as_view(
        template_name="user_manager/password_reset/password_reset_complete.html"),
        name="password_reset_complete"),

    url(r'^search/$', user_manager.views.search, name="search"),
    url(r'^notifications/view/$', login_required(TemplateView.as_view(template_name='other/notification_index.html')), name="notification_index"),

    url(r'^experiments/', include('experiments_manager.urls')),
    url(r'^experiments/requirements/', include('requirements_manager.urls')),
    url(r'^packages/', include('marketplace.urls')),
    url(r'^builds/', include('build_manager.urls')),
    url(r'^coverage/', include('coverage_manager.urls')),
    url(r'^metrics/', include('quality_manager.urls')),
    url(r'^github/', include('git_manager.urls')),
    url(r'^docs/', include('docs_manager.urls')),
    url(r'^schema/', include('dataschema_manager.urls')),

    # Installed apps URLs
    url(r'^markdownx/', include('markdownx.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^accounts/', include('allauth.urls')),
]