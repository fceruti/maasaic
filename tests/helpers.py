import string
from random import choice

from maasaic.apps.content.models import Website
from maasaic.apps.users.models import User


def _random_string(length=10):
    return ''.join(choice(string.ascii_letters) for _ in range(length))


def create_test_user(username=None, email=None, password=None) -> User:
    if not username:
        username = _random_string()
    if not password:
        password = _random_string()
    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password)
    return user


def create_test_website(subdomain=None, user=None) -> Website:
    if not subdomain:
        subdomain = _random_string()
    if not user:
        user = create_test_user()
    website = Website.objects.create(user=user, subdomain=subdomain)
    return website
