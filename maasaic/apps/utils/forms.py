from django.forms.widgets import Widget


class ColorWidget(Widget):
    template_name = 'widgets/color.html'
