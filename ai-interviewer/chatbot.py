from dotenv import load_dotenv
from utils.prompt import start_interview_prompt
from utils.inputs import update_history
from utils.bot import get_client, get_bot_response
from utils.interview import conduct_interview
from utils.openai_functions import end_interview
import os
import django
load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from jobs.models import Job
from profiles.models import TalentProfile


def conduct_ai_interview(job: Job, talent: TalentProfile, meeting_bot) -> None:  
    '''
    Main function which conducts the screening interview via the terminal.

    Inputs:
        job : Job
            Conducts an screening interview based on the job
        talent: TalentProfile
            Accounts for aspects on the talent's profile
        meeting_bot: MeetingBot
            Meeting bot that is running zoom meeting
            
    Returns: 
        None
    '''
    file_string =  start_interview_prompt(job, talent)
    transcript_messages = []
    conversation_history = []
    conversation_history.append({"role": "system", "content": file_string})

    # openai setup
    client = get_client()
    
    # first message
    bot_response = get_bot_response(client, conversation_history=conversation_history, tools=[end_interview()])
    bot_reply = bot_response.content
    
    update_history("assistant", conversation_history, transcript_messages,bot_reply)
    print("Interviewer: ", bot_reply)
    meeting_bot.tts(bot_reply)

    # start interview starting interview model
    try:
        conduct_interview(talent, job, transcript_messages, conversation_history, client, meeting_bot)
    except KeyboardInterrupt:
        print("\nStopped transcriber and interview.")

def conduct_random_interview(meeting_bot) -> None:
    '''
    Conducts a random interview with a random job and talent.

    Inputs:
        meeting_bot: MeetingBot
            Meeting bot that is running zoom meeting
    Returns:
        None
    '''
    # fetch random job and talent from database
    rand_job = Job.objects.order_by('?').first()
    rand_talent = TalentProfile.objects.order_by('?').first()

    print("Conducting a random interview for the position " + rand_job.title + ". The candidate's name is " + rand_talent.user.first_name + " " + rand_talent.user.last_name + ".")

    conduct_ai_interview(rand_job, rand_talent, meeting_bot)
