from django.urls import re_path

from maasaic.apps.content.views.app import PageView

urlpatterns = [
    re_path('(?P<url>.*)', PageView.as_view(), name='page'),
]
