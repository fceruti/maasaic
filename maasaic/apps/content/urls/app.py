from django.urls import include
from django.urls import path
from django.urls import re_path

from maasaic.apps.content.views.app import CellVisibilityUpdateView
from maasaic.apps.content.views.app import PageView
from maasaic.apps.content.views.app import SectionVisibilityUpdateView

urlpatterns = [
    re_path('(?P<url>.*)', PageView.as_view(), name='page'),
]
