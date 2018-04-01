import os
from django.conf import settings
from urllib.parse import urljoin

from django.contrib.postgres.fields import JSONField
from django.db import models
from image_cropping import ImageCropField
from image_cropping import ImageRatioField
from django.core.validators import MinValueValidator, MaxValueValidator

from maasaic.apps.users.models import User
from maasaic.apps.utils.models import Choices

# ------------------------------------------------------------------------------
# Sass variables
# ------------------------------------------------------------------------------
MAX_COLS = 'MAX_COLS'
MAX_ROWS = 'MAX_ROWS'
CELL_HEIGHTS = 'CELL_HEIGHTS'
SASS_VARIABLES = {}
variables_path = os.path.join(settings.ASSETS_PATH, 'sass/_variables.sass')
with open(variables_path, 'r') as f:
    for line in f:
        try:
            var_name, value = line.split(':')
            if var_name == '$max-cols':
                SASS_VARIABLES[MAX_COLS] = int(value)
            elif var_name == '$max-rows':
                SASS_VARIABLES[MAX_ROWS] = int(value)
            elif var_name == '$cell-heights':
                SASS_VARIABLES[CELL_HEIGHTS] = [int(hh) for hh in
                                                value.split(',')]
        except ValueError:
            pass


# ------------------------------------------------------------------------------
# File paths
# ------------------------------------------------------------------------------
def favicon_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = 'favicon.%s' % ext
    return os.path.join('img', instance.slug, filename)


def image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = 'image_%s.%s' % (instance.pk, ext)
    return os.path.join('img', instance.slug, filename)


# ------------------------------------------------------------------------------
# Status helpers
# ------------------------------------------------------------------------------
class PublicationStatus(Choices):
    UN_PUBLISHED = 'UN_PUBLISHED'
    PUBLISHED = 'PUBLISHED'
    DELETED = 'DELETED'


class Language(Choices):
    EN = 'English'
    ES = 'Spanish'


class CellHeight(Choices):
    pass


for cell_height in SASS_VARIABLES[CELL_HEIGHTS]:
    setattr(CellHeight, 'HEIGHT_%s' % cell_height, cell_height)


class PublicationStatusField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(PublicationStatusField, self).__init__(
            max_length=255,
            choices=PublicationStatus.choices())


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(LanguageField, self).__init__(
            max_length=255,
            choices=Language.choices())


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------
class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_visible = models.BooleanField(default=False)
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    language = LanguageField()
    favicon = ImageCropField(upload_to=favicon_path, null=True, blank=True)
    favicon_cropping = ImageRatioField('favicon', '128x128')
    page_width = models.PositiveIntegerField(default=1000, help_text='In pixels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug

    def domain(self):
        return '%s.maasaic.com' % self.slug


class Page(models.Model):
    class Mode(Choices):
        LIVE = 'LIVE'
        EDIT = 'EDIT'
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    parent_page = models.ForeignKey('self', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    mode = models.CharField(max_length=255, choices=Mode.choices())
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, default='')
    page_width = models.PositiveIntegerField(null=True, blank=True, help_text='In pixels', default=1000)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('parent_page', 'slug', 'mode')

    def visible_sections(self):
        return self.section_set\
            .filter(is_visible=True)\
            .order_by('-order')

    def absolute_path(self):
        slug = '/' if self.slug is None else self.slug
        if self.parent_page is None:
            return slug
        else:
            return urljoin(self.parent_page.absolute_path(), slug)

    def __str__(self):
        return '%s | %s' % (self.website.name, self.name)

    def get_page_width(self):
        if self.page_width:
            return self.page_width
        else:
            return self.website.page_width


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    is_visible = models.BooleanField(default=True)
    n_columns = models.PositiveIntegerField(
        default=5,
        help_text='Measured in cells',
        validators=[MinValueValidator(1),
                    MaxValueValidator(SASS_VARIABLES[MAX_COLS])])
    n_rows = models.PositiveIntegerField(
        default=1,
        help_text='Measured in cells',
        validators=[MinValueValidator(1),
                    MaxValueValidator(SASS_VARIABLES[MAX_ROWS])])
    cell_height = models.PositiveIntegerField(choices=CellHeight.choices(),
                                              help_text='In pixels')
    css = JSONField(null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('page', 'order')

    def __str__(self):
        return '%s #%s' % (self.page, self.order)


class Cell(models.Model):
    class Type(Choices):
        TEXT = 'TEXT'
        IMAGE = 'IMAGE'
        IFRAME = 'IFRAME'

    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    cell_type = models.CharField(max_length=255, choices=Type.choices())
    is_visible = models.BooleanField(default=True)
    h = models.PositiveIntegerField(help_text='Number of cells')
    w = models.PositiveIntegerField(help_text='Number of cells')
    x = models.PositiveIntegerField(
        help_text='Number of cells',
        choices=[(x + 1, x + 1) for x in range(SASS_VARIABLES[MAX_COLS])])
    y = models.PositiveIntegerField(
        help_text='Number of cells',
        choices=[(x + 1, x + 1) for x in range(SASS_VARIABLES[MAX_ROWS])])

    content = models.TextField(null=True, blank=True)
    css = JSONField(null=True, blank=True)
    padding = models.CharField(max_length=255, default='20px')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s: %s (w: %s, h:%s, x: %s, y: %s)' % \
               (self.section_id, self.cell_type,
                self.w, self.h, self.x, self.y)

    def draw_content(self):
        return 'yeah'
