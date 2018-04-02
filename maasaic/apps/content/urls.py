from django.urls import include
from django.urls import path

from maasaic.apps.content.views import SectionVisibilityUpdateView

section_urls = [
    path('visibility',
         SectionVisibilityUpdateView.as_view(),
         name='section_visibility_update'),
]

urlpatterns = [
    path('sections/<int:section_pk>/', include(section_urls)),
]
