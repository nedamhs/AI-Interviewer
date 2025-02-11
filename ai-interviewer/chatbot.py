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


def chat_with_gpt():
    client = OpenAI(
        api_key=os.environ.get("OPENAI-API-KEY"),
    )

    file_path = "ai-interviewer\\prompt.txt"
    file_string = file_to_string(file_path)
    print("AI Interviewer")
    conversation_history = []
    conversation_history.append({"role": "system", "content": file_string})

    response = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-4o",
    )

    bot_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": bot_reply})

    print("AI:", bot_reply)
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                messages=conversation_history,
                model="gpt-4o",
            )
            bot_reply = response.choices[0].message.content
            print("AI:", bot_reply)

            conversation_history.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            print("Error communicating with OpenAI API:", str(e))

if __name__ == "__main__":
    chat_with_gpt()
