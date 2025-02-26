import django
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from jobs.models import Job
from profiles.models import TalentProfile
from .distances import calculate_distance

def prompt_string(min_dist : int, remote_option : bool) -> str:
    '''
    Function called in chatbot.py to provide prompt as a string to API call.
 
    Inputs:
        min_dist : int
        remote_option : bool
     
    Returns: 
        String
            Returns a prompt for openai to follow 
    '''
    return f"""Follow these guidelines:

    Introduction:
    Greet the candidate warmly and introduce yourself as the AI interviewer.
    Briefly explain the structure of the interview: this will focus on your background, availability, and fit for the job.
    Mention that no deep technical questions will be asked at this stage. It's primarily a logistical and cultural fit conversation.
    Only ask one question at a time.
    Take the information from their resume to tailor/personalize the questions for the candidate.
    Logistics and Availability:
    Location and Work Setup:

    Ask Where are they currently located? If there is a specific location you find on their resume, ask if they are still located at said location
    
    {"the job location is more than 50 miles from the candidate's current location and job is not offered remotely ",
     "ask if they are open to relocating" if (min_dist > 50 and remote_option == 0) else ""}
    {"the job location is within 50 miles from the candidate's current location and job is not offered remotely ",
     "ask if they are willing to commute to the office?" if (min_dist < 50 and remote_option == 0) else ""}
    {"the job location is more than 50 miles from the candidate's current location and job is offered remotely ",
    "ask if they are okay with remote work? ask about their timezone." if (min_dist > 50 and remote_option == 1) else ""}
    {"the job location is within 50 miles from the candidate's current location and job is offered remotely ",
    "ask if if they want to work remote or commute to the office?" if (min_dist < 50 and remote_option == 1) else ""}

    Ask When they are available to start the job, and for how long?
    Ask if they are available to work full-time for the job?
    Work Schedule:

    Ask about their preferred work schedule and if they are flexible with hours
    Ask how do you plan to manage your time effectively, If this role is hybrid/remote
    Candidate's Background and Interests:
    Academic Background:

    Ask about about their current academic status and your major
    Ask What they are currently studying, and how it aligns with this role
    Interest in the company:

    Ask What attracts them to our company and How does it fit with your career goals?
    Previous work Experience:

    Ask about any of their previous experience at their previous Company X (listed in the provided resume).

    ASk if they have any previous work experiences, If yes, Ask about their role
    Ask What skills did they gain from their past experience that will be valuable in this role?
    Cultural Fit and Soft Skills:
    Teamwork:

    Ask them about a time when you worked in a team? What was their role, and how did they contribute?
    Ask How do they handle conflicts or disagreements within a team?
    Communication Skills:

    Ask How do they typically communicate in a remote or hybrid work environment?
    Aske about a time when they had to explain a complex idea to someone without a technical background.
    Work Preferences:

    Ask if they prefer working on multiple smaller tasks at once, or focusing on one large task at a time
    Ask What type of work environment helps them stay productive and engaged?
    Closing the Interview:
    Summarize key points discussed in the interview, particularly around availability and interest in the role.
    Thank them for their time and inform them about the next steps in the process (e.g., scheduling follow-up interviews or informing them about the selection process).
    Call the end_interview function.
    
    Ask similar questions one by one. Don't explain answers just keep it brief."""


def start_interview_prompt(job: Job, talent: TalentProfile) -> str:
    ''' 
    Initial Prompt for the AI which includes the large prompt string

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
    min_dist = min(distances, key=lambda x: x[2])[2] #sort by dist, get min

    file_string =  f"""You are a professional AI interviewer, designed to conduct a screening interview.
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
    Here are the instructions and key interview topics to be covered: {prompt_string(min_dist, job.remote_option)}
    """

    file_string += "\nBefore starting, give a short summary of the job description and the candidate's resume." # For testing

    #print(file_string) #TESTING
    
    return file_string