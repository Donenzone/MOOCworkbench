"""
Django settings for MOOCworkbench project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from os.path import dirname, abspath, basename, normpath, join

from .production_settings import ALLOWED_HOSTS, SECRET_KEY, DEBUG, GITHUB_WEBHOOK_KEY
from .production_settings import EMAIL_BACKEND, EMAIL_HOST, EMAIL_HOST_PASSWORD,\
    EMAIL_HOST_USER,EMAIL_PORT,\
    EMAIL_USE_TLS, DEFAULT_FROM_EMAIL

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."),
)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
        "ROUTING": "MOOCworkbench.routing.channel_routing",
    },
}

# Application definition
SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'channels',
    'bootstrap3',
    'rest_framework',

    'experiments_manager',
    'git_manager',
    'user_manager',
    'marketplace',
    'requirements_manager',
    'quality_manager',
    'build_manager',
    'feedback',
    'docs_manager',
    'coverage_manager',
    'cookiecutter_manager',
    'pylint_manager',
    'dataschema_manager',

    'bootstrapform',
    'django_tables2',
    'markdownx',
    'notifications',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.bitbucket',
    'allauth.socialaccount.providers.dropbox',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.gitlab',

    'django_bootstrap_breadcrumbs',
    'autoadmin'
]

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'feedback.middleware.MiddlewareTaskCompleted',
]

ROOT_URLCONF = 'MOOCworkbench.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'user_manager.context_processor.workbench_user',
                'feedback.context_processor.active_task',
                'django.template.context_processors.request'
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGE_SIZE': 10
}

WSGI_APPLICATION = 'MOOCworkbench.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_ROOT = '{0}/static'.format(PROJECT_ROOT)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
    os.path.join(BASE_DIR, "bower_components"),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'build_manager': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
        },
        'cookiecutter_manager': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
        },
        'coverage_manager': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
        },
        'dataschema_manager': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
        },
        'user_manager': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
        },
    },
}

LOGIN_REDIRECT_URL = '/'
