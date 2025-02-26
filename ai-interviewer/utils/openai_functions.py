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