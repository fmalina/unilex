from unilex.settings_local import *
from medd.db_router import MEDD_APPS
import os.path

VERSION = '1.2'

PWD = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = PWD.replace('unilex/unilex', 'unilex')

INTERNAL_IPS = ['127.0.0.1']
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_NAME = 'Unilexicon'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
MEDIA_ROOT = PROJECT_ROOT+'media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/')
STATIC_URL = '/static/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
AUTHENTICATION_BACKENDS = ['allauth.account.auth_backends.AuthenticationBackend']
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile'
TEMPLATE_DIR = f'{PWD}/templates/'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'unilex.vocabulary.context_processors.current_site',
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
    'unilex.paging.paging_middleware',
    'medd.browse.middleware.SiteMiddleware',
]

ROOT_URLCONF = 'unilex.urls'
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

    'unilex.vocabulary',
    'unilex.tag',
    'unilex.feedback',
    'pay',

    'reversion',
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.microsoft',
] + MEDD_APPS
