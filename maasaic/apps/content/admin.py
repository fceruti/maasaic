import nested_admin
from django.contrib import admin

from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import Website


# ------------------------------------------------------------------------------
# Website
# ------------------------------------------------------------------------------
@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    class PageInline(admin.StackedInline):
        model = Page
        extra = 0

    list_display = ['name', 'subdomain', 'private_domain',  'user',
                    'created_at', 'updated_at']
    inlines = [PageInline]


# ------------------------------------------------------------------------------
# Page
# ------------------------------------------------------------------------------
class CellInline(nested_admin.NestedTabularInline):
    model = Cell
    extra = 0


class SectionInline(nested_admin.NestedStackedInline):
    model = Section
    sortable_field_name = 'order'
    inlines = [CellInline]
    extra = 0


@admin.register(Page)
class PageAdmin(nested_admin.NestedModelAdmin):
    list_display = ['website', 'title', 'created_at', 'updated_at']
    inlines = [SectionInline]


# ------------------------------------------------------------------------------
# Section
# ------------------------------------------------------------------------------
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    class CellInline(admin.StackedInline):
        model = Cell
        extra = 0
    list_display = ['page']
    inlines = [CellInline]


# ------------------------------------------------------------------------------
# Cell
# ------------------------------------------------------------------------------
@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['section', 'cell_type', 'h', 'w', 'x', 'y']
