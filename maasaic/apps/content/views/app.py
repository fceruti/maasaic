from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import Resolver404
from django.urls import resolve
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from maasaic.apps.content.forms import CellVisibilityForm
from maasaic.apps.content.forms import SectionVisibilityForm
from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import Website

FONTS = [
    ["Roboto", "'Roboto', sans-serif"],
    ["Open Sanas", "'Open Sans', sans-serif"],
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
FONTS_URL = "https://fonts.googleapis.com/css?family=Amatic+SC|Cinzel|Covered+By+Your+Grace|Faster+One|IBM+Plex+Serif|Love+Ya+Like+A+Sister|Merriweather|Mina|Montserrat|Nanum+Brush+Script|Open+Sans|Oswald|Permanent+Marker|Poiret+One|Raleway|Rammetto+One|Roboto|Rock+Salt|Shadows+Into+Light+Two|Slabo+27px"

from maasaic.apps.content.utils import resolve_url
from django.http import HttpResponseRedirect
from django.http import Http404
from django.contrib import messages
from maasaic.apps.content.urls import frontend as frontend_urls


class BaseVaiew(View):
    website = None

    def dispatch(self, request, *args, **kwargs):
        path = request.get_full_path()
        host_name = request.META.get('HTTP_HOST') or \
                    request.META.get('SERVER_NAME')
        pieces = host_name.split('.')
        domain = '.'.join(pieces[-2:])
        subdomain = '.'.join(pieces[:-2])

        default_domain = settings.DEFAULT_SITE_DOMAIN
        if domain == default_domain:
            if subdomain in ['', 'www']:
                try:
                    resolve(path, frontend_urls)
                except Resolver404:
                    raise Http404
            else:
                try:
                    self.website = Website.objects.get(slug=subdomain)
                except Website.DoesNotExist:
                    msg = 'The web domain "%s.%s" is available. ' \
                          'Create your own amazing website now!' \
                          % (subdomain, default_domain)
                    messages.success(request, msg)
                    url = resolve_url(name='welcome') + '?subdomain=%s' % subdomain
                    return HttpResponseRedirect(url)
        else:
            try:
                self.website = Website.objects.get(private_domain=host_name)
            except Website.DoesNotExist:
                msg = 'Sorry it we don\'t handle the website %s' % domain
                messages.error(request, msg)
                url = resolve_url(name='welcome')
                return HttpResponseRedirect(url)
        super(self, BaseView).dispatch(request, *args, **kwargs)


class BaseView(View):

    @cached_property
    def website(self):
        if self.request.domain == settings.DEFAULT_SITE_DOMAIN:
            web = get_object_or_404(Website, subdomain=self.request.subdomain)
        else:
            web = get_object_or_404(Website, private_domain=self.request.domain)
        return web


class PageView(TemplateView, BaseView):
    template_name = 'app/page.html'

    @cached_property
    def pages(self):
        return self.website.page_set.all()

    @cached_property
    def page(self):
        return get_object_or_404(Page,
                                 website=self.website,
                                 path=self.kwargs['url'])

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


class SectionVisibilityUpdateView(UpdateView):
    form_class = SectionVisibilityForm
    http_method_names = ['post']

    def get_object(self, queryset=None):
        section = get_object_or_404(Section, pk=self.kwargs['section_pk'])
        return section

    def get_success_url(self):
        section = self.get_object()
        url = section.page.absolute_path + '?edit=on'
        return url

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(redirect_to=self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(redirect_to=self.get_success_url())


class CellVisibilityUpdateView(UpdateView):
    form_class = CellVisibilityForm
    http_method_names = ['post']

    def get_object(self, queryset=None):
        return get_object_or_404(Cell, pk=self.kwargs['cell_pk'])

    def get_success_url(self):
        cell = self.get_object()
        url = cell.section.page.absolute_path + '?edit=on'
        return url

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(redirect_to=self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(redirect_to=self.get_success_url())
