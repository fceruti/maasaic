from maasaic.settings.common import *


STATICFILES_DIRS = [
    ('img', os.path.join(ASSETS_PATH, 'img')),
    ('CACHE', os.path.join(ASSETS_PATH, 'CACHE')),
    ('font-awesome', os.path.join(NODE_MODULES_PATH, 'font-awesome')),
]

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
COMPRESS_URL = STATIC_URL

STATICFILES_STORAGE = 'maasaic.apps.utils.storage_backends.CachedS3BotoStorage'
COMPRESS_STORAGE = STATICFILES_STORAGE

# ------------------------------------------------------------------------------
# collectfast
# ------------------------------------------------------------------------------
AWS_PRELOAD_METADATA = True
INSTALLED_APPS = ['collectfast',] + INSTALLED_APPS
COLLECTFAST_THREADS = 20
