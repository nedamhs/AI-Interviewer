from dotenv import load_dotenv
from utils.prompt import start_interview_prompt, location_prompt
from utils.inputs import update_history
from utils.bot import get_client, get_bot_response
from utils.interview import conduct_interview, finalize_interview
from utils.openai_functions import end_interview, stop_interview_relocation, ask_relocation_confirmation
import os
import django
import time
import json
from django.utils import timezone

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from jobs.models import Job
from profiles.models import TalentProfile
from utils.distances import calculate_distance
from utils.bot import get_bot_response
from utils.inputs import get_user_input,update_history
from interviews.models import Interview, InterviewStatusChoices


def start_ai_interview(job: Job, talent: TalentProfile, meeting_bot) -> None:  
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
    
    job_locations = job.locations.all()  # get all job locations
    talent_locations = talent.locations.all() # get all talent location
    #curr_location = talent_locations[0].display_name if talent_locations else "Unknown" # get curr location in case of location update
    #print("TEST, CURR_LOCATION:", curr_location)

    distances = calculate_distance(job_locations, talent_locations)
    min_dist = min(distances, key=lambda x: x[2])[2] #sort by dist, get min
    print("\nTESTING: distances : ", distances, "\n") #testing! remove later

    start_time = time.time()

    # creating interview obj 
    interviewobj = Interview.objects.create(candidate=talent, job=job,
                                             start = timezone.now(),  # start time
                                             status=InterviewStatusChoices.SCHEDULED)
     
    # asking location questions: 
    category = "location"
    for question in location_prompt(min_dist, job.remote_option): 

            
            instruction =  f""" you are an ai interviewer, ask the following interview question in a friendly and personalized way:
                            Take the information from their resume to tailor/personalize the questions for the candidate.{question}"""

            conversation_history.append({"role": "user", "content": instruction})
            bot_response = get_bot_response(client, conversation_history, tools=[stop_interview_relocation()])

            if bot_response.content: 
                       bot_reply = bot_response.content
                       print("\nInterviewer:", bot_reply)
                       update_history("assistant", conversation_history, transcript_messages, bot_reply, category=category)
            
            print("You: ", end='', flush=True)
            user_input = get_user_input()
            update_history("user", conversation_history, transcript_messages, user_input)


  
    # after asking location questions, confirm the relocation decison if they are not willing to relocate 
    instruction =  f"""if candidate responds no to the relocation question, call the ask_relocation_confirmation() tool to confirm their relocation decision"""

    conversation_history.append({"role": "user", "content": instruction})
    bot_response = get_bot_response(client, conversation_history, tools=[ask_relocation_confirmation()])

    bot_tools = bot_response.tool_calls

    # if ask_relocation_confirmation() tool called 
    if bot_tools:
                for tool_call in bot_tools:
                            name = tool_call.function.name
                            args = json.loads(tool_call.function.arguments)

                            if name == "ask_relocation_confirmation":
                                    confirmation_question =  args["question"] # question generated from tool call
                                    print("\nInterviewer:", confirmation_question)
                                    update_history("assistant", conversation_history, transcript_messages, confirmation_question, category=category)

                                    # get confirmation response
                                    print("You: ", end='', flush=True)
                                    user_input = get_user_input()
                                    update_history("user", conversation_history, transcript_messages, user_input)

                                    # after asking confirmation quesion, decide to stop or not 
                                    instruction =  f"""if candidate confirmed they are not willing to relocate, Immediately call the ' stop_interview_relocation' tool to end the interview.""" 
                                     
                                    # ADD this TO INSTRUCTION : if changed mind, thank them. 
                                    conversation_history.append({"role": "user", "content": instruction})
                                    bot_response = get_bot_response(client, conversation_history, tools=[stop_interview_relocation()])

                                    # if changed mind, tool not called 
                                    if bot_response.content: 
                                         bot_reply = bot_response.content
                                         print("\nInterviewer:", bot_reply)
                                         update_history("assistant", conversation_history, transcript_messages, bot_reply, category=category)

                                    # if 'stop_interview_relocation' tool called
                                    else: 
                                         ending_msg = "unfortunately we cannot proceed further. have a great day."
                                         print("\nInterviewer:", ending_msg) 
                                         update_history("assistant", conversation_history, transcript_messages, ending_msg)
 

                                    bot_tools = bot_response.tool_calls

                                    if bot_tools:
                                        end = False
                                        for tool_call in bot_tools:
                                            name = tool_call.function.name
                                            args = json.loads(tool_call.function.arguments)

                                            if name == "stop_interview_relocation":
                                                 print("\nInterviewer [For admin]:", args["summary"]) 
                                                 interview_summary =  args["summary"]
                                                 interviewobj.summary = interview_summary # store in db
                                                 end = True
                                            if end:
                                               finalize_interview(interviewobj, transcript_messages, talent, client)
                                               return

                                    else: 
                                        # go to main interview function when user change minds on relocation.
                                        conduct_interview(interviewobj, talent, job, transcript_messages, conversation_history, client)
 
    else: 
        # goes to main interview function to ask non-location questions. 
        conduct_interview(interviewobj, talent, job, transcript_messages, conversation_history, client)



# ran as a script
if __name__ == "__main__":
    # function for conducting a interview with a random job and talent
    # function only if ran from command line
    def conduct_random_interview():
        # fetch random job and talent from database
        rand_job = Job.objects.order_by('?').first()
        rand_talent = TalentProfile.objects.order_by('?').first()

    print("Conducting a random interview for the position " + rand_job.title + ". The candidate's name is " + rand_talent.user.first_name + " " + rand_talent.user.last_name + ".")

    start_ai_interview(rand_job, rand_talent, meeting_bot)
