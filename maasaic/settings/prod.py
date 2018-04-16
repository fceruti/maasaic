from maasaic.settings.common import *


DEFAULT_FILE_STORAGE = 'maasaic.apps.utils.storage_backends.S3MediaStorage'
COMPRESS_STORAGE = STATICFILES_STORAGE
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
COMPRESS_URL = STATIC_URL

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'standard': {
            'format': '[%(levelname)7s] %(asctime)s %(name)20s %(lineno)3d | %(message)s',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/var/log/django', 'info.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['log_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
