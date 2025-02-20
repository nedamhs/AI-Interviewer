import time
import sys
from select import select
import msvcrt
import platform

def get_user_input(timeout: int = 5 * 60, warning_time: int = 60 ) -> str:
    '''
    Timed input system for the user, will timeout if the user takes greater than the timeout time to respond. This function will 
    send a timeout warning when [warning_time] seconds remain.
    
    TODO:
        Change for getting the input from the webapp rather than the terminal app  
        Penalize users for taking too long to respond
        Change how the exit case works if the user takes too long to respond 

    Inputs:
        timeout : Int 
            Timeout time in seconds, currently set to 5 minutes... note to adjusting time, 
            ensure the timeout time is longer than the warning time
        warning_time : Int 
            Warning time in seconds, this will alert the user how long is left for the question before timeout, 
            currently set to 1 minute
            
    Returns: 
        String
            Either will be the user input or the exit case
    '''
    warning_message = f"Interviewer: Hello are you there? This interview will timeout if no response is given in {warning_time} seconds."
    input_time = time.time()

    # print("You:", end= " ")
    while (time.time()-input_time) < timeout:
        if platform.system() == "Windows":
            if msvcrt.kbhit():
                return sys.stdin.readline().strip()
        else:
            ready_for_input, _, _ = select([sys.stdin], [], [], 1)
            if ready_for_input:
                return sys.stdin.readline().strip()
        
        if warning_time >= timeout - (time.time() - input_time):
            print(f"\n{warning_message} \nYou:", end = " ")
            warning_time = -1 

    
    print("\nUser did not respond in time, thank you for your time.", end= ' ')
    return "exit"

def update_history(role:str, conversation_history: list, transcript: list, input: str) -> None:
    """
    Update the conversation history and the transcript by adding input into it 

    Inputs: 
        role : str 
            The role of whoever is speaking (user or assistant)
        conversation_history : list
            The total conversation history which will be updated
        transcript : list 
            The total transcript which will be updated
        input : str 
            The inputted message
    
    Returns: 
        None
    """
    conversation_history.append({"role": role, "content": input})
    transcript.append({"role": role,"content": input,"time": time.strftime("%H:%M:%S", time.localtime())})