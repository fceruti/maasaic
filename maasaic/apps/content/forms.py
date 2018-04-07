from django import forms
from django.conf import settings
from django.db import transaction

from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import Website
from maasaic.apps.content.models import Page
from maasaic.apps.users.models import User
from image_cropping import ImageCropWidget

import re

path_pattern = re.compile('^([/\w+-.]*)$')


class UserLoginForm(forms.Form):
    subdomain = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)


class UserCreateForm(forms.Form):
    subdomain = forms.CharField(max_length=255, help_text='This will be the url to your website. Also your login nickname,')
    name = forms.CharField(max_length=255)
    email = forms.EmailField(required=False, help_text='Optional. We don\'t really care about sending you emails. It\'s just in case you forget your password. If you don\'t put one and you loose it. You are screwed. Well, not really, life goes on, it\'s just that you just won\'t be able to edit your site anymore.')
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, help_text='Try not to put something like "asdf" and then compaint about getting "hacked".')

    def clean_subdomain(self):
        subdomain = self.cleaned_data['subdomain'].lower()
        try:
            Website.objects.get(subdomain=self.cleaned_data['subdomain'])
            msg = 'The domain %s.%s has already been taken. Try another one.' \
                  % (subdomain, settings.DEFAULT_SITE_DOMAIN)
            raise forms.ValidationError(msg)
        except Website.DoesNotExist:
            pass
        try:
            User.objects.get(nickname=subdomain)
            msg = 'The domain %s.%s has already been taken. Try another one.' \
                  % (subdomain, settings.DEFAULT_SITE_DOMAIN)
            raise forms.ValidationError(msg)
        except User.DoesNotExist:
            pass
        return subdomain

    def clean_email(self):
        if self.cleaned_data['email']:
            return self.cleaned_data['email']
        return None

    def save(self, commit=True):
        subdomain = self.cleaned_data['subdomain']
        with transaction.atomic():
            user = User.objects.create_user(
                nickname=subdomain,
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'])
            website = Website.objects.create(
                user=user,
                subdomain=subdomain,
                name=self.cleaned_data['name'])
        return website


class WebsiteCreateForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['subdomain',
                  'name',
                  'description',
                  'favicon']

        help_texts = {
            'subdomain': 'This will be the first part of your url: '
                         'example.maasaic.com',
            'name': 'The name used to show the page internally and also '
                    'gives title to pages that have none.',
            'description': 'This will help us showcase your website to other '
                           'users and search engines.',
            'favicon': 'This is the tiny image users will see on their tabs '
                       'when they go to your site',
        }

    def clean_subdomain(self):
        return self.cleaned_data['subdomain'].lower()

    def __init__(self, *args, **kwargs):
        super(WebsiteCreateForm, self).__init__(*args, **kwargs)
        self.fields['favicon'].required = False
        self.fields['description'].widget.attrs['rows'] = 3


class WebsiteConfigForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['subdomain', 'name', 'description', 'language', 'favicon', 'favicon_cropping']

    def __init__(self, *args, **kwargs):
        super(WebsiteConfigForm, self).__init__(*args, **kwargs)
        self.fields['subdomain'].widget.attrs['readonly'] = True


class PageCreateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'path', 'description']

    def __init__(self, website, *args, **kwargs):
        self.website = website
        super(PageCreateForm, self).__init__(*args, **kwargs)
        self.fields['path'].help_text = 'Url to this page. If you put "weird", then %s/weird will link to this page. Leave empty for root.' % website.public_url
        self.fields['title'].help_text = 'This will be shown in the tab when a user visits, on google search results and social media shares.'
        self.fields['description'].help_text = 'The same as with title, this is shown on search results and social media shares.'
        self.fields['description'].widget.attrs['rows'] = 3

    def save(self, commit=True):
        with transaction.atomic():
            path = self.cleaned_data['path']
            live_page = Page.objects.create(
                website=self.website,
                is_visible=False,
                mode=Page.Mode.LIVE,
                title=self.cleaned_data['title'],
                path=path,
                description=self.cleaned_data['description'])
            Page.objects.create(
                website=self.website,
                is_visible=False,
                target_page=live_page,
                mode=Page.Mode.EDIT,
                title=self.cleaned_data['title'],
                path=path,
                description=self.cleaned_data['description'])
        return live_page

    def clean_path(self):
        path = self.cleaned_data['path']
        if path:
            if path[0] == '/':
                path = path[1:]
            if path[-1] == '/':
                path = path[:-1]
            if path == '':
                path = '/'
        else:
            path = '/'
        if not path_pattern.match(path):
            err_msg = 'Please create a valid path with the following ' \
                      'characters: a-z, A-Z, 0-9, /, -, _.'
            raise forms.ValidationError(err_msg)
        try:
            Page.objects.get(website=self.website,
                             path=path,
                             mode=Page.Mode.LIVE)
            err_msg = 'The path "%s" is already in use for this page' % path
            raise forms.ValidationError(err_msg)
        except Page.DoesNotExist:
            return path


class PageUpdateForm(PageCreateForm):

    def save(self, commit=True):
        assert self.instance.mode == Page.Mode.LIVE
        with transaction.atomic():
            live_page = self.instance
            live_page.title = self.cleaned_data['title']
            live_page.path = self.cleaned_data['path']
            live_page.description = self.cleaned_data['description']
            live_page.save()

            edit_page = self.instance.edit_page
            edit_page.title = self.cleaned_data['title']
            edit_page.path = self.cleaned_data['path']
            edit_page.description = self.cleaned_data['description']
            edit_page.save()
        return live_page

    def clean_path(self):
        path = self.cleaned_data['path']
        if path:
            if path[0] == '/':
                path = path[1:]
            if path[-1] == '/':
                path = path[:-1]
            if path == '':
                path = '/'
        else:
            path = '/'
        if not path_pattern.match(path):
            err_msg = 'Please create a valid path with the following ' \
                      'characters: a-z, A-Z, 0-9, /, -, _.'
            raise forms.ValidationError(err_msg)
        n_pages = Page.objects \
            .filter(website=self.website) \
            .filter(path=path).filter(mode=Page.Mode.LIVE) \
            .exclude(pk=self.instance.pk)\
            .count()
        if n_pages > 0:
            err_msg = 'The path "%s" is already in use for this page' % path
            raise forms.ValidationError(err_msg)
        return path


class SectionVisibilityForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['is_visible']


class CellVisibilityForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['is_visible']
