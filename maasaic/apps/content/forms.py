import re

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction

from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import MAX_ROWS_KEY
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import SASS_VARIABLES
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import UploadedImage
from maasaic.apps.content.models import Website
from maasaic.apps.content.utils import get_margin_string_from_position
from maasaic.apps.content.utils import get_position_dict_from_margin
from maasaic.apps.users.models import User

path_pattern = re.compile('^([/\w+-.]*)$')


class UserLoginForm(forms.Form):
    subdomain = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        subdomain = self.cleaned_data.get('subdomain')
        password = self.cleaned_data.get('password')

        if not subdomain:
            raise forms.ValidationError('Please enter a subdomain')
        if not password:
            raise forms.ValidationError('Please enter a valid username')

        try:
            website = Website.objects.get(subdomain=subdomain)
        except Website.DoesNotExist:
            err = 'Theres no website with a subdomain of "%s".' % subdomain
            raise forms.ValidationError(err)

        username = website.user.username
        self.user_cache = authenticate(self.request,
                                       username=username,
                                       password=password)
        if self.user_cache is None:
            err = 'Wrong subdomain or password'
            raise forms.ValidationError(err)

    def get_user(self):
        return self.user_cache


class UserCreateForm(forms.Form):
    HELP_TEXTS = {
        'SUBDOMAIN': 'This will be the url to your website. '
                     'Also your login nickname,',
        'EMAIL': 'Optional. We don\'t really care about sending you emails. '
                 'It\'s just in case you forget your password. If you don\'t '
                 'put one and you loose it. You are screwed. Well, '
                 'not really, life goes on, it\'s just that you just won\'t '
                 'be able to edit your site anymore.',
        'PASSWORD': 'Try not to put something like "asdf" and then compain '
                    'about getting "hacked".'
    }

    subdomain = forms.CharField(max_length=255,
                                help_text=HELP_TEXTS['SUBDOMAIN'])
    name = forms.CharField(max_length=255, label='Site name')
    email = forms.EmailField(required=False, help_text=HELP_TEXTS['EMAIL'])
    password = forms.CharField(max_length=255, widget=forms.PasswordInput,
                               help_text=HELP_TEXTS['PASSWORD'])

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
            User.objects.get(username=subdomain)
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
                username=subdomain,
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
        fields = ['subdomain', 'name', 'description', 'language', 'favicon',
                  'favicon_cropping']

    def __init__(self, *args, **kwargs):
        super(WebsiteConfigForm, self).__init__(*args, **kwargs)
        self.fields['subdomain'].widget.attrs['readonly'] = True


class WebsitePublishForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['is_visible']


class PageCreateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'path', 'width', 'description']

    def __init__(self, website, *args, **kwargs):
        self.website = website
        super(PageCreateForm, self).__init__(*args, **kwargs)
        self.fields['path'].help_text = \
            'Url to this page. If you put "weird", then %s/weird will link ' \
            'to this page. Leave empty for root.' % website.public_url
        self.fields['title'].help_text = \
            'This will be shown in the tab when a user visits, on google ' \
            'search results and social media shares.'
        self.fields['description'].help_text = \
            'The same as with title, this is shown on search results and ' \
            'social media shares.'
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
        if path and path != '/':
            if path[0] == '/':
                path = path[1:]
            if path and path[-1] == '/':
                path = path[:-1]
            if path and path == '':
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
        if path and path != '/':
            if path[0] == '/':
                path = path[1:]
            if path and path[-1] == '/':
                path = path[:-1]
            if path and path == '':
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


class PagePublishForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['is_visible']


class PageResetForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = []


class SectionCreateForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['page', 'n_columns', 'n_rows', 'name',
                  'html_id']

        help_texts = {
            'n_rows': 'Measured in cells. You can always change this '
                      'number in the future.',
            'name': 'Mainly for you to recognize this section.',
            'html_id': 'Optional, useful when you want to create inside links.'
        }
        labels = {
            'n_columns': '# of columns',
            'n_rows': '# of rows',
        }

    def __init__(self, page, *args, **kwargs):
        super(SectionCreateForm, self).__init__(*args, **kwargs)
        self.fields['page'].initial = page
        self.fields['page'].widget = forms.HiddenInput()
        self.fields['n_rows'].initial = '5'
        max_cols = SASS_VARIABLES[MAX_ROWS_KEY]
        self.fields['n_columns'].help_text = \
            'Measured in cells. Must be a number between 1 and %s. Please' \
            ' note that you cannot change this value in the future.' % max_cols,


class SectionVisibilityForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['is_visible']


class SectionOrderForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['order']

    def save(self, commit=True):
        section = super(SectionOrderForm, self).save(commit=False)
        from_order = Section.objects.get(pk=section.pk).order
        to_order = section.order

        section.save()

        if from_order < to_order:
            other_sections = Section.objects \
                .filter(page=section.page) \
                .filter(order__gte=from_order) \
                .filter(order__lte=to_order) \
                .exclude(pk=section.pk)
            for other_section in other_sections:
                other_section.order -= 1
                other_section.save()
        else:
            other_sections = Section.objects \
                .filter(page=section.page) \
                .filter(order__lte=from_order) \
                .filter(order__gte=to_order) \
                .exclude(pk=section.pk)
            for other_section in other_sections:
                other_section.order += 1
                other_section.save()
        return section


# ------------------------------------------------------------------------------
# Cell forms
# ------------------------------------------------------------------------------
class CellCreateForm(forms.ModelForm):
    css_padding = forms.CharField(required=False)
    css_margin = forms.CharField(required=False)
    css_background = forms.CharField(required=False)
    css_border = forms.CharField(required=False)
    css_border_radius = forms.CharField(required=False)
    css_shadow = forms.CharField(required=False)

    class Meta:
        model = Cell
        fields = ['section', 'cell_type', 'x', 'y', 'w', 'h', 'content']

    def clean_padding(self):
        pos = get_position_dict_from_margin(self.cleaned_data['css_padding'])
        return get_margin_string_from_position(pos)

    def clean_margin(self):
        pos = get_position_dict_from_margin(self.cleaned_data['css_margin'])
        return get_margin_string_from_position(pos)

    # TODO: clean_css_background

    def get_css(self):
        return {
            'padding': self.cleaned_data['css_padding'],
            'background': self.cleaned_data['css_background'],
            'margin': self.cleaned_data['css_margin'],
            'border': self.cleaned_data['css_border'],
            'border_radius': self.cleaned_data['css_border_radius'],
            'box_shadow': self.cleaned_data['css_shadow'],
        }

    def save(self, commit=True):
        cell = super(CellCreateForm, self).save(commit=False)
        cell.css = self.get_css()
        cell.order = 0
        for other_cell in Cell.objects.filter(section=cell.section):
            other_cell.order += 1
            other_cell.save()
        cell.save()
        return cell


class CellUpdateContentForm(CellCreateForm):
    class Meta:
        model = Cell
        fields = ['content']

    def save(self, commit=True):
        cell = super(CellCreateForm, self).save(commit=False)
        cell.css = self.get_css()
        cell.save()
        return cell


class CellPositionForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['x', 'y']


class CellVisibilityForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['is_visible']


class CellOrderForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['order']

    def save(self, commit=True):
        cell = super(CellOrderForm, self).save(commit=False)
        from_order = Cell.objects.get(pk=cell.pk).order
        to_order = cell.order

        cell.save()

        if from_order < to_order:
            other_cells = Cell.objects \
                .filter(section=cell.section) \
                .filter(order__gte=from_order) \
                .filter(order__lte=to_order) \
                .exclude(pk=cell.pk)
            for other_cell in other_cells:
                other_cell.order -= 1
                other_cell.save()
        else:
            other_cells = Cell.objects \
                .filter(section=cell.section) \
                .filter(order__lte=from_order) \
                .filter(order__gte=to_order) \
                .exclude(pk=cell.pk)
            for other_cell in other_cells:
                other_cell.order += 1
                other_cell.save()

        return cell


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'name', 'description']
