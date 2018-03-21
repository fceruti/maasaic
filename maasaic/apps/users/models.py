from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from maasaic.apps.users.managers import UserManager
from maasaic.apps.utils.models import Choices


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, db_index=True)
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_profile_ready = models.BooleanField(default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
