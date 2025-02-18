from openai import OpenAI
import os

def get_client() -> OpenAI:
    '''
    Initalizes an instance of the client and returns it to the requested source 

    Inputs:
        None

    Returns:
        client : OpenAI
            returns the client used to send api calls  
    '''
    client = OpenAI(
        api_key=os.environ.get("OPENAI-API-KEY"),
    )
    return client 

def get_bot_response(client: OpenAI, conversation_history: list, model_type: str = "gpt-4o-mini") -> str:
    '''
    Gives the bot conversation history and then sends back a reply to the user. 

    Inputs: 
        client : OpenAI
            Uses the client to send the call
        conversation_history : list
            Gives the AI bot conversation history in list
        model_type : str
            Allows the function callers the option to change the model type if need be

    Returns: 
        String
            Extracts the response which is a string
    '''
    response = client.chat.completions.create(
                messages=conversation_history,
                model=model_type,
            )
    return response.choices[0].message.content