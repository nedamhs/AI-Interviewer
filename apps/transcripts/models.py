from django.db import models
from interviews.models import Interview
from core.models import Timestampable
import uuid 

class Transcript(Timestampable):
    """Stores interview transcripts for a specific session"""

    #session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Unique session ID
    session_id = models.UUIDField(default=uuid.uuid4,  editable=False) # removed uniqe id, because we can have multiple entries w same id in table 
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="transcripts") 
    question = models.TextField() # stores question asked by chatbot
    answer = models.TextField() # stores answer from candidate
    category = models.CharField(max_length=50, blank=True, null = True)
    
    def __str__(self):
        return f"Transcript ({self.session_id}) for {self.interview.candidate.user.first_name} - {self.interview.job.title}"
    class Meta:
        app_label = 'transcripts'

class CategoryChoices(models.TextChoices):
    LOCATION = "location"
    AVAILABILITY = "availability"
    SCHEDULE = "schedule"
    ACADEMIC_BACKGROUND = "academic_background"
    INTEREST = "interest"
    PREV_EXPERIENCE = "prev_experience"
    TEAMWORK = "teamwork"
    COMMUNICATION = "communication"
    PREFERENCE = "preference"

class InterviewScore(models.Model):  
    interview = models.ForeignKey(Interview,on_delete=models.CASCADE, related_name="scores")
    category = models.CharField(max_length=50,choices=CategoryChoices.choices)
    score = models.FloatField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.interview} - {self.category}: {self.score}"