from maasaic.settings.dev import *

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATICFILES_STORAGE = 'maasaic.apps.utils.storage_backends.CachedS3BotoStorage'
DEFAULT_FILE_STORAGE = 'maasaic.apps.utils.storage_backends.S3MediaStorage'
COMPRESS_STORAGE = STATICFILES_STORAGE
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
COMPRESS_URL = STATIC_URL
