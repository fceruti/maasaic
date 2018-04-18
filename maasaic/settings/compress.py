from maasaic.settings.common import *


# ------------------------------------------------------------------------------
# Static files
# ------------------------------------------------------------------------------
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = ASSETS_PATH
COMPRESS_FILTERS = {
    'css': ['compressor.filters.css_default.CssAbsoluteFilter'],
    'js': ['compressor.filters.jsmin.JSMinFilter']
}
