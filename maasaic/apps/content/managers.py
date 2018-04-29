from django.db import models
from django.db import transaction


class PageManager(models.Manager):

    def create_page(self, website, path, title, width, description):
        from maasaic.apps.content.models import Page
        with transaction.atomic():
            live_page = Page.objects.create(
                website=website,
                is_visible=False,
                mode=Page.Mode.LIVE,
                title=title,
                path=path,
                width=width,
                description=description)
            edit_page = Page.objects.create(
                website=website,
                is_visible=False,
                target_page=live_page,
                mode=Page.Mode.EDIT,
                title=title,
                path=path,
                width=width,
                description=description)
        return live_page, edit_page
