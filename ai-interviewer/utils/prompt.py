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

def location_prompt(min_dist : int, remote_option : bool) -> str:

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

    return "\n".join(questions)

def availability_prompt() -> str:
    return """ Ask When they are available to start the job, and for how long?
    Ask if they are available to work full-time for the job? """.strip()

def schedule_prompt() -> str:
    return """ Ask about their preferred work schedule and if they are flexible with hours
    Ask how do you plan to manage your time effectively, If this role is hybrid/remote """.strip()
    
def academic_background_prompt() -> str:
    return """Ask about about their current academic status and your major
    Ask What they are currently studying, and how it aligns with this role""".strip()

def interest_prompt() -> str:
    return """Ask What attracts them to our company and How does it fit with your career goals?""".strip()

def prev_experience_prompt() -> str:
    return """Ask about any of their previous experience at their previous Company X (listed in the provided resume).
              ASk if they have any previous work experiences, If yes, Ask about their role
              Ask What skills did they gain from their past experience that will be valuable in this role?""".strip()

def teamwork_prompt() -> str:
    return """Ask them about a time when you worked in a team? What was their role, and how did they contribute?
    Ask How do they handle conflicts or disagreements within a team?""".strip()

def communication_prompt() -> str:
    return """Ask How do they typically communicate in a remote or hybrid work environment?
    Aske about a time when they had to explain a complex idea to someone without a technical background.""".strip()

def preference_prompt() -> str:
    return """ Ask if they prefer working on multiple smaller tasks at once, or focusing on one large task at a time?
    Ask What type of work environment helps them stay productive and engaged?""".strip()

def randomize_prompts() -> list[str]:
    """
    Randomizes the order of a list of predefined prompt functions.

    This function calls various prompt-generating functions and shuffles their order 
    before returning them in a randomized list. 

    Returns:
        list: A shuffled list of prompts.
    """
    prompt_list = [
    availability_prompt(),
    schedule_prompt(), 
    academic_background_prompt(),
    interest_prompt(), 
    prev_experience_prompt(), 
    teamwork_prompt(), 
    communication_prompt(), 
    preference_prompt()]

    random.shuffle(prompt_list)

    return prompt_list

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

    distances = calculate_distance(job_locations, talent_locations)
    print("distances : ", distances) #testing! remove later
    if distances: 
        min_dist = min(distances, key=lambda x: x[2])[2] #sort by dist, get min

    file_string =  f"""You are a professional AI interviewer, designed to conduct a screening interview.
    Greet the candidate warmly and introduce yourself as the AI interviewer.
    Briefly explain the structure of the interview: this will focus on your background, availability, and fit for the job.
    Mention that no deep technical questions will be asked at this stage. It's primarily a logistical and cultural fit conversation.
    **Only ask one question at a time, even if the next question you want to ask is related to the one being asked.**
    Take the information from their resume to tailor/personalize the questions for the candidate.
    Ask structured interview questions based on the candidate's resume and predefined topics and Keep the conversation focused and relevant.
    Make sure that interview questions asked are dynamically generated and personalized based on the job information and candidate information provided below.

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

    file_string += location_prompt(min_dist, job.remote_option )  
    file_string += f"\n\n".join(randomize_prompts())     # other prompts in random order

    file_string += """Closing the Interview:
    Summarize key points discussed in the interview, particularly around availability and interest in the role.
    Thank them for their time and inform them about the next steps in the process (e.g., scheduling follow-up 
    interviews or informing them about the selection process). 
    Call the end_interview function.
    
    Ask similar questions one by one. Don't explain answers just keep it brief."""

    file_string += "\nBefore starting, give a short summary of the job description and the candidate's resume." # For testing
    #print(file_string) #TESTING
    
    return file_string