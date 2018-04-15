from maasaic.settings.common import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['localhost', '127.0.0.1', 'maasaic-local.com:8000', 'fceruti.maasaic-local.com:8000']

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False
