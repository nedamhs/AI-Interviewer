from dotenv import load_dotenv
from utils.prompt import start_interview_prompt
from utils.inputs import update_history
from utils.bot import get_client, get_bot_response
from utils.interview import conduct_interview
import os
import django
import time

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from jobs.models import Job
from documents.models import Resume


def conduct_ai_interview(job: Job, resume: Resume) -> None:  
    '''
    Main function which conducts the screening interview via the terminal.

    Inputs:
        job : Job
            Conducts an screening interview based on the job
        resume : Resume 
            Accounts for aspects on the resume
            
    Returns: 
        None
    '''
    file_string =  start_interview_prompt(job, resume)
    transcript_messages = []
    conversation_history = []
    conversation_history.append({"role": "system", "content": file_string})

    # openai setup
    client = get_client()
    
    # first message
    bot_reply = get_bot_response(client, conversation_history=conversation_history)
    update_history("assistant", conversation_history, transcript_messages,bot_reply)
    print("Interviewer: ", bot_reply)

    conduct_interview(resume, transcript_messages, conversation_history, client)  


# ran as a script
if __name__ == "__main__":
    # function for conducting a interview with a random job and resume
    # function only if ran from command line
    def conduct_random_interview():
        # fetch random job and resume from database
        rand_job = Job.objects.order_by('?').first()
        rand_resume = Resume.objects.order_by('?').first()

        print("Conducting a random interview for the position " + rand_job.title + ". The candidate's name is " + rand_resume.data["first_name"] + ".")

        conduct_ai_interview(rand_job, rand_resume)

    conduct_random_interview()
