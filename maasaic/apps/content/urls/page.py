import sys

from django.conf import settings
from django.urls import re_path

from maasaic.apps.content.views.page import PageView

urlpatterns = [
    re_path('(?P<url>.*)', PageView.as_view(), name='page'),
]

if settings.DEBUG:
    base_urls = sys.modules[settings.ROOT_URLCONF].urlpatterns
    urlpatterns += base_urls
