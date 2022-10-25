from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, is_active=True):
        if not phone_number:
            raise ValueError("User must have a phone number")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)  # change password to hash
        user.phone_number = phone_number
        user.is_active = is_active
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, is_active=True, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not phone_number:
            raise ValueError("User must have a phone number")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.phone_number = phone_number
        user.is_active = is_active
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    last_login = None
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=13, default="+98", unique=True, help_text="Phone number should start with '+98'.\nThis field should contain 13 character.")
    national_code = models.CharField(max_length=10, default="", help_text="National code should contain 10 character.")
    is_expert = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    objects = UserManager()

    def __str__(self):
        return self.phone_number
