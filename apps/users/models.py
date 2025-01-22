from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    """Abstract user class with basic information"""

    # Allow blank values for first_name and last_name
    first_name = models.CharField(max_length=30, blank=True)

    last_name = models.CharField(max_length=30, blank=True)

    email = models.EmailField(
        _("email address"),
        max_length=50,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )