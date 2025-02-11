from dotenv import load_dotenv
from openai import OpenAI
import os
import django

load_dotenv()
def file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        return None

# function for conducting ai interview in terminal
# takes on job and resume model objects
def conduct_ai_interview(job, resume):
    # fetch prompt from text file
    file_path = "ai-interviewer\\prompt.txt"
    file_string = file_to_string(file_path)
    
    # append job and resume
    # TODO: remake this with prompt engineering for better resume and job prompt
    file_string += "\nJob description: " + job.description
    file_string += "\nCandidate Name: " + resume.data['first_name'] + " " + resume.data['last_name']
    file_string += "\nCandidate Resume: " + resume.clean_text

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
    print("Interviewer: ", bot_reply)

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit": # remove later
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                messages=conversation_history,
                model="gpt-4o-mini",
            )
            bot_reply = response.choices[0].message.content
            print("Interviewer:", bot_reply)

            conversation_history.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            print("Error communicating with OpenAI API:", str(e))


# ran as a script
if __name__ == "__main__":
    # setup django and models (only when ran as a script)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    from jobs.models import Job
    from documents.models import Resume

    # function for conducting a interview with a random job and resume
    # function only if ran from command line
    def conduct_random_interview():
        # fetch random job and resume from database
        rand_job = Job.objects.order_by('?').first()
        rand_resume = Resume.objects.order_by('?').first()

        print("Conducting a random interview for the position " + rand_job.title + ". The candidate's name is " + rand_resume.data["first_name"] + ".")

        conduct_ai_interview(rand_job, rand_resume)

    conduct_random_interview()
