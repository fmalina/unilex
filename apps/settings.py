VERSION = '1.1'

import os.path
PWD = os.path.dirname(os.path.realpath(__file__ ))
PROJECT_ROOT = PWD.replace('apps', '')

from settings_local import *

INTERNAL_IPS = ['127.0.0.1']
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
MEDIA_ROOT  = PROJECT_ROOT+'media/'
STATIC_ROOT = PROJECT_ROOT+'static/'
STATIC_URL = '/static/'
ACCOUNT_ACTIVATION_DAYS = 2
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/'

from django.utils.log import DEFAULT_LOGGING as LOGGING
LOGGING['handlers']['mail_admins']['include_html'] = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PWD + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'vocabulary.context_processors.current_site',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'paging.PagingMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'vocabulary',
    'tag',
    'pay',
    'registration',
    'feedback',
)
