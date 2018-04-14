from django.conf import settings


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_name = request.META.get('HTTP_HOST') or \
                    request.META.get('SERVER_NAME')
        pieces = host_name.split('.')
        domain = '.'.join(pieces[-2:])
        subdomain = '.'.join(pieces[:-2])

        if domain == settings.DEFAULT_SITE_DOMAIN:
            if subdomain in ['', 'www']:
                url_conf_path = 'maasaic.apps.content.urls.app'
            else:
                url_conf_path = 'maasaic.apps.content.urls.page'
        else:
            url_conf_path = 'maasaic.apps.content.urls.page'
        request.urlconf = url_conf_path
        request.domain = domain
        request.subdomain = subdomain
        return self.get_response(request)
