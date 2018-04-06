from django.urls import include
from django.urls import path
from django.urls import re_path

from maasaic.apps.content.views.app import CellVisibilityUpdateView
from maasaic.apps.content.views.app import PageView
from maasaic.apps.content.views.app import SectionVisibilityUpdateView

section_urls = [
    path('visibility',
         SectionVisibilityUpdateView.as_view(),
         name='section_visibility_update'),
]

cells_urls = [
    path('visibility',
         CellVisibilityUpdateView.as_view(),
         name='cell_visibility_update'),
]

urlpatterns = [
    path('sections/<int:section_pk>/', include(section_urls)),
    path('cells/<int:cell_pk>/', include(cells_urls)),
    re_path('(?P<url>.*)', PageView.as_view(), name='page'),
]
