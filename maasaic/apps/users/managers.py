from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if email:
            email = self.normalize_email(email.lower())
        else:
            email = None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username=username)
