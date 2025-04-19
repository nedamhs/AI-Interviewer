from django.http import JsonResponse
from transcripts.models import Transcript, InterviewScore
from django.shortcuts import get_object_or_404, render


# Get all transcripts for an interview session
def get_transcripts(request, session_id):
    transcripts = Transcript.objects.filter(session_id=session_id)
    transcript_data = [
        {
            "question": transcript.question,
            "answer": transcript.answer,
            "category": transcript.category,
            "interview": {
                "candidate": transcript.interview.candidate.user.first_name,
                "job_title": transcript.interview.job.title,
            }
        }
        for transcript in transcripts
    ]
    return JsonResponse(transcript_data, safe=False)

# Get interview scores for a particular interview id
def get_interview_scores(request, interview_id):
    interview_scores = InterviewScore.objects.filter(interview_id=interview_id)
    score_data = [
        {
            "category": score.category,
            "score": score.score,
            "reason": score.reason,
        }
        for score in interview_scores
    ]
    return JsonResponse(score_data, safe=False)
