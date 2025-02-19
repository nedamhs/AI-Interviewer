import json
import time

def write_to_transcript(id: int, user: str, messages: list) -> None:
    '''
    Creates a dictionary, converts it to a json object and writes to a json file
    
    Inputs:
        id : Int 
            Conversation id to link a screening interview transcript to a user
        user : User
            Links the users first name to the transcript 
        messages : list
            transcript of the message history and who said what during the interview

    Returns: 
        None    
    '''
    transcript = { "conversation_id": id, "interviewee": user, "messages": messages}
    json_obj = json.dumps(transcript, indent=4)
    with open("transcript.json", "w") as file:
        file.write(json_obj)

