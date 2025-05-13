from django.contrib.auth.models import AbstractUser
from django.db import models

from base.managers import UserManager
from base.models import TimestampedUUIDBaseModel


class User(TimestampedUUIDBaseModel, AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=63, blank=True)
    last_name = models.CharField(max_length=63, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
