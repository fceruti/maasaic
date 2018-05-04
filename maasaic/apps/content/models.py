import os
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxLengthValidator
from django.core.validators import MaxValueValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from easy_thumbnails.files import get_thumbnailer
from image_cropping import ImageCropField
from image_cropping import ImageRatioField

from maasaic.apps.content.managers import PageManager
from maasaic.apps.users.models import User
from maasaic.apps.utils.models import Choices

# ------------------------------------------------------------------------------
# Sass variables
# ------------------------------------------------------------------------------
MAX_COLS_KEY = 'MAX_COLS'
MAX_ROWS_KEY = 'MAX_ROWS'
PAGE_WIDTHS_KEY = 'PAGE_WIDTHS'
SASS_VARIABLES = {}
variables_path = os.path.join(settings.ASSETS_PATH, 'sass/_variables.sass')
with open(variables_path, 'r') as f:
    for line in f:
        try:
            var_name, value = line.split(':')
            if var_name == '$max-cols':
                SASS_VARIABLES[MAX_COLS_KEY] = int(value)
            elif var_name == '$max-rows':
                SASS_VARIABLES[MAX_ROWS_KEY] = int(value)
            elif var_name == '$page-widths':
                SASS_VARIABLES[PAGE_WIDTHS_KEY] = [int(hh) for hh in
                                                   value.split(',')]
        except ValueError:
            pass


# ------------------------------------------------------------------------------
# File paths
# ------------------------------------------------------------------------------
def favicon_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = 'favicon.%s' % ext
    return os.path.join(instance.subdomain, 'favicons', filename)


def image_path(instance, filename):
    return os.path.join('img', instance.website.subdomain, 'images', filename)


def image_cell_path(instance, filename):
    page = instance.cell.section.page
    website = page.website
    return os.path.join('img', website.subdomain, 'page-%s' % page.pk, filename)


# ------------------------------------------------------------------------------
# Status helpers
# ------------------------------------------------------------------------------
class Language(Choices):
    EN = 'EN'
    ES = 'ES'


class PageWidth(Choices):
    pass


for page_width in SASS_VARIABLES[PAGE_WIDTHS_KEY]:
    setattr(PageWidth, '%s_px' % page_width, page_width)


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
    private_domain = models.CharField(max_length=255, unique=True,
                                      db_index=True, null=True, blank=True)
    subdomain = models.CharField(max_length=255, unique=True, db_index=True,
                                 validators=[MinLengthValidator(1),
                                             MaxLengthValidator(20)])
    name = models.CharField(max_length=255, validators=[MinLengthValidator(1),
                                                        MaxLengthValidator(50)])
    description = models.TextField(null=True, blank=True)
    language = LanguageField()
    favicon = ImageCropField(upload_to=favicon_path, null=True, blank=True)
    favicon_cropping = ImageRatioField('favicon', '128x128')
    page_width = models.PositiveIntegerField(choices=PageWidth.choices(),
                                             default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain

    @property
    def domain(self):
        if self.private_domain:
            return self.private_domain
        return '%s.%s' % (self.subdomain, settings.DEFAULT_SITE_DOMAIN)

    @property
    def public_url(self):
        schema = 'https' if settings.SECURE_SCHEMA else 'http'
        return '{schema}://{domain}'.format(schema=schema, domain=self.domain)

    @cached_property
    def favicon_url(self):
        if self.favicon_cropping:
            from image_cropping.utils import get_backend
            thumbnail_url = get_backend().get_thumbnail_url(
                self.favicon,
                {
                    'size': (128, 128),
                    'box': self.favicon_cropping,
                    'crop': True,
                    'detail': True,
                }
            )
            return thumbnail_url
        return '%simg/favicon.png' % settings.STATIC_URL

    @cached_property
    def edit_pages(self):
        return self.page_set.filter(mode=Page.Mode.EDIT)

    @cached_property
    def live_pages(self):
        return self.page_set.filter(mode=Page.Mode.LIVE).order_by('path')


class Page(models.Model):
    class Mode(Choices):
        LIVE = 'LIVE'
        EDIT = 'EDIT'
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    target_page = models.OneToOneField('self', null=True, blank=True,
                                       on_delete=models.CASCADE,
                                       related_name='edit_page')
    is_visible = models.BooleanField(default=False)
    mode = models.CharField(max_length=255, choices=Mode.choices())
    title = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    width = models.PositiveIntegerField(choices=PageWidth.choices())
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PageManager()

    class Meta:
        unique_together = ('website', 'path', 'mode')

    def __str__(self):
        return '%s | %s' % (self.website.name, self.title)

    @cached_property
    def all_sections(self):
        return self.section_set\
            .order_by('order')

    @cached_property
    def visible_sections(self):
        return [section for section in self.all_sections if section.is_visible]

    @property
    def public_url(self):
        return urljoin(self.website.public_url, self.path)

    @cached_property
    def edit_page(self):
        if self.mode == self.Mode.LIVE:
            raise Exception
        return Page.objects.get(target_page=self)


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    is_visible = models.BooleanField(default=True)
    n_columns = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1),
                    MaxValueValidator(SASS_VARIABLES[MAX_COLS_KEY])])
    n_rows = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1),
                    MaxValueValidator(SASS_VARIABLES[MAX_ROWS_KEY])])
    css = JSONField(null=True, blank=True)
    name = models.CharField(max_length=255)
    html_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_attr_dict(self):
        return {
            'order': self.order,
            'n_columns': self.n_columns,
            'n_rows': self.n_rows,
            'css': self.css,
            'name': self.name,
            'html_id': self.html_id,
        }

    class Meta:
        ordering = 'order',

    def __str__(self):
        return '%s #%s' % (self.page, self.order)

    @cached_property
    def all_cells(self):
        return self.cell_set\
            .order_by('order')

    @cached_property
    def visible_cells(self):
        return [cell for cell in self.all_cells if cell.is_visible]

    @cached_property
    def editable_cells(self):
        return self.visible_cells


