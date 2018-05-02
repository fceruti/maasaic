import debug_toolbar
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from maasaic.urls.common import urlpatterns

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path(r'__debug__/', include(debug_toolbar.urls)),
    path('favicon.ico', favicon_view),
] + urlpatterns

urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
