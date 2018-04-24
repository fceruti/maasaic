from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe


class ColorWidget(Widget):
    template_name = 'widgets/color.html'
