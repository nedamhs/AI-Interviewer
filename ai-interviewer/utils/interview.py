from .openai_functions import end_interview
import time
import json
from .transcript import write_to_transcript, write_transcript_to_db
from .bot import get_bot_response
from .inputs import get_user_input,update_history
from openai import OpenAI
import django
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from profiles.models import TalentProfile
from jobs.models import Job
from locations.models import Location
from .distances import calculate_distance, process_location_update
from django.utils import timezone
from interviews.models import Interview, InterviewStatusChoices
from .scoring import score_interview 


def conduct_interview(talent: TalentProfile, job: Job,  transcript_messages:list, conversation_history:list, client:OpenAI) -> None:
        '''
        Main structured function for conducting the screening interview

        Inputs: 
            talent: TalentProfile
                The users talent profile 
            job: Job
                Job model which includes information about the specific job
            transcript_messages : list
                The transcript messages meant for the bot and the user
            conversation_history : list
                The conversation history the bot will be using
            client : OpenAI
                The way to API call the bot
        
        Returns:
            None
        '''
        start_time = time.time()
        max_time = 15 * 60  # max time in seconds 
        warning_flag = False
        relocation_flag = False
        relocation_reconsideration_flag = False

        job_locations = job.locations.all()  # get all job locations
        talent_locations = talent.locations.all() # get all talent location
        curr_location = talent_locations[0].display_name if talent_locations else "Unknown" # get curr location in case of location update
        #print("TEST, CURR_LOCATION:", curr_location)

        distances = calculate_distance(job_locations, talent_locations)
        min_dist = min(distances, key=lambda x: x[2])[2] #sort by dist, get min

        # creating interview obj 
        interview = Interview.objects.create(candidate=talent, job=job,
                                             start = timezone.now(),  # start time
                                             status=InterviewStatusChoices.SCHEDULED)

        bot_reply = "" 

        while True:
            if  warning_flag == False and time.time() - start_time >= max_time - 60:
                warning_msg = "Warning: The interview will end in 1 minute."
                print(warning_msg) #remove later
                update_history("assistant", conversation_history, transcript_messages, warning_msg)
                warning_flag = True

            if time.time() - start_time >= max_time:
                timed_ending_msg = "Time is up! Ending the interview now."
                print(timed_ending_msg) #remove later
                update_history("assistant", conversation_history, transcript_messages, timed_ending_msg)
                finalize_interview(interview, transcript_messages, talent, client)
                break
            
            print("You: ", end='', flush=True)
            user_input = get_user_input()
            update_history("user", conversation_history, transcript_messages, user_input)

            if user_input.lower() == "exit": 
                goodbye_msg = "Goodbye! have a great day."
                print(goodbye_msg) # remove later
                update_history("assistant", conversation_history, transcript_messages, goodbye_msg)
                finalize_interview(interview, transcript_messages, talent, client)
                break

            if bot_reply and ("currently located" in bot_reply.lower().strip() or "current location" in bot_reply.lower().strip()):
                print("TEST: processing location change")
                updated_location, updated_dist = process_location_update(user_input, job_locations)

                if updated_location != "Invalid": 
                    curr_location = updated_location
                    min_dist = updated_dist
                    print(f"updated current location to {curr_location}")

            # asking the first relocation question
            if bot_reply and ("open to relocating" in bot_reply.lower().strip() or "willing to commute" in bot_reply.lower().strip() or "open to moving" in bot_reply.lower().strip()) and min_dist > 50:
                    if user_input.lower().strip() in ["no", "i can't", "not willing to relocate", "nope", "not sure"]:
                        reconsideration_msg = "Are you sure? This may mean you are not eligible for this position."
                        print("Interviewer:", reconsideration_msg) # remove later
                        update_history("assistant", conversation_history, transcript_messages, reconsideration_msg)
                        bot_reply = reconsideration_msg
                        relocation_flag = True
                        continue

            # reconsideration relocation msg
            # ends interview if response to relocation question is no AFTER reconsidering, 
            # or moves on and raises flag for hiring manager if answer changes.
            if relocation_flag:
                if user_input.lower().strip() in ["yes", "yeah", "correct", "that's right"]:
                    final_msg = "Thank you for confirming. Unfortunately, we cannot proceed further since the job requires relocation/commuting."
                    print("Interviewer:", final_msg) # remove later
                    bot_reply = final_msg
                    update_history("assistant", conversation_history, transcript_messages, final_msg)
                    finalize_interview(interview, transcript_messages, talent, client)
                    return
                    

                elif user_input.lower().strip() in ["no", "actually, i can", "i changed my mind"]:
                    confirmation_msg = "Thanks for clarifying! Let's move on."
                    print("Interviewer:", confirmation_msg) #remove later
                    update_history("assistant", conversation_history, transcript_messages, confirmation_msg)
                    bot_reply = confirmation_msg
                    relocation_flag = False 
                    relocation_reconsideration_flag = True #flag for HR
         
            try:

                bot_response = get_bot_response(client, conversation_history=conversation_history, tools=[end_interview()])
                #print(bot_response.content)

                if bot_response.content:
                    content = bot_response.content.strip()

                    # if response contain more than 1 obj
                    if content.count("{") > 1 and content.count("}") > 1:
                        first_json_obj = content.split("\n")[0].strip() # get first one only
                        parsed = json.loads(first_json_obj)
         
                    else: 
                        parsed = json.loads(content)

                    bot_reply = parsed["question"]
                    category = parsed["category"]
                    print("\nInterviewer:", bot_reply)
                    update_history("assistant", conversation_history, transcript_messages, bot_reply, category)
                else:
                   print("tool called, ending the interview.")
                   #print(bot_response)


                #bot_reply = bot_response.content 
                bot_tools = bot_response.tool_calls
                # print("\nInterviewer:", bot_reply)
                # update_history("assistant", conversation_history, transcript_messages, bot_reply)

                # Check for function call by model
                # End interview and print summary if found
                if bot_tools:
                    end = False
                    for tool_call in bot_tools:
                        name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        if name == "end_interview":
                            # In a non-terminal version, this would be saved to a database, not shown to interviewee
                            print("\nInterviewer [For admin]:", args["summary"]) 
                            interview_summary =  args["summary"] # store this somewhere in db later
                            end = True
                    if end:
                        finalize_interview(interview, transcript_messages, talent, client)
                        break

            except Exception as e:
                print("Error communicating with OpenAI API:", str(e))
                print("Raw bot response:", repr(bot_response.content))


def finalize_interview(interview: Interview , transcript_messages:list, talent: TalentProfile, client:OpenAI) -> None :
    """
    Finalizes the interview by marking it as "awaiting feedback", saving the end time,
    and writing the conversation transcript to the database and a jason file.

    Inputs:
        interview: Interview object to be updated.
        transcript_messages (list): List of messages during the interview.
        talent: TalentProfile representing the candidate.
        client: OpenAI
                The way to API call the bot

    Returns:
        None
    """
    interview.end = timezone.now() 
    interview.status = InterviewStatusChoices.AWAITING_FEEDBACK   #update status
    interview.save() # update db

    # store in jason
    write_to_transcript(talent.user.id, talent.user.first_name, messages=transcript_messages)

    # store in db
    write_transcript_to_db(interview, transcript_messages)

    print("TESTING: transcript stored sucessfully!!!")

    score_interview(interview, client=client)
    print("TESTING: Scoring complete.")

