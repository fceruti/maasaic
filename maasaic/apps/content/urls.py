from django.urls import include
from django.urls import path

from maasaic.apps.content.views import SectionVisibilityUpdateView
from maasaic.apps.content.views import CellVisibilityUpdateView

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
]
