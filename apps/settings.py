from settings_local import *
from medd.db_router import MEDD_APPS
import os.path

VERSION = '1.2'

PWD = os.path.dirname(os.path.realpath(__file__ ))
PROJECT_ROOT = PWD.replace('apps', '')

INTERNAL_IPS = ['127.0.0.1']
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_NAME = 'Unilexicon'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
MEDIA_ROOT = PROJECT_ROOT+'media/'
STATIC_ROOT = PROJECT_ROOT+'static/'
STATIC_URL = '/static/'
ACCOUNT_ACTIVATION_DAYS = 2
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{PWD}/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'vocabulary.context_processors.current_site',
                'medd.browse.context_processor.base',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    }
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'paging.paging_middleware',
    'medd.browse.middleware.SiteMiddleware',
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'urls'
CACHING = True
DATABASE_ROUTERS = ['medd.db_router.MeddDbRouter']

INSTALLED_APPS = [
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
    'feedback',

    'reversion',
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.microsoft',
] + MEDD_APPS
