"""
fetch_swim_aug13.py
"""
import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

activities = client.get_activities_by_date("2026-08-13", "2026-08-13")
for act in activities:
    print(f"[{act.get('activityId')}] Type: {act.get('activityType', {}).get('typeKey')} - Distance: {act.get('distance')} - Duration: {act.get('duration')}s")
    if "swim" in str(act.get('activityType', {}).get('typeKey')).lower():
        print(json.dumps(act, indent=2))
