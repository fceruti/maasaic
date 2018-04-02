from django.views.generic import TemplateView
from django.views.generic import FormView

from maasaic.apps.content.models import Website
from maasaic.apps.content.models import Page
from maasaic.apps.content.forms import SectionVisibilityForm
from maasaic.apps.content.models import Section
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages


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


class PageView(TemplateView):
    template_name = 'page.html'

    @property
    def website(self):
        return Website.objects.get()

    @property
    def tree(self):
        parts = self.kwargs['url'].split('/')
        pages = []
        parent_page = None
        for index, part in enumerate(parts):
            if part == '':
                part = '/'
            page = Page.objects.get(parent_page=parent_page,
                                    slug=part)
            parent_page = page
            pages.append(page)
        return pages

    @property
    def page(self):
        return self.tree[-1]

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)

        context['FONTS'] = FONTS
        context['FONTS_URL'] = FONTS_URL
        context['website'] = self.website
        context['tree'] = self.tree
        context['page'] = self.page
        context['user'] = self.request.user
        if self.request.user == self.website.user:
            context['page_edit_on'] = 'edit' in self.request.GET
            context['user_is_owner'] = True
        else:
            context['page_edit_on'] = False
            context['user_is_owner'] = True
        return context


class SectionVisibilityUpdateView(FormView):
    form_class = SectionVisibilityForm
    http_method_names = ['post']

    def get_success_url(self):
        section = get_object_or_404(Section, pk=self.kwargs['section_pk'])
        return reverse('page', args=[section.page.absolute_path])

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        url = self.get_success_url()
        return HttpResponseRedirect(redirect_to=url)

