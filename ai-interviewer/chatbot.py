from dotenv import load_dotenv
from openai import OpenAI
import os

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


def conduct_ai_interview():
    
    # fetch prompt from text file
    file_path = "ai-interviewer\\prompt.txt"
    file_string = file_to_string(file_path)
    
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

if __name__ == "__main__":
    conduct_ai_interview()
