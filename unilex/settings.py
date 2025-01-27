import sentry_sdk  # NoQA
from sentry_sdk.integrations.django import DjangoIntegration  # NoQA
import os.path

SECRET_KEY = os.getenv('SECRET_KEY', '12345')
DEBUG = bool(int(os.getenv('UNILEX_DEBUG', '0')))
VERSION = '1.72'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_RATE_LIMITS = {
    'change_redpassword': '5/m',
    'manage_email': '10/m',
    'reset_password': '20/m',
    'reset_password_email': '5/m',
    'reset_password_from_key': '20/m',
    'signup': '20/m',
}
ACCOUNT_SIGNUP_FORM_CLASS = 'unilex.vocabulary.forms.AutoBotHoneypotSignupForm'
AUTHENTICATION_BACKENDS = ['allauth.account.auth_backends.AuthenticationBackend']
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
        },
    }
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'unilex.paging.paging_middleware',
    'medd.browse.middleware.SiteMiddleware',
    'medd.browse.middleware_static.StaticCacheMiddleware',
]

ROOT_URLCONF = 'unilex.urls'
STATIC_CACHING = not DEBUG
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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
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
    'medd.prescription',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unilex',
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
    },
    'medd': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'medd',
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
    },
}
ALLOWED_HOSTS = ['unilexicon.com', 'unilexicon.co']
CSRF_TRUSTED_ORIGINS = ['https://unilexicon.com', 'https://unilexicon.co']
if DEBUG:
    MY_SITE_PROTOCOL = 'https'
DEFAULT_FROM_EMAIL = 'hi@unilexicon.com'
ADMINS = MANAGERS = [('Admin', DEFAULT_FROM_EMAIL)]
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
PAY_PLANS = {365: ('229.00', '', '')}
if DEBUG:
    sentry_sdk.init()
else:
    SENTRY_URL = 'https://2b75f709314a42a4b1e5cb8b3d616353@o315515.ingest.sentry.io/5411895'
    sentry_sdk.init(dsn=SENTRY_URL, integrations=[DjangoIntegration()])
