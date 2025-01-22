from django.db import models

# Create your models here.

class Resume(models.Model):
    """Resume document model, storing relevant resume data"""

    # resume data parsed into JSON format
    data = models.JSONField(blank=True, null=True)

    clean_text = models.TextField(blank=True, null=True)