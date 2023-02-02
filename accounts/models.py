from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from repo.models import BaseModel


class UserManager(BaseUserManager):
    """Custom manager for the `User` model."""

    def create_user(self, email, password, **extra_fields):
        """Create and return a new user instance with the given email and
        password.

        Args:
            email (str): The email address for the user.
            password (str): The password for the user.
            **extra_fields (dict): Additional fields to set on the user instance.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the `email` argument is not provided.
        """
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a new superuser instance with the given email and
        password.

        Args:
            email (str): The email address for the user.
            password (str): The password for the user.
            **extra_fields (dict): Additional fields to set on the user instance.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)


class User(PermissionsMixin, BaseModel, AbstractBaseUser):
    """Custom user model that extends Django's built-in `AbstractBaseUser` and
    `PermissionsMixin` models."""

    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    is_admin = models.BooleanField(default=False, blank=True)
    is_staff = models.BooleanField(default=False, blank=True)
    is_superuser = models.BooleanField(default=False, blank=True)
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name",)
