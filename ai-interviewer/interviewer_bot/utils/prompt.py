import django
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from jobs.models import Job
from profiles.models import TalentProfile
from .distances import calculate_distance
import random

def location_prompt(min_dist : int, remote_option : bool) -> list[str]:

    questions = [
        "Ask Where are they currently located? If there is a specific location you find on their resume, ask if they are still located at said location. if there are multiple locations listed in their profile, ask which one is their current location",
    ]

    if min_dist > 50 and remote_option == 0:
        questions.append("the job location is more than 50 miles from the candidate's current location and job is not offered remotely, Ask if they are open to relocating")
    elif min_dist < 50 and remote_option == 0:
        questions.append("the job location is within 50 miles from the candidate's current location and job is not offered remotely, Ask if they are willing to commute to the office?")
    elif min_dist > 50 and remote_option == 1:
        questions.append("the job location is more than 50 miles from the candidate's current location and job is offered remotely, Ask if they are okay with remote work? ask about their timezone.")
    elif min_dist < 50 and remote_option == 1:
        questions.append("the job location is within 50 miles from the candidate's current location and job is offered remotely, Ask if if they want to work remote or commute to the office? ")

    return questions

def availability_prompt() -> list[str]:
    return ["Ask When they are available to start the job, and for how long?", 
            "Ask Whether they are open to full-time, part-time, or internship roles"]
    

# def schedule_prompt() -> list[str]:
#     return ["Ask about their preferred work schedule and if they are flexible with hours", 
#             "Ask how do they plan to manage your time effectively, If this role is hybrid/remote"]
    
    
def academic_background_prompt() -> list[str]:
    return ["Using the academic information from the resume,  Ask about about their current academic status.", 
            "Using the information from the resume,, Ask how their educational background [X] (listed in the provided resume) aligns with this role"]


def interest_prompt() -> list[str]:
    return ["Using the job description and company details, ask What attracts them to the company [X] (listed in job description)", 
    " Ask What attracts them to the company [X](listed in job description) and How does it fit with their career goals?"]
    

def prev_experience_prompt() -> list[str]:
    return ["Based on the candidate's previous roles listed in the resume: Ask about any of their previous experience at their previous Company [X] (listed in the provided resume).",
    "Based on the candidate's previous roles listed in the resume:  Ask What skills did they gain from their past experience that will be valuable in this role?",
    "Based on the candidate's previous roles listed in the resume: Ask How do those skills apply to the responsibilities listed in this role?" ]


# def teamwork_prompt() -> list[str]:
#     return ["Ask them about a time when you worked in a team? What was their role, and how did they contribute?",
#             "Ask How do they handle conflicts or disagreements within a team?"]

# def communication_prompt() -> list[str]:
#     return ["Ask How do they typically communicate in a remote or hybrid work environment?",
#             "Aske about a time when they had to explain a complex idea to someone without a technical background."]
    

# def preference_prompt() -> list[str]:
#     return ["Ask if they prefer working on multiple smaller tasks at once, or focusing on one large task at a time?", 
#             "Ask What type of work environment helps them stay productive and engaged?" ]


PROMPT_DICT = {#"location"            : location_prompt(), 
               "availability"        : availability_prompt(), 
               #"schedule"            : schedule_prompt(),  
               "academic_background" : academic_background_prompt(),
               "interest"            : interest_prompt(),
               "experience"          : prev_experience_prompt(), 
               #"teamwork"            : teamwork_prompt(), 
               #"communication"       : communication_prompt(), 
               #"preference"          : preference_prompt()
               }


def start_interview_prompt(job: Job, talent: TalentProfile) -> str:
    ''' 
    Initial Prompt for the AI which includes the prompt strings

    Inputs: 
        job : Job
            Job model which includes information about the specific job
        talent: TalentProfile
             TalentProfile model which includes information about the talent and their resume  

    Returns: 
        String
            Returns the inital prompting string which the AI will input
    '''
    job_locations = job.locations.all()  # get all job locations
    talent_locations = talent.locations.all() # get all talent location
    job_location_names = ", ".join([loc.display_name for loc in job_locations])
    talent_location_names = ", ".join([loc.display_name for loc in talent_locations])

    file_string =  f"""You are a professional AI interviewer, designed to conduct a screening interview.
    Greet the candidate warmly and introduce yourself as the AI interviewer.
    Briefly explain the structure of the interview: this will focus on your background, availability, and fit for the job.
    Mention that no deep technical questions will be asked at this stage. It's primarily a logistical and cultural fit conversation.
    Absolutely never ask more than one question at a time.
    Take the information from their resume to tailor/personalize the questions for the candidate.
    Ask structured interview questions based on the candidate's resume and predefined topics and Keep the conversation focused and relevant.
    Make sure that interview questions asked are dynamically generated and personalized based on the job information and candidate information provided below.
    Change the wording in the following questions to sound natural and adjust tone and language to give a more conversational experience.
    If the candidate does not fully answer the question, do not proceed. Politely rephrase and ask again until they provide a complete response. Do not move forward until the current question is fully answered.
    Do not proceed to the next question until you have confirmed that the previous question has been fully answered.

    --- Job Information ---
    **Job Title:** {job.title}
    **Job Remote Option:** {job.remote_option}
    **Job Location(s):** {job_location_names}
    **Job Description:** {job.description}

    --- Candidate Information ---
    **Candidate Name:** {talent.user.first_name} {talent.user.last_name}
    **Candidate location:** {talent_location_names}
    **Candidate Resume Summary:**{talent.resume.clean_text}
    """
    file_string += """Closing the Interview:
    Summarize key points discussed in the interview, particularly around availability and interest in the role.
    Thank them for their time and inform them about the next steps in the process (e.g., scheduling follow-up 
    interviews or informing them about the selection process). 
    Call the end_interview function.
    
    Ask ONE QUESTION AT TIME. Don't explain answers just keep it brief."""

    file_string += "\nBefore starting, give a short summary of the job description and the candidate's resume." # For testing

    file_string += "\nONLY CALL THE END_INTERVIEW TOOL IF MOST OF THE KEY CATEGORIES ARE ASKED"

    #print(file_string) #TESTING
    
    return file_string
