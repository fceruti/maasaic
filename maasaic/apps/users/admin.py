from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from maasaic.apps.users.models import User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ['pk', 'username', 'email']
    list_filter = []
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

