import sys

from django.conf import settings
from django.urls import re_path

from maasaic.apps.content.views.page import PageView

base_urls = sys.modules[settings.ROOT_URLCONF].urlpatterns

urlpatterns = [
    re_path('(?P<url>.*)', PageView.as_view(), name='page'),
] + base_urls
