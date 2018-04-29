from django import forms
from django.core.validators import slug_re

from maasaic.apps.content.models import Website
from maasaic.apps.users.models import User
from django.conf import settings


class SubdomainField(forms.CharField):

    def clean(self, value):
        subdomain = value.lower()
        if not slug_re.match(subdomain):
            raise forms.ValidationError(
                'Invalid subdomain. Please only use the following characters: '
                'a-z, 0-9, -, _.')

        try:
            Website.objects.get(subdomain=subdomain)
            msg = 'The domain %s.%s has already been taken. Try another one.' \
                  % (subdomain, settings.DEFAULT_SITE_DOMAIN)
            raise forms.ValidationError(msg)
        except Website.DoesNotExist:
            pass
        try:
            User.objects.get(username=subdomain)
            msg = 'The domain %s.%s has already been taken. Try another one.' \
                  % (subdomain, settings.DEFAULT_SITE_DOMAIN)
            raise forms.ValidationError(msg)
        except User.DoesNotExist:
            pass
        return subdomain
