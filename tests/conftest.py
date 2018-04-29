import pytest
from django.urls import reverse
from django.urls import set_urlconf

from tests.helpers import create_test_user
from tests.helpers import create_test_website


@pytest.fixture
def app_urls():
    set_urlconf('maasaic.apps.content.urls.app')


@pytest.fixture
def user_website():
    email = 'me@test.com'
    password = '12345678'
    user = create_test_user(email=email, password=password)
    company = create_test_website(subdomain= 'test-web', user=user)
    return user, company


@pytest.fixture
def client_user_website(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': user.email, 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    return client, user, website
