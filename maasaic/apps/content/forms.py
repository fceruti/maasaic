from maasaic.apps.content.models import Section
from maasaic.apps.content.models import Cell
from django import forms


class SectionVisibilityForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['is_visible']
