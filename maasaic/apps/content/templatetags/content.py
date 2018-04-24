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
# Default Attibutes
# ------------------------------------------------------------------------------
def get_defaults_cache_value(request, website, scope, prop_name):
    def build_cache_key(scope, prop_name):
        return '%s-%s' % (scope, prop_name)

    key = build_cache_key(scope, prop_name)
    if not hasattr(request, '_defaults_cache'):
        default_props = SiteDefaultProp.objects.filter(site=website)
        default_props_dict = dict((build_cache_key(pr.scope, pr.prop), pr.value)
                                  for pr in default_props)

        cache = {}
        for site_prop in list(site_props.values()):
            site_prop_key = build_cache_key(site_prop['scope'],
                                            site_prop['name'])
            try:
                cache[site_prop_key] = default_props_dict[site_prop_key]
            except KeyError:
                cache[site_prop_key] = site_prop['default']

        setattr(request, '_defaults_cache', cache)
    print(getattr(request, '_defaults_cache'))
    return getattr(request, '_defaults_cache')[key]


@register.simple_tag(takes_context=True)
def section_cell_default_padding(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='padding')


@register.simple_tag(takes_context=True)
def section_cell_default_margin(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='margin')


@register.simple_tag(takes_context=True)
def section_cell_default_background(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='background')


@register.simple_tag(takes_context=True)
def section_cell_default_border(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='border')


@register.simple_tag(takes_context=True)
def section_cell_default_border_radius(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='border_radius')


@register.simple_tag(takes_context=True)
def section_cell_default_shadow(context, section):
    return get_defaults_cache_value(request=context['request'],
                                    website=section.page.website,
                                    scope=SiteDefaultProp.Scope.CELL,
                                    prop_name='box_shadow')


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
