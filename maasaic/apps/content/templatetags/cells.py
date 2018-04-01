from django import template
from maasaic.apps.content.models import Cell
from django.utils.text import mark_safe
register = template.Library()


@register.simple_tag()
def insert_cell_class(col, row, cells):
    for cell in cells:
        if all([cell.x <= col,
                col <= cell.x + cell.w - 1,
                cell.y <= row,
                row <= cell.y + cell.h - 1]):
            return 'cannot-insert'
    return 'can-insert'


@register.simple_tag()
def cell_type_icon(cell):
    if cell.cell_type == Cell.Type.TEXT:
        return mark_safe('<i class="fa fa fa-font"></i>')
    if cell.cell_type == Cell.Type.IMAGE:
        return mark_safe('<i class="fa fa fa-camera"></i>')
