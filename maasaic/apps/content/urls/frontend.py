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

from maasaic.apps.content.views.frontend import HomeView
from maasaic.apps.content.views.frontend import PageCreateView
from maasaic.apps.content.views.frontend import PageDeleteView
from maasaic.apps.content.views.frontend import PageListView
from maasaic.apps.content.views.frontend import PageUpdateView
from maasaic.apps.content.views.frontend import UserCreateView
from maasaic.apps.content.views.frontend import UserLoginView
from maasaic.apps.content.views.frontend import UserLogoutView
from maasaic.apps.content.views.frontend import WebsiteCellAttrView
from maasaic.apps.content.views.frontend import WebsiteConfigView
from maasaic.apps.content.views.frontend import WebsiteCreateView
from maasaic.apps.content.views.frontend import WebsiteDetailView
from maasaic.apps.content.views.frontend import WebsiteListView
from maasaic.apps.content.views.frontend import WebsitePageAttrView
from maasaic.apps.content.views.frontend import PageConfigView

base_urls = sys.modules[settings.ROOT_URLCONF].urlpatterns

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register', UserCreateView.as_view(), name='user_create'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),
    path('sites', WebsiteListView.as_view(), name='website_list'),
    path('sites/create', WebsiteCreateView.as_view(), name='website_create'),

    path('sites/<str:subdomain>', WebsiteDetailView.as_view(), name='website_detail'),
    path('sites/<str:subdomain>/pages', PageListView.as_view(), name='page_list'),
    path('sites/<str:subdomain>/pages/create', PageCreateView.as_view(), name='page_create'),
    path('sites/<str:subdomain>/pages/<int:pk>/config', PageConfigView.as_view(), name='page_config'),
    path('sites/<str:subdomain>/pages/<int:pk>/update', PageUpdateView.as_view(), name='page_update'),
    path('sites/<str:subdomain>/pages/<int:pk>/delete', PageDeleteView.as_view(), name='page_delete'),

    path('sites/<str:subdomain>/config', WebsiteConfigView.as_view(), name='website_config'),
    path('sites/<str:subdomain>/default-page-attrs', WebsitePageAttrView.as_view(), name='website_page_attr'),
    path('sites/<str:subdomain>/default-cell-attrs', WebsiteCellAttrView.as_view(), name='website_cell_attr'),
    path('admin', admin.site.urls),
    path('nested_admin', include('nested_admin.urls')),
] + base_urls
