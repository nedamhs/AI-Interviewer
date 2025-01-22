from django.db import models
from locations.models import Location
from djmoney.models.fields import MoneyField

class Job(models.Model):
    """Job model, storing relevant job data"""

    # role basic data
    title = models.CharField(max_length=100, default="", blank=True)

    # job decription, markdown supported
    description = models.TextField(default="", blank=True)

    locations = models.ManyToManyField(Location, related_name="jobs", blank=True)

    target_budget = MoneyField(
        max_digits=12, decimal_places=4, default_currency="USD", null=True, blank=True
    )

    remote_option = models.BooleanField(default=False, blank=True)

