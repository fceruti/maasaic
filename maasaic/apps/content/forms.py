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
from maasaic.apps.content.models import SiteDefaultProp
from maasaic.apps.content.models import SASS_VARIABLES
from maasaic.apps.content.models import MAX_COLS_KEY
from maasaic.apps.content.models import MAX_ROWS_KEY
from maasaic.apps.utils.forms import ColorWidget

path_pattern = re.compile('^([/\w+-.]*)$')


# ------------------------------------------------------------------------------
# Users
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Websites
# ------------------------------------------------------------------------------
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


site_props = {
    'n_cols': {
        'scope': SiteDefaultProp.Scope.SECTION,
        'name': 'n_cols', 'type': 'int', 'default': 5,
        'min': 1, 'max': SASS_VARIABLES[MAX_COLS_KEY],
        'label_name': '# Columns',
        'help_text': 'Measured in cells. Must be a number between 1 and %s.'
                     % SASS_VARIABLES[MAX_COLS_KEY]},
    'n_rows': {
        'scope': SiteDefaultProp.Scope.SECTION,
        'name': 'n_rows', 'type': 'int', 'default': 5,
        'min': 1, 'max': SASS_VARIABLES[MAX_ROWS_KEY],
        'label_name': '# Rows',
        'help_text': 'Measured in cells. Must be a number between 1 and %s.'
                     % SASS_VARIABLES[MAX_ROWS_KEY]},
    'sec_background': {
        'scope': SiteDefaultProp.Scope.SECTION,
        'label_name': 'Background', 'widget': ColorWidget,
        'name': 'background', 'type': 'str', 'default': '#FFFFFF'},
    'sec_padding-top': {
        'scope': SiteDefaultProp.Scope.SECTION,
        'label_name': 'Padding top',
        'name': 'padding_top', 'type': 'str', 'default': '30px'},
    'sec_padding-bottom': {
        'scope': SiteDefaultProp.Scope.SECTION,
        'label_name': 'Padding bottom',
        'name': 'padding_bottom', 'type': 'str', 'default': '30px'},

    'color': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'color', 'type': 'str', 'default': '#111111'},
    'background': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'background', 'type': 'str', 'default': '#FFFFFF'},
    'margin': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'margin', 'type': 'str', 'default': '15px'},
    'padding': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'padding', 'type': 'str', 'default': '15px'},
    'border': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'border', 'type': 'str', 'default': 'none'},
    'border_radius': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'border_radius', 'type': 'str', 'default': 'none'},
    'box_shadow': {
        'scope': SiteDefaultProp.Scope.CELL,
        'name': 'box_shadows', 'type': 'str', 'default': 'none'},
}


def get_key_for_prop(prop):
    return '%s_%s' % (prop['scope'].lower(), prop['name'])


class WebsiteDefaultsForm(forms.Form):
    def __init__(self, website, *args, **kwargs):
        self.website = website
        super(WebsiteDefaultsForm, self).__init__(*args, **kwargs)

        for prop in site_props.values():
            field_attr = {}
            try:
                section_default_prop = SiteDefaultProp.objects.get(
                    site=self.website, scope=prop['scope'], prop=prop['name'])
                field_attr['initial'] = section_default_prop.value
            except SiteDefaultProp.DoesNotExist:
                field_attr['initial'] = prop['default']
            if prop['type'] == 'int':
                field_class = forms.IntegerField
                if 'min' in prop:
                    field_attr['min_value'] = prop['min']
                if 'max' in prop:
                    field_attr['max_value'] = prop['max']
            elif prop['type'] == 'str':
                field_class = forms.CharField
            else:
                raise Exception

            self.fields[get_key_for_prop(prop)] = field_class(**field_attr)

    def save(self, commit=False):
        for prop in site_props.values():
            val = self.cleaned_data[get_key_for_prop(prop)]
            SiteDefaultProp.objects.update_or_create(site=self.website,
                                                     prop=prop['name'],
                                                     scope=prop['scope'],
                                                     defaults={'value': val})


class WebsitePublishForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['is_visible']


# ------------------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Sections
# ------------------------------------------------------------------------------
class SectionCreateForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['page', 'name', 'html_id']

        help_texts = {
            'name': 'Mainly for you to recognize this section.',
            'html_id': 'Optional, useful when you want to create inside links.'
        }

    def __init__(self, page, *args, **kwargs):
        super(SectionCreateForm, self).__init__(*args, **kwargs)
        self.fields['page'].initial = page
        self.fields['page'].widget = forms.HiddenInput()

        if not self.fields['name'].initial:
            section_n = page.section_set.count() + 1
            self.fields['name'].initial = 'Section #%s' % section_n
            self.fields['html_id'].initial = 'section_%s' % section_n

        for prop in site_props.values():
            if prop['scope'] != SiteDefaultProp.Scope.SECTION:
                continue
            field_attr = {}
            if 'label_name' in prop:
                field_attr['label'] = prop['label_name']
            if 'help_text' in prop:
                field_attr['help_text'] = prop['help_text']
            if 'widget' in prop:
                field_attr['widget'] = prop['widget']()
            try:
                section_default_prop = SiteDefaultProp.objects.get(
                    site=page.website, scope=prop['scope'], prop=prop['name'])
                field_attr['initial'] = section_default_prop.value
            except SiteDefaultProp.DoesNotExist:
                field_attr['initial'] = prop['default']
            if prop['type'] == 'int':
                field_class = forms.IntegerField
                if 'min' in prop:
                    field_attr['min_value'] = prop['min']
                if 'max' in prop:
                    field_attr['max_value'] = prop['max']
            elif prop['type'] == 'str':
                field_class = forms.CharField
            else:
                raise Exception

            self.fields[get_key_for_prop(prop)] = field_class(**field_attr)

    def get_css(self):
        return {
            'background': self.cleaned_data['section_background'],
            'padding_top': self.cleaned_data['section_padding_top'],
            'padding_bottom': self.cleaned_data['section_padding_bottom'],
        }

    def save(self, commit=True):
        section = super(SectionCreateForm, self).save(commit=False)
        section.n_rows = self.cleaned_data['section_n_rows']
        section.n_columns = self.cleaned_data['section_n_cols']
        section.css = self.get_css()
        section.save()
        return section


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
    css_background = forms.CharField(required=False, widget=ColorWidget)
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
