"""
fetch_activities_aug2.py
"""
import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

target_date = "2026-08-02"
print(f"Fetching activities for {target_date}...")

try:
    activities = client.get_activities_by_date(target_date, target_date, "marathon_agent")
    if not activities:
        print("No activities found.")
    else:
        for act in activities:
            name = act.get('activityName', 'Unknown')
            act_type = act.get('activityType', {}).get('typeKey', 'unknown')
            distance = act.get('distance', 0) / 1000.0
            duration = act.get('duration', 0) / 60.0
            print(f"[{act_type}] {name} - {distance:.2f}km | {duration:.1f}m")
except Exception as e:
    print(f"Error: {e}")
