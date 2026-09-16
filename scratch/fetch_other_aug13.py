"""
fetch_other_aug13.py
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
    type_key = act.get('activityType', {}).get('typeKey')
    if type_key in ["cycling", "strength_training"]:
        print(f"\n--- {type_key.upper()} ---")
        print(f"ID: {act.get('activityId')}")
        print(f"Distance: {act.get('distance', 0) / 1000:.2f} km")
        print(f"Duration: {act.get('duration', 0) / 60:.1f} mins")
        print(f"Avg HR: {act.get('averageHR')}")
        print(f"Max HR: {act.get('maxHR')}")
        print(f"Calories: {act.get('calories')}")
        print(f"Aerobic TE: {act.get('aerobicTrainingEffect')}")
