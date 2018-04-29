import pytest
from django.urls import reverse

from maasaic.apps.content.models import Language
from tests.helpers import create_test_page

pytestmark = pytest.mark.django_db


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


def test_delete_page(client_user_website):
    client, user, website = client_user_website
    assert website.page_set.count() == 0
    live_page, edit_page = create_test_page(website=website)
    assert website.page_set.count() == 2
    url = reverse('page_delete', args=[website.subdomain, live_page.pk])
    client.post(url)
    assert website.page_set.count() == 0
