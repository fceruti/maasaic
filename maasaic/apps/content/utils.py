from django.conf import settings
from django.urls import reverse


def resolve_url(name, args=None, private_domain=None):
    schema = 'https' if settings.SECURE_SCHEMA else 'http'
    domain = private_domain if private_domain else settings.DEFAULT_SITE_DOMAIN
    if args is None:
        args = []
    path = reverse(name, args=args)
    return '{schema}://{domain}{path}'\
        .format(schema=schema, domain=domain, path=path)
