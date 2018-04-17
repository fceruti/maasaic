from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from maasaic.apps.content.forms import UserCreateForm
from maasaic.apps.content.forms import UserLoginForm


# ------------------------------------------------------------------------------
# Home
# ------------------------------------------------------------------------------
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

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kw = super(UserLoginView, self).get_form_kwargs()
        kw['request'] = self.request,
        return kw

    def get_success_url(self):
        return reverse('website_list')


class UserLogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return reverse('home')
