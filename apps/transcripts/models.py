from django.db import models
from interviews.models import Interview
from core.models import Timestampable
import uuid 

class Transcript(Timestampable):
    """Stores interview transcripts for a specific session"""

    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Unique session ID
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="transcripts")
    question = models.TextField() # stores question asked by chatbot
    answer = models.TextField() # stores answer from candidate
    def __str__(self):
        return f"Transcript ({self.session_id}) for {self.interview.candidate.user.first_name} - {self.interview.job.title}"