class Cell(models.Model):
    class Type(Choices):
        TEXT = 'TEXT'
        IMAGE = 'IMAGE'
        IFRAME = 'IFRAME'

    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    cell_type = models.CharField(max_length=255, choices=Type.choices())
    is_visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    x = models.PositiveIntegerField(
        help_text='Number of cells',
        choices=[(x + 1, x + 1) for x in range(SASS_VARIABLES[MAX_COLS_KEY])])
    y = models.PositiveIntegerField(
        help_text='Number of cells',
        choices=[(x + 1, x + 1) for x in range(SASS_VARIABLES[MAX_ROWS_KEY])])
    w = models.PositiveIntegerField(help_text='Number of cells')
    h = models.PositiveIntegerField(help_text='Number of cells')

    content = models.TextField(null=True, blank=True)
    css = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_file(self):
        if self.cell_image:
            return self.cellimage.image
        return None

    @property
    def image_cropping(self):
        if self.cell_image:
            return self.cellimage.cropping
        return None

    @cached_property
    def cell_image(self):
        try:
            return CellImage.objects.get(cell=self)
        except CellImage.DoesNotExist:
            return None

    def get_attr_dict(self):
        return {
            'cell_type': self.cell_type,
            'order': self.order,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'content': self.content,
            'css': self.css,
        }

    class Meta:
        ordering = 'order',

    def __str__(self):
        return '%s: %s (w: %s, h:%s, x: %s, y: %s)' % \
               (self.section_id, self.cell_type,
                self.w, self.h, self.x, self.y)


class UploadedImage(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_path,
                              height_field='height',
                              width_field='width')
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    height = models.IntegerField()
    width = models.IntegerField()
    size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def thumbnail_url(self):
        options = {'size': (300, 200), 'crop': True}
        return get_thumbnailer(self.image).get_thumbnail(options).url


class CellImage(models.Model):
    cell = models.OneToOneField(Cell, on_delete=models.CASCADE)
    uploaded_image = models.ForeignKey(UploadedImage, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(blank=True, upload_to=image_cell_path)
    cropping = JSONField()


class SiteDefaultProp(models.Model):
    class Scope(Choices):
        SECTION = 'SECTION'
        CELL = 'CELL'
    site = models.ForeignKey(Website, on_delete=models.CASCADE)
    scope = models.CharField(max_length=255, choices=Scope.choices())
    prop = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('site', 'scope', 'prop')


class Font(models.Model):
    class Source(Choices):
        NATIVE = 'NATIVE'
        GOOGLE = 'GOOGLE'

    name = models.CharField(max_length=255)
    default = models.CharField(max_length=255, default='sans-serif')
    source = models.CharField(max_length=255, default=Source.GOOGLE)

    def __str__(self):
        return self.name

    @property
    def url(self):
        url_name = '+'.join(self.name.split(' '))
        return 'https://fonts.googleapis.com/css?family=%s' % url_name


class PageFont(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    font = models.ForeignKey(Font, on_delete=models.CASCADE)
