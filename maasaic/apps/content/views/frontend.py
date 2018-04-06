from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from maasaic.apps.content.forms import PageCreateForm
from maasaic.apps.content.forms import UserCreateForm
from maasaic.apps.content.forms import UserLoginForm
from maasaic.apps.content.forms import WebsiteConfigForm
from maasaic.apps.content.forms import WebsiteCreateForm
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Website
from maasaic.apps.content.utils import resolve_url


class HomeView(TemplateView):
    template_name = 'frontend/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['user_create_form'] = UserCreateForm()
        return context


class UserCreateView(FormView):
    template_name = 'frontend/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        website = form.save(commit=True)
        login(self.request, website.user)
        msg = 'Great! Now you can start adding some pages to your site.'
        messages.success(self.request, msg)
        url = reverse('website_detail', args=[website.subdomain])
        return HttpResponseRedirect(url)


class UserLoginView(FormView):
    template_name = 'frontend/user_login.html'
    form_class = UserLoginForm


class UserLogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return reverse('home')


class WebsiteListView(LoginRequiredMixin, ListView):
    template_name = 'frontend/website_list.html'
    context_object_name = 'websites'

    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(WebsiteListView, self).get_context_data(*args, **kwargs)
        context['website_create_form'] = WebsiteCreateForm()
        return context


class WebsiteCreateView(LoginRequiredMixin, FormView):
    template_name = 'frontend/website_create.html'
    form_class = WebsiteCreateForm

    def form_valid(self, form):
        website = form.save(commit=False)
        website.user = self.request.user
        website.save()
        msg = 'The site %s has been created. Keep it weird.' % website.domain
        messages.success(self.request, msg)
        url = reverse('website_detail', args=[website.subdomain])
        return HttpResponseRedirect(url)


class WebsiteDetailBase(LoginRequiredMixin, View):
    @cached_property
    def website(self):
        return get_object_or_404(Website, subdomain=self.kwargs['subdomain'])


class WebsiteDetailView(RedirectView, WebsiteDetailBase):
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def get_redirect_url(self, *args, **kwargs):
        return reverse('website_pages', args=[self.website.subdomain])


class WebsitePageListView(DetailView, WebsiteDetailBase):
    template_name = 'frontend/page_list.html'
    form_class = WebsiteConfigForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def get_context_data(self, **kwargs):
        context = super(WebsitePageListView, self).get_context_data(**kwargs)
        context['page_title'] = 'Pages'
        context['current_tab'] = 'pages'
        context['pages'] = Page.objects.filter(website=self.website,
                                               mode=Page.Mode.LIVE)
        context['page_create_form'] = PageCreateForm(website=self.website)
        return context


class WebsitePageCreateView(CreateView, WebsiteDetailBase):
    template_name = 'frontend/page_create.html'
    model = Page
    form_class = PageCreateForm

    def get_form_kwargs(self, *args, **kwargs):
        kw = super(WebsitePageCreateView, self).get_form_kwargs(*args, **kwargs)
        kw['website'] = self.website
        return kw

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Page created')
        url = reverse('website_pages', args=[self.website.subdomain])
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        context = super(WebsitePageCreateView, self).get_context_data(**kwargs)
        context['website'] = self.website
        context['current_tab'] = 'pages'
        return context


class WebsitePageEditView(DetailView, WebsiteDetailBase):
    template_name = 'frontend/page_edit.html'
    model = Page

    def get_context_data(self, **kwargs):
        context = super(WebsitePageEditView, self).get_context_data(**kwargs)
        context['page_edit_on'] = True
        context['website'] = self.website
        return context


class WebsitePageDeleteView(DeleteView, WebsiteDetailBase):
    model = Page

    def get_success_url(self):
        return reverse('website_pages', args=[self.website.subdomain])

    def delete(self, request, *args, **kwargs):
        response = super(WebsitePageDeleteView, self)\
            .delete(request, *args, **kwargs)
        messages.success(self.request, 'Your page has been deleted')
        return response


class WebsiteConfigView(LoginRequiredMixin, UpdateView):
    template_name = 'frontend/website_detail_config.html'
    form_class = WebsiteConfigForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def get_context_data(self, **kwargs):
        context = super(WebsiteConfigView, self).get_context_data(**kwargs)
        context['page_title'] = 'Configuration'
        context['current_tab'] = 'config'
        return context


class WebsitePageAttrView(LoginRequiredMixin, UpdateView):
    template_name = 'frontend/website_detail_page_attr.html'
    form_class = WebsiteConfigForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def get_context_data(self, **kwargs):
        context = super(WebsitePageAttrView, self).get_context_data(**kwargs)
        context['page_title'] = 'Page attributes'
        context['current_tab'] = 'page_attr'
        return context


class WebsiteCellAttrView(LoginRequiredMixin, UpdateView):
    template_name = 'frontend/website_detail_cell_attr.html'
    form_class = WebsiteConfigForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def get_context_data(self, **kwargs):
        context = super(WebsiteCellAttrView, self).get_context_data(**kwargs)
        context['page_title'] = 'Cell attributes'
        context['current_tab'] = 'cell_attr'
        return context
