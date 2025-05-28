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


def get_bot_response(client: OpenAI, conversation_history: list, model_type: str = "gpt-4o", tools: list = [], tool_choice: dict = None) -> dict:
    '''
    Gives the bot conversation history and then sends back a reply to the user. 

    Inputs: 
        client : OpenAI
            Uses the client to send the call
        conversation_history : list
            Gives the AI bot conversation history in list
        model_type : str
            Allows the function callers the option to change the model type if need be
        tools : 
            list of tools (optional)
        tool_choice : 
             dict (optional) → enforce specific tool usage

    Returns: 
            OpenAI message object
    '''
    response = client.chat.completions.create(
                messages=conversation_history,
                model=model_type,
                tools=tools,
                #tool_choice=tool_choice, # useful for multiple tools
                # response_format = {"type": "json_schema",
                #                    "json_schema": {
                #                          "name": "ask_question",
                #                          "schema": {
                #                             "type": "object",
                #                                "properties": {
                #                                     "category": {
                #                                         "type": "string",
                #                                         "description": "Category of the question. Choose ONLY ONE from: location, availability, schedule, academic_background, interest, prev_experience, teamwork, communication, preference",
                #                                         "enum" : ["location","availability","schedule","academic_background","interest","prev_experience","teamwork","communication","preference"]
                #                                     },
                #                                     "question": {
                #                                         "type": "string",
                #                                        "description": "The interview question to ask the candidate."
                #                                     }
                #                                 },
                #                                 "required": ["category", "question"],
                #                                 "additionalProperties": False
                #                         }
                #                         ,
                #                     "strict": True
                #                      }
                #                     }
             )

    return response.choices[0].message
    
