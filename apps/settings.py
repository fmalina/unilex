VERSION = '1.0'

import os.path
PWD = os.path.dirname(os.path.realpath(__file__ ))
PROJECT_ROOT = PWD.replace('apps', '')

from settings_local import *

TEMPLATE_DEBUG = DEBUG
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
MEDIA_ROOT  = PROJECT_ROOT+'media/'
STATIC_ROOT = PROJECT_ROOT+'static/'
MEDIA_URL = '/'
ADMIN_MEDIA_PREFIX = '/admin/'
ACCOUNT_ACTIVATION_DAYS = 2
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/'

from django.utils.log import DEFAULT_LOGGING as LOGGING
LOGGING['handlers']['mail_admins']['include_html'] = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'paging.PagingMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = [
   PWD + '/templates/',
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'content',
    'vocabulary',
    'tag',
    'registration',
    'feedback',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    "vocabulary.context_processors.current_site",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
]
