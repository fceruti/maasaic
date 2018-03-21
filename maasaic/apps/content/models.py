import os

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.template.defaultfilters import slugify
from image_cropping import ImageCropField
from image_cropping import ImageRatioField

from maasaic.apps.users.models import User
from maasaic.apps.utils.models import Choices


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


class PublicationStatusField(models.CharField):
    def __init__(self, *args, **kwargs):
        return super(PublicationStatusField, self).__init__(
            max_length=255,
            choices=PublicationStatus.choices())


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        return super(LanguageField, self).__init__(
            max_length=255,
            choices=Language.choices())


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------
class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_status = PublicationStatusField()
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    language = LanguageField()
    favicon = ImageCropField(upload_to=favicon_path, null=True, blank=True)
    favicon_cropping = ImageRatioField('favicon', '128x128')


class Page(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    pub_status = PublicationStatusField()
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)


class Row(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    pub_status = PublicationStatusField()
    order = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        unique_together = ('page', 'order')


class Cell(models.Model):
    class Type(Choices):
        TEXT = 'TEXT'
        IMAGE = 'IMAGE'
        VIDEO = 'VIDEO'
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cell_type = models.CharField(max_length=255, choices=Type.choices())
    background = models.TextField(null=True, blank=True)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    content = models.TextField(null=True, blank=True)
    css = JSONField(null=True, blank=True)


class CellPosition(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

class Image(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    image = models.ImageField()
    alt_text = models.CharField(max_length=255)


class CellImage(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    cropping = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255)
