import hashlib

from django import template
from django.utils.text import mark_safe
from pyquery import PyQuery as pq

from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import SiteDefaultProp
from maasaic.apps.content.forms import site_props
from maasaic.apps.content.utils import get_position_dict_from_margin
from maasaic.apps.content.utils import get_position_string_from_position

register = template.Library()


# ------------------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------------------
CLASS_HASH_FIELDS = {
    Page: ['title', 'path', 'width', 'description'],
    Section: ['order', 'n_columns', 'n_rows', 'css', 'name', 'html_id'],
    Cell: ['cell_type', 'x', 'y', 'w', 'h', 'content', 'css'],
}


def get_obj_hash(obj):
    str_repr = ','.join([str(getattr(obj, field_acc))
                         for field_acc in CLASS_HASH_FIELDS[type(obj)]])
    return hashlib.md5(str_repr.encode('utf-8')).hexdigest()


# ------------------------------------------------------------------------------
# Page
# ------------------------------------------------------------------------------
@register.simple_tag()
def has_page_changed(edit_page):
    live_page = edit_page.target_page
    assert edit_page.mode == Page.Mode.EDIT
    assert live_page.mode == Page.Mode.LIVE

    try:
        assert get_obj_hash(edit_page) == get_obj_hash(live_page)
    except AssertionError:
        return True

    edit_sections = edit_page.visible_sections
    live_sections = live_page.visible_sections

    try:
        assert set(get_obj_hash(section) for section in edit_sections)  == \
               set(get_obj_hash(section) for section in live_sections)
    except AssertionError:
        return True

    edit_cells_hashes = set()
    live_cells_hashes = set()
    for section in edit_sections:
        for cell in section.visible_cells:
            edit_cells_hashes.add(get_obj_hash(cell))
    for section in live_sections:
        for cell in section.visible_cells:
            live_cells_hashes.add(get_obj_hash(cell))
    return live_cells_hashes != edit_cells_hashes


# ------------------------------------------------------------------------------
# Section
# ------------------------------------------------------------------------------
@register.simple_tag()
def section_cell_default_padding(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='padding')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['padding']['default']


@register.simple_tag()
def section_cell_default_margin(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='margin')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['margin']['default']


@register.simple_tag()
def section_cell_default_background(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='background')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['background']['default']


@register.simple_tag()
def section_cell_default_border(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='border')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['border']['default']


@register.simple_tag()
def section_cell_default_border_radius(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='border_radius')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['border_radius']['default']


@register.simple_tag()
def section_cell_default_shadow(section):
    try:
        prop = SiteDefaultProp.objects.get(
            site=section.page.website,
            scope=SiteDefaultProp.Scope.CELL,
            prop='box_shadow')
        return prop.value
    except SiteDefaultProp.DoesNotExist:
        return site_props['box_shadow']['default']


# ------------------------------------------------------------------------------
# Cell
# ------------------------------------------------------------------------------
@register.simple_tag()
def cell_type_icon(cell):
    if cell.cell_type == Cell.Type.TEXT:
        return mark_safe('<i class="fa fa fa-font"></i>')
    if cell.cell_type == Cell.Type.IMAGE:
        return mark_safe('<i class="fa fa fa-camera"></i>')


@register.simple_tag()
def cell_short_text(cell):
    if cell.cell_type == Cell.Type.TEXT:
        if cell.content:
            dom = pq(cell.content)
            return dom.text()[:10]
        else:
            return '(empty)'


@register.simple_tag()
def cell_inner_style_background(cell):
    try:
        background = cell.css['background']
    except KeyError:
        # TODO: fetch section default background
        background = 'white'
    return 'background: %s;' % background


@register.simple_tag()
def cell_inner_style_margin_position(cell):
    try:
        margin = cell.css['margin']
    except KeyError:
        margin = '0px'
    pos_dict = get_position_dict_from_margin(margin)
    return get_position_string_from_position(pos_dict)


@register.simple_tag()
def cell_inner_style_padding(cell):
    try:
        margin = cell.css['padding']
    except KeyError:
        margin = '0px'
    return 'margin: %s;' % margin
