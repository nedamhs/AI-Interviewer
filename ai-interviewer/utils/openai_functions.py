def end_interview() -> dict:
    return {
        "type": "function",
        "function":
        {
            "name": "end_interview",
            "description": "Ends the interview and returns a summary of the interview and how strong the candidate is.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string",}
                },
                "required": [
                    "summary"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }

# not using this 

# def get_question_tool():
#     """
#     Returns the OpenAI tool schema for structured interview questions.
#     """
#     return [
#         {
#             "type": "function",
#             "function": {
#                 "name": "ask_question",
#                 "description": "Ask the candidate a structured interview question, based on their provided context. Feel free to include friendly, conversational transitions in your response *before* calling the tool.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "category": {
#                             "type": "string",
#                             "description": "Category of the question. Choose from: location, availability, schedule, academic_background, interest, prev_experience, teamwork, communication, preference"
#                         },
#                         "question": {
#                             "type": "string",
#                             "description": "The interview question to ask the candidate."
#                         }
#                     },
#                     "required": ["category", "question"]
#                 }
#             }
#         }
#     ]
