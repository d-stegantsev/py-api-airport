from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from base.managers import UserManager
from base.models import UUIDBaseModel


class User(UUIDBaseModel, AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
