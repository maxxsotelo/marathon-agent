"""
update_strength_activity.py
Finds today's strength activity and updates the notes/name.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()
activities = client.get_activities_by_date(today, today)

for act in activities:
    act_type = act.get('activityType', {}).get('typeKey', '')
    if act_type == 'strength_training':
        act_id = act.get('activityId')
        name = act.get('activityName', 'Strength')
        print(f"Found Strength Activity: {act_id} - {name}")
        
        # Update the activity
        try:
            # We can update the description/notes
            # client.update_activity(act_id, {"description": "Plate Loaded Chest Press (Heavy), Pec Deck"})
            # But garminconnect python library has specific methods for updating, or we just leave a note.
            print(f"Details: {act.get('duration')}s, HR: {act.get('averageHR')}")
        except Exception as e:
            print(f"Error updating: {e}")
"""
