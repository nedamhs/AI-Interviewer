import requests
import json

from dotenv import load_dotenv

from zoom_auth import get_access_token

# load .env file 
load_dotenv()

# Zoom API endpoint for creating a meeting (use 'me' for the user associated with the app)
CREATE_MEETING_URL = "https://api.zoom.us/v2/users/me/meetings"


class Meeting:
    def __init__(self):
        self.meeting_id = None
        self.join_url = None
        self.password = None
        self.encrypted_password = None

    def create_zoom_meeting(self) -> dict:
        """
        
        Creates a new Zoom meeting using the access token.
        API Reference: https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingCreate
        
        """
        
        token = get_access_token()
        
        if not token:
            print("Cannot create meeting without an access token.")
            return None

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        meeting_details = {
            "topic": "Pairwise Screening Interview",
            "type": 1,
            "start_time": "2025-04-23T07:15:00Z", # CHANGE THIS TO A FUTURE TIME 
            "duration": 15,
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

            self.meeting_id = meeting_info.get("id")
            self.join_url = meeting_info.get("join_url")
            self.password = meeting_info.get("password")
            self.encrypted_password = meeting_info.get("encrypted_password")
            
            # uncomment for full meeting details
            # print(json.dumps(meeting_info, indent=2)) 

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

    def end_zoom_meeting(self):
        """
        Ends zoom meeting

        """
        pass

    def delete_zoom_meeting(self):
        """
        Deletes zoom meeting
        
        """
        pass

    # def launch_meeting(self, meeting_info) -> None:
    #     if meeting_info and 'start_url' in meeting_info:
    #         start_url = meeting_info['start_url']
    #         print(f"Launching meeting (Host URL): {start_url}")
            
    #         # comment out to disable auto-launch
    #         #webbrowser.open(start_url)

    #         # url for participants to join
    #         # use this to send to candidates
    #         print(f"Participant Join URL: {meeting_info.get('join_url')}")
    #     else:
    #         print("Could not launch meeting. Start URL not found in meeting info.")