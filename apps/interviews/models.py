from django.db import models

# Create your models here.

from django.db import models
from jobs.models import Job 
from profiles.models import TalentProfile 
from core.models import Timestampable
import uuid 

class InterviewStatusChoices(models.TextChoices):
    SCHEDULED = "scheduled"
    AWAITING_FEEDBACK = "awaiting_feedback"
    COMPLETE = "complete"

class Interview(Timestampable):
    start = models.DateTimeField(
            null=True, blank=True, help_text="Start time of the interview"
        )
    end = models.DateTimeField(
            null=True, blank=True, help_text="End time of the interview"
        )

    candidate = models.ForeignKey(
            TalentProfile,
            related_name="job_applications",
            on_delete=models.CASCADE,
            null=True,
        )

    job = models.ForeignKey(
            Job,
            related_name="job_applications",
            on_delete=models.CASCADE,
            null=True
        )

    status = models.CharField(
            max_length=50,
            choices=InterviewStatusChoices.choices,
            default=InterviewStatusChoices.SCHEDULED,
        )