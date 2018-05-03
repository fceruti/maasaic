from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Website


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
        context['website'] = self.website

        context['page'] = self.page
        context['user'] = self.request.user
        context['page_edit_on'] = False
        context['user_is_owner'] = False
        return context
