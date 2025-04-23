import requests
import os
import base64
import json
import webbrowser
from datetime import datetime, timedelta
from dotenv import load_dotenv

# load .env file 
load_dotenv()

# get creds from .env variables
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# validate the credentials
if not all([ACCOUNT_ID, CLIENT_ID, CLIENT_SECRET]):
    print("Error: Ensure ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, and ZOOM_CLIENT_SECRET environment variables are set in the .env file.")
    exit()

# Zoom API endpoint for creating a meeting (use 'me' for the user associated with the app)
CREATE_MEETING_URL = "https://api.zoom.us/v2/users/me/meetings"
# Zoom OAuth token URL
TOKEN_URL = "https://zoom.us/oauth/token"

def get_access_token() -> str:
    """
    
    Function to obtain a S2S OAuth access token from Zoom.
    
    """
    try:
        # Prepare credentials for Basic Auth
        message = f"{CLIENT_ID}:{CLIENT_SECRET}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        headers = {
            'Authorization': f'Basic {base64_message}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'account_credentials',
            'account_id': ACCOUNT_ID
        }

        print("Requesting Access Token...")
        response = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4XX or 5XX)

        token_data = response.json()
        print("Access Token received.")
        return token_data.get('access_token')

    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during token retrieval: {e}")
        return None


def create_zoom_meeting(token) -> dict:
    """
    
    Creates a new Zoom meeting using the access token.
    
    """
    if not token:
        print("Cannot create meeting without an access token.")
        return None

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    meeting_details = {
        "topic": "Pairwise Screening Interview",
        "type": 2,
        "start_time": "2025-04-23T07:15:00Z", # CHANGE THIS TO A FUTURE TIME 
        "duration": 60,
        "timezone": "America/Los_Angeles",
        "password": "pairwise",
        "settings": {
            "host_video": True,
            "participant_video": False,
            "join_before_host": True,
            "mute_upon_entry": True,
            "waiting_room": False,
            "password" : "balls",
            "audio": "both", # 'voip', 'telephony', 'both'
            "auto_recording": "none", # 'local', 'cloud', 'none',
            "meeting_authentication": False # makes sure that only authenticated users can join the meeting
            }
    }

    # For Instant Meeting (type 1), remove start_time if present
    if meeting_details["type"] == 1 and "start_time" in meeting_details:
        del meeting_details["start_time"]

    try:
        print("Creating Zoom Meeting...")
        response = requests.post(CREATE_MEETING_URL, headers=headers, json=meeting_details, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses

        meeting_info = response.json()
        print("Meeting created successfully!")

        # uncomment for full meeting details
        # print(json.dumps(meeting_info, indent=2)) 
        return meeting_info

    except requests.exceptions.RequestException as e:
        print(f"Error creating Zoom meeting: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            try:
                # print Zoom's error message if available
                error_details = response.json()
                print(f"Error details: {json.dumps(error_details, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text: {response.text}") # Print raw text if not JSON
        return None
    except Exception as e:
        print(f"An unexpected error occurred during meeting creation: {e}")
        return None


def launch_meeting(meeting_info) -> None:
    if meeting_info and 'start_url' in meeting_info:
        start_url = meeting_info['start_url']
        print(f"Launching meeting (Host URL): {start_url}")
        
        # comment out to disable auto-launch
        #webbrowser.open(start_url)

        # url for participants to join
        # use this to send to candidates
        print(f"Participant Join URL: {meeting_info.get('join_url')}")
    else:
        print("Could not launch meeting. Start URL not found in meeting info.")

# run as script will automatically launch meeting
if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        new_meeting = create_zoom_meeting(access_token)
        if new_meeting:
            launch_meeting(new_meeting)
