import sentry_sdk  # NoQA
from sentry_sdk.integrations.django import DjangoIntegration  # NoQA
import os.path
import pymysql
pymysql.install_as_MySQLdb()

SECRET_KEY = os.getenv('SECRET_KEY', '12345')

DEBUG = False
VERSION = '1.4'

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

INTERNAL_IPS = ['127.0.0.1']
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_NAME = 'Unilexicon'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(STATIC_ROOT, 'assets')]
STATIC_URL = '/assets/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_RATE_LIMITS = {
    "change_password": "5/m",
    "manage_email": "10/m",
    "reset_password": "20/m",
    "reset_password_email": "5/m",
    "reset_password_from_key": "20/m",
    "signup": "20/m",
}
ACCOUNT_SIGNUP_FORM_CLASS = 'unilex.vocabulary.forms.AutoBotHoneypotSignupForm'
AUTHENTICATION_BACKENDS = ['allauth.account.auth_backends.AuthenticationBackend']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile'
TEMPLATE_DIR = os.path.join(BASE_DIR, 'unilex', 'templates')
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
] + [
    'medd.lookup',
    'medd.ingredient',
    'medd.vtm',
    'medd.vmp',
    'medd.amp',
    'medd.vmpp',
    'medd.ampp',
    'medd.gtin',
    'medd.browse',
    'medd.prescription'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unilex', 'USER': 'root', 'PASSWORD': os.getenv('DB_PASS')
    },
    'medd': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'medd', 'USER': 'root', 'PASSWORD': os.getenv('DB_PASS')
    }
}
ALLOWED_HOSTS = ['unilexicon.com']
CSRF_TRUSTED_ORIGINS = ['https://unilexicon.com']
if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1', 'unilexicon.co']
    CSRF_TRUSTED_ORIGINS += ['https://unilexicon.co']
    MY_SITE_PROTOCOL = 'http'
DEFAULT_FROM_EMAIL = 'hi@unilexicon.com'
ADMINS = MANAGERS = [('Admin', DEFAULT_FROM_EMAIL)]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    sentry_sdk.init()
else:
    SENTRY_URL = "https://2b75f709314a42a4b1e5cb8b3d616353@o315515.ingest.sentry.io/5411895"
    sentry_sdk.init(dsn=SENTRY_URL, integrations=[DjangoIntegration()])
