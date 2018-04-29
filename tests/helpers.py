import string
from random import choice

from maasaic.apps.content.models import Website
from maasaic.apps.content.models import Page
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


def create_test_website(name=None, subdomain=None, user=None) -> Website:
    if not subdomain:
        subdomain = _random_string()
    if not name:
        name = subdomain.title()
    if not user:
        user = create_test_user()
    website = Website.objects.create(user=user, name=name, subdomain=subdomain)
    return website


def create_test_page(website=None, path=None, title=None, width=None,
                     description=None):
    if path is None:
        path = '/'
    if website is None:
        website = create_test_website()
    if title is None:
        title = 'Test page'
    if width is None:
        width = 1000
    if description is None:
        description = 'No description given'
    return Page.objects.create_page(website=website,
                                    path=path,
                                    title=title,
                                    width=width,
                                    description=description)
