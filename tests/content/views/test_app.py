import pytest
from django.urls import reverse
pytestmark = pytest.mark.django_db
from maasaic.apps.content.models import Language


@pytest.mark.parametrize('field, value, fails', [
    ('name', '', True),
    ('name', 'Good name', False),
    ('name', 'Way too long of a text for a title that should actually be short', True),
    ('language', '', False),
    ('language', Language.EN, False),
    ('language', Language.ES, False),
    ('language', 'PT', True),
])
def test_update_website(client_user_website, field, value, fails):
    client, user, website = client_user_website

    params = {'name': website.name,
              'page_width': website.page_width,
              'description': website.description,
              'language': website.language,
              field: value}

    config_url = reverse('website_config', args=[website.subdomain])
    response = client.post(config_url, params, follow=False)

    if fails:
        assert response.status_code == 200
    else:
        assert response.status_code == 302
