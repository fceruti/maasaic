import pytest
from django.urls import reverse

from tests.helpers import create_test_website

pytestmark = pytest.mark.django_db


def test_login_with_username(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': user.username, 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is True


def test_login_with_subdomain(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': website.subdomain, 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is True


def test_login_with_secondary_subdomain(user_website, app_urls, client):
    user, website = user_website
    other_website = create_test_website(subdomain='other-site', user=user)
    post_kwargs = {'subdomain': other_website.subdomain, 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is True


def test_cannot_login_wrong_username(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': user.username + '1', 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is False


def test_cannot_login_wrong_subdomain(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': website.subdomain + '1', 'password': '12345678'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is False


def test_cannot_login_wrong_password(user_website, app_urls, client):
    user, website = user_website
    post_kwargs = {'subdomain': website.subdomain, 'password': '1234567'}
    response = client.post(reverse('login'), post_kwargs, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated is False
