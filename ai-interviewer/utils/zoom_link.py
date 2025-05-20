import requests

CALENDLY_TOKEN = "TOKEN_HERE"

def extract_zoom_link(location):
    """Handles both dict and string-based location fields"""
    if isinstance(location, str):
        if "zoom.us" in location:
            return location.split(" - ")[-1].strip()
    elif isinstance(location, dict):
        return location.get("join_url")
    return None


def get_all_zoom_links():

    headers = { "Authorization": f"Bearer {CALENDLY_TOKEN}"}

    # Get your Calendly user URI
    user_resp = requests.get("https://api.calendly.com/users/me", headers=headers)
    if user_resp.status_code != 200:
        print("Failed to get user info:", user_resp.text)
        return []

    user_uri = user_resp.json()["resource"]["uri"]

    # Fetch all scheduled events for that user
    params = {"user": user_uri, "sort": "start_time:desc"}
    zoom_links = []

    while True:
        events_resp = requests.get("https://api.calendly.com/scheduled_events", headers=headers, params=params)
        if events_resp.status_code != 200:
            print("Failed to get events:", events_resp.text)
            break

        events = events_resp.json().get("collection", [])
        for event in events:
            zoom_link = extract_zoom_link(event.get("location"))
            if zoom_link:
                zoom_links.append({
                    "zoom_link": zoom_link,
                    "start_time": event.get("start_time"),
                    "name": event.get("name")
                })

        # Handle pagination
        next_page = events_resp.json().get("pagination", {}).get("next_page")
        if next_page:
            params = {}  # Empty because next_page URL already includes query params
            url = next_page
        else:
            break

    return zoom_links



if __name__ == "__main__":

    links = get_all_zoom_links()
    if links:
        for entry in links:
            print("\n" , entry)
            #print(f"\n{entry['start_time']} — {entry['zoom_link']}\n")
    else:
        print("No Zoom links found.")
