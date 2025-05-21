import time
import json
import django
import os
import asyncio
from .openai_functions import end_interview
from .transcript import write_to_transcript, write_transcript_to_db
from .bot import get_bot_response
from .inputs import get_user_input,update_history
from profiles.models import TalentProfile
from jobs.models import Job
from locations.models import Location
from .distances import calculate_distance
# from audio_utils.text_to_speech import text_to_audio
# from audio_utils.audio_transcriber import Transcriber
from openai import OpenAI
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
from .evaluator import  evaluate_response_action
from .prompt import *
from .HR_report import generate_report_components


def conduct_interview(interview: Interview, talent: TalentProfile, job: Job,  transcript_messages:list, conversation_history:list, client:OpenAI) -> None:
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
            meeting_bot: MeetingBot
                Meeting bot that is running zoom meeting
        
        Returns:
            None
        '''
        #get start time from obj, convert to float
        start_time = interview.start.timestamp()  
        max_time = 15 * 60  # max time in seconds 
        warning_flag = False

        bot_reply = "" 
        
        items = list(PROMPT_DICT.items())
        random.shuffle(items)

        for category, questions in items: 
            #print(f"\nTESTING: CURRENT CATEGORY: {category}")
            category_q_a_pairs = "" 

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
                return
            
            try: 
                for question in questions: 
                    instruction =  f""" you are an ai interviewer, ask the following interview question in a friendly and personalized way:
                     Take the information from their resume to tailor/personalize the questions for the candidate.{question}
                     before asking the question, provide feedback on previous response given by the user."""

                    conversation_history.append({"role": "user", "content": instruction})
                    bot_response = get_bot_response(client, conversation_history, tools=[end_interview()])

                    if bot_response.content: 
                       bot_reply = bot_response.content
                       print("\nInterviewer:", bot_reply)
                       update_history("assistant", conversation_history, transcript_messages, bot_reply, category=category)
                    else: 
                       print("no response")
                       print("tool called, ending the interview.")


                    bot_tools = bot_response.tool_calls

                    if bot_tools:
                        end = False
                        for tool_call in bot_tools:
                            name = tool_call.function.name
                            args = json.loads(tool_call.function.arguments)

                            if name == "end_interview":
                                  print("\nInterviewer [For admin]:", args["summary"]) 
                                  interview_summary =  args["summary"]
                                  interview.summary = interview_summary # store in db
                                  end = True
                            if end:
                                finalize_interview(interview, transcript_messages, talent, client)
                                return

                    print("You: ", end='', flush=True)
                    user_input = get_user_input()
                    update_history("user", conversation_history, transcript_messages, user_input)

                    # append q,a to current category transcript
                    category_q_a_pairs += f"Q: {question}\nA: {user_input}\n\n"

                    if user_input.lower() == "exit": 
                         goodbye_msg = "Goodbye! have a great day."
                         print(goodbye_msg) # remove later
                         update_history("assistant", conversation_history, transcript_messages, goodbye_msg)
                         finalize_interview(interview, transcript_messages, talent, client)
                         return

                action = None   #? 
                action, followup_suggestion = evaluate_response_action(client, category, category_q_a_pairs)
                if action in ["follow_up", "re_ask"] and followup_suggestion:
                            print("\nInterviewer (follow-up):", followup_suggestion)
                            update_history("assistant", conversation_history, transcript_messages, followup_suggestion, category=category)

                            print("You: ", end='', flush=True)
                            user_input = get_user_input()
                            update_history("user", conversation_history, transcript_messages, user_input)

                            if user_input.lower() == "exit": 
                                   goodbye_msg = "Goodbye! have a great day."
                                   print(goodbye_msg) # remove later
                                   update_history("assistant", conversation_history, transcript_messages, goodbye_msg)
                                   finalize_interview(interview, transcript_messages, talent, client)
                                   return  

            except Exception as e:
                    print(f"Interviewer: (Error generating question): {e}")
                    continue
        
        finalize_interview(interview, transcript_messages, talent, client)



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

    generate_report_components(interview, client=client)
