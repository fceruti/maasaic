from maasaic.settings.common import *

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
