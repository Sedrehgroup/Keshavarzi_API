from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_staff = None
    username = None
    last_login = None
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=13, default="+98", unique=True, help_text="Phone number should start with '+98'.\nThis field should contain 13 character.")
    national_code = models.CharField(max_length=10, default="", help_text="National code should contain 10 character.")
    is_expert = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.phone_number
