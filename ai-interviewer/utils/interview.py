import time
from .transcript import write_to_transcript
from .bot import get_bot_response
from .inputs import get_user_input,update_history
from openai import OpenAI
import django
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from documents.models import Resume

def conduct_interview(resume: Resume, transcript_messages:list, conversation_history:list, client:OpenAI) -> None:
        '''
        Main structured function for conducting the screening interview

        Inputs: 
            resume : Resume 
                The users resume 
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

        while True:
            if  warning_flag == False and time.time() - start_time >= max_time - 60:
                print("Warning: The interview will end in 1 minute.")
                warning_flag = True

            if time.time() - start_time >= max_time:
                print("Time is up! Ending the interview now.")
                break
            
            print("You: ", end='', flush=True)
            user_input = get_user_input()
            if user_input.lower() == "exit": # remove later
                write_to_transcript(resume.id, resume.data['first_name'], messages=transcript_messages)
                print("Goodbye!")
                break

            update_history("user", conversation_history, transcript_messages, user_input)
            
            try:
                bot_reply = get_bot_response(client, conversation_history=conversation_history)
                print("Interviewer:", bot_reply)

                update_history("assistant", conversation_history, transcript_messages, bot_reply)
            except Exception as e:
                print("Error communicating with OpenAI API:", str(e))