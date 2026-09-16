"""
fetch_activities_aug11.py
"""
import os, sys, json
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 8, 11).isoformat()
activities = client.get_activities_by_date(today, today)

if not activities:
    print(f"No activities found for {today}.")
else:
    for act in activities:
        act_type = act.get('activityType', {}).get('typeKey', 'unknown')
        act_name = act.get('activityName', 'Unnamed')
        dur_mins = act.get('duration', 0) / 60 if 'duration' in act else 0
        avg_hr   = act.get('averageHR')
        dist     = act.get('distance', 0) / 1000 if 'distance' in act else 0
        cals     = act.get('calories', 0)
        
        print(f"[{act_type}] {act_name}")
        print(f"  Duration: {dur_mins:.1f} mins")
        if dist > 0:
            print(f"  Distance: {dist:.2f} km")
        print(f"  Avg HR: {avg_hr}")
        print(f"  Calories: {cals}")
        print("-" * 30)
