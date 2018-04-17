from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Website

FONTS = [
    ["Roboto", "'Roboto', sans-serif"],
    ["Open Sans", "'Open Sans', sans-serif"],
    ["Montserrat", "'Montserrat', sans-serif"],
    ["Oswald", "'Oswald', sans-serif"],
    ["Raleway", "'Raleway', sans-serif"],
    ["Mina", "'Mina', sans-serif"],
    ["Merriweather", "'Merriweather', serif"],
    ["Amatic SC", "'Amatic SC', cursive"],
    ["Permanent Marker", "'Permanent Marker', cursive"],
    ["Nanum Brush Script", "'Nanum Brush Script', cursive"],
    ["Shadows Into Light Two", "'Shadows Into Light Two', cursive"],
    ["Covered By Your Grace", "'Covered By Your Grace', cursive"],
    ["Rock Salt", "'Rock Salt', cursive"],
    ["Faster One", "'Faster One', cursive"],
    ["Rammetto One", "'Rammetto One', cursive"],
    ["Poiret One", "'Poiret One', cursive"],
    ["Love Ya Like A Sister", "'Love Ya Like A Sister', cursive"],
    ["IBM Plex Serif", "'IBM Plex Serif', serif"],
    ["Slabo 27px", "'Slabo 27px', serif"],
    ["Cinzel", "'Cinzel', serif"],
]
FONTS_URL = "https://fonts.googleapis.com/css?family=Amatic+SC|Cinzel|Covered+By+Your+Grace|Faster+One|IBM+Plex+Serif|Love+Ya+Like+A+Sister|Merriweather|Mina|Montserrat|Nanum+Brush+Script|Open+Sans|Oswald|Permanent+Marker|Poiret+One|Raleway|Rammetto+One|Roboto|Rock+Salt|Shadows+Into+Light+Two|Slabo+27px"  # noqa


class PageView(TemplateView):
    template_name = 'app/page.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.page.is_visible:
            raise Http404
        return super(PageView, self).dispatch(request, *args, **kwargs)

    @cached_property
    def website(self):
        if self.request.domain == settings.DEFAULT_SITE_DOMAIN:
            web = get_object_or_404(Website, subdomain=self.request.subdomain)
        else:
            web = get_object_or_404(Website, private_domain=self.request.domain)
        if not web.is_visible:
            raise Http404
        return web

    @cached_property
    def page(self):
        path = self.kwargs['url']
        if not path:
            path = '/'
        page = get_object_or_404(Page,
                                 website=self.website,
                                 path=path,
                                 mode=Page.Mode.LIVE)
        return page

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        context['FONTS'] = FONTS
        context['FONTS_URL'] = FONTS_URL
        context['website'] = self.website
        context['page'] = self.page
        context['user'] = self.request.user
        if self.request.user == self.website.user:
            context['page_edit_on'] = 'edit' in self.request.GET
            context['user_is_owner'] = True
        else:
            context['page_edit_on'] = False
            context['user_is_owner'] = True
        return context
