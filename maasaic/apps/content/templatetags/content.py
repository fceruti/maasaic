from django import template
from django.utils.text import mark_safe
from pyquery import PyQuery as pq

from maasaic.apps.content.models import Cell
from maasaic.apps.content.utils import get_position_dict_from_margin
from maasaic.apps.content.utils import get_position_string_from_position

register = template.Library()


# ------------------------------------------------------------------------------
# Page
# ------------------------------------------------------------------------------
@register.simple_tag()
def page_width(page):
    if page.page_width:
        return page.page_width
    else:
        return page.website.page_width


# ------------------------------------------------------------------------------
# Section
# ------------------------------------------------------------------------------
@register.simple_tag()
def section_cell_default_padding(section):
    # TODO: Implement section defaults
    return '20px'


@register.simple_tag()
def section_cell_default_margin(section):
    # TODO: Implement section defaults
    return '20px'


@register.simple_tag()
def section_cell_default_background(section):
    # TODO: Implement section defaults
    return '#DDDDDD'


@register.simple_tag()
def section_cell_default_border(section):
    # TODO: Implement section defaults
    return 'none'


@register.simple_tag()
def section_cell_default_border_radius(section):
    # TODO: Implement section defaults
    return '0px'


@register.simple_tag()
def section_cell_default_shadow(section):
    # TODO: Implement section defaults
    return 'none'


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
