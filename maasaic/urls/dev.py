import debug_toolbar
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

from maasaic.urls.common import urlpatterns

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path(r'__debug__/', include(debug_toolbar.urls)),
    path('favicon.ico', favicon_view),
] + urlpatterns
