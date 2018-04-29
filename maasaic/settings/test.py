from maasaic.settings.common import *

DEBUG = False
TEMPLATE_DEBUG = False

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'test_db'
#     }
# }
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_SITE_DOMAIN = 'testserver'
