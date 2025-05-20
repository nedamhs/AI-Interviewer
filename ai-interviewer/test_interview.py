from dotenv import load_dotenv
import os
import django
import time
import json

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from utils.interview_session import InterviewSession
from profiles.models import TalentProfile
from jobs.models import Job


def receive_response(response):
    print("Interviewer: ", response)
    
# ran as a script
if __name__ == "__main__":
    # function for conducting a interview with a random job and talent
    # function only if ran from command line
    def conduct_random_interview():
        # fetch random job and talent from database
        rand_job = Job.objects.order_by('?').first()
        rand_talent = TalentProfile.objects.order_by('?').first()

        print("Conducting a random interview for the position " + rand_job.title +
              ". The candidate's name is " + rand_talent.user.first_name + " " + rand_talent.user.last_name + ".")

        interview = InterviewSession(rand_job, rand_talent, receive_response)
        interview.start()
        
        while not interview.phase == "ENDED":
            i = input("You: ")
            interview.send_response(i)

    conduct_random_interview()
