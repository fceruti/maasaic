"""maasaic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import sys

from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path

from maasaic.apps.content.views.app import CellContentUpdateView
from maasaic.apps.content.views.app import CellCreateView
from maasaic.apps.content.views.app import CellDeleteView
from maasaic.apps.content.views.app import CellOrderUpdateView
from maasaic.apps.content.views.app import CellPositionUpdateView
from maasaic.apps.content.views.app import CellVisibilityUpdateView
from maasaic.apps.content.views.app import ImageCreateView
from maasaic.apps.content.views.app import PageConfigView
from maasaic.apps.content.views.app import PageCreateView
from maasaic.apps.content.views.app import PageDeleteView
from maasaic.apps.content.views.app import PageListView
from maasaic.apps.content.views.app import PagePublishView
from maasaic.apps.content.views.app import PageResetView
from maasaic.apps.content.views.app import PageUpdateView
from maasaic.apps.content.views.app import SectionCreateView
from maasaic.apps.content.views.app import SectionDeleteView
from maasaic.apps.content.views.app import SectionOrderUpdateView
from maasaic.apps.content.views.app import SectionUpdateView
from maasaic.apps.content.views.app import SectionVisibilityUpdateView
from maasaic.apps.content.views.app import WebsiteConfigView
from maasaic.apps.content.views.app import WebsiteCreateView
from maasaic.apps.content.views.app import WebsiteGalleryView
from maasaic.apps.content.views.app import WebsiteDetailView
from maasaic.apps.content.views.app import WebsiteListView
from maasaic.apps.content.views.app import WebsitePageDefaultsView
from maasaic.apps.content.views.app import WebsitePublishView
from maasaic.apps.content.views.frontend import HomeView
from maasaic.apps.content.views.frontend import UserCreateView
from maasaic.apps.content.views.frontend import UserLoginView
from maasaic.apps.content.views.frontend import UserLogoutView

cells_urls = [
    path('/create', CellCreateView.as_view(), name='cell_create'),
    path('/<int:pk>/move', CellPositionUpdateView.as_view(), name='cell_update_move'),
    path('/<int:pk>/visibility', CellVisibilityUpdateView.as_view(), name='cell_update_visibility'),
    path('/<int:pk>/order', CellOrderUpdateView.as_view(), name='cell_update_order'),
    path('/<int:pk>/delete', CellDeleteView.as_view(), name='cell_delete'),
    path('/<int:pk>/update', CellContentUpdateView.as_view(), name='cell_update'),
]

sections_urls = [
    path('/create', SectionCreateView.as_view(), name='section_create'),
    path('/<int:pk>/update', SectionUpdateView.as_view(), name='section_update'),
    path('/<int:pk>/delete', SectionDeleteView.as_view(), name='section_delete'),
    path('/<int:pk>/visibility', SectionVisibilityUpdateView.as_view(), name='section_update_visibility'),
    path('/<int:pk>/order', SectionOrderUpdateView.as_view(), name='section_update_order'),
]

pages_urls = [
    path('', PageListView.as_view(), name='page_list'),
    path('/create', PageCreateView.as_view(), name='page_create'),
    path('/<int:pk>/config', PageConfigView.as_view(), name='page_config'),
    path('/<int:pk>/update', PageUpdateView.as_view(), name='page_update'),
    path('/<int:pk>/delete', PageDeleteView.as_view(), name='page_delete'),
    path('/<int:pk>/publish', PagePublishView.as_view(), name='page_publish'),
    path('/<int:pk>/reset', PageResetView.as_view(), name='page_reset'),
]

sites_urls = [
    path('', WebsiteListView.as_view(), name='website_list'),
    path('/create', WebsiteCreateView.as_view(), name='website_create'),
    path('/<str:subdomain>', WebsiteDetailView.as_view(), name='website_detail'),
    path('/<str:subdomain>/gallery', WebsiteGalleryView.as_view(), name='website_gallery'),
    path('/<str:subdomain>/config', WebsiteConfigView.as_view(), name='website_config'),
    path('/<str:subdomain>/defaults', WebsitePageDefaultsView.as_view(), name='website_defaults'),
    path('/<str:subdomain>/publish', WebsitePublishView.as_view(), name='website_publish'),
    path('/<str:subdomain>/images', ImageCreateView.as_view(), name='image_create'),

    path('/<str:subdomain>/pages', include(pages_urls)),
]


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('join', UserCreateView.as_view(), name='user_create'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),

    path('sites', include(sites_urls)),
    path('sections', include(sections_urls)),
    path('cells', include(cells_urls)),

    path('admin', admin.site.urls),
    path('nested_admin', include('nested_admin.urls')),
]

if settings.DEBUG:
    base_urls = sys.modules[settings.ROOT_URLCONF].urlpatterns
    urlpatterns += base_urls
