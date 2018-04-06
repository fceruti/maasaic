from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from maasaic.apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.nickname

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return self.is_superuser
