from dotenv import load_dotenv
from openai import OpenAI
from select import select
from prompt import prompt_string
import os
import django
import time
import sys
import json

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from jobs.models import Job
from documents.models import Resume

def get_user_input(timeout: int = 5 * 60, warning_time: int = 60 ):
    '''
    Timed input system for the user, will timeout if the user takes greater than the timeout time to respond. This function will 
    send a timeout warning when [warning_time] seconds remain.
    
    TODO:
        Change for getting the input from the webapp rather than the terminal app  
        Penalize users for taking too long to respond
        Change how the exit case works if the user takes too long to respond 

    Inputs:
        timeout : Int 
            Timeout time in seconds, currently set to 5 minutes... note to adjusting time, 
            ensure the timeout time is longer than the warning time
        warning_time : Int 
            Warning time in seconds, this will alert the user how long is left for the question before timeout, 
            currently set to 1 minute
            
    Returns: 
        String
            Either will be the user input or the exit case
    '''
    warning_message = f"Interviewer: Hello are you there? This interview will timeout if no response is given in {warning_time} seconds."
    input_time = time.time()

    # print("You:", end= " ")
    while (time.time()-input_time) < timeout:
        ready_for_input, _, _ = select([sys.stdin], [], [], 1)
        if warning_time >= timeout - (time.time() - input_time):
            print(f"\n{warning_message} \nYou:", end = " ")
            warning_time = -1 
        if ready_for_input: 
            return sys.stdin.readline().strip()

    
    print("\nUser did not respond in time, thank you for your time.", end= ' ')
    return "exit"

# writes all messages to json transcript
def write_to_transcript(id, user, messages):
    # creates dictionary, converts it to json object then writes to json file
    transcript = { "conversation_id": id, "interviewee": user, "messages": messages}
    json_obj = json.dumps(transcript, indent=4)
    with open("transcript.json", "w") as file:
        file.write(json_obj)

# function for conducting ai interview in terminal
# takes on job and resume model objects
def conduct_ai_interview(job, resume):  
    file_string =  f"""You are a professional AI interviewer, designed to conduct a screening interview.
    Ask structured interview questions based on the candidate's resume and predefined topics and Keep the conversation focused and relevant.
    Make sure that interview questions asked are dynamically generated and personalized based on the job information and candidate information provided below.
    --- Job Information ---
    **Job Title:** {job.title}
    **Job Description:** {job.description}
    **Job Remote Option:** {job.remote_option}

    --- Candidate Information ---
    **Candidate Name:** {resume.data['first_name']} {resume.data['last_name']}
    **Candidate Resume Summary:**
    {resume.clean_text}
    Here are the instructions and key interview topics to be covered: 
    {prompt_string()}
    """
    file_string += "\nBefore starting, give a short summary of the job description and the candidate's resume." # For testing

    # transcript
    messages = []
    # conversation history for llm
    conversation_history = []
    conversation_history.append({"role": "system", "content": file_string})

    # openai setup
    client = OpenAI(
        api_key=os.environ.get("OPENAI-API-KEY"),
    )

    # first message
    response = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-4o-mini",
    )
    bot_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "assistant","content": bot_reply,"time": time.strftime("%H:%M:%S", time.localtime())})
    print("Interviewer: ", bot_reply)

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
            write_to_transcript(resume.id, resume.data['first_name'], messages=messages)
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})
        messages.append({"role": "user","content": user_input,"time": time.strftime("%H:%M:%S", time.localtime())})
        
        try:
            response = client.chat.completions.create(
                messages=conversation_history,
                model="gpt-4o-mini",
            )
            bot_reply = response.choices[0].message.content
            print("Interviewer:", bot_reply)

            conversation_history.append({"role": "assistant", "content": bot_reply})
            messages.append({"role": "assistant","content": bot_reply,"time": time.strftime("%H:%M:%S", time.localtime())})
        except Exception as e:
            print("Error communicating with OpenAI API:", str(e))


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
