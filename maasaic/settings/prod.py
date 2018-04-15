from maasaic.settings.common import *

INSTALLED_APPS += [
    'storages',
]

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = env('AWS_LOCATION')

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DEFAULT_FILE_STORAGE = 'maasaic.apps.utils.storage_backends.S3MediaStorage'
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
