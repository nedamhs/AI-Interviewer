from django.db import models
from django.conf import settings
from documents.models import Resume
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField

class TalentProfile(models.Model):
    """Abstract user profile for talent"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    headline = models.CharField(max_length=100)

    linkedin_url = models.URLField(max_length=200, default="", blank=True)

    locations = models.ManyToManyField(
        to="locations.Location", related_name="talent_profiles", blank=True
    )

    resume = models.OneToOneField(
        Resume, on_delete=models.SET_NULL, related_name="profile", null=True, blank=True
    )

    # additional contact info
    phone_number = PhoneNumberField(null=True, blank=True)

