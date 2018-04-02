from maasaic.settings.common import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    # 'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['localhost', '127.0.0.1']
