from django.db import models
from jobs.models import Job
from profiles.models import TalentProfile
import uuid 

class Transcript(models.Model):
    """Stores interview transcripts for a specific session"""

    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Unique session ID
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="transcripts")
    candidate_profile = models.ForeignKey(TalentProfile, on_delete=models.CASCADE, related_name="transcripts")
    content = models.TextField()  # storing full interview transcript
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript ({self.session_id}) for {self.candidate_profile.user.first_name} - {self.job.title}"
