"""
fetch_today_activities.py
Pulls all activities for today to evaluate the technical boxing session.
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

print(f"=== ACTIVITIES FOR {today} ===")
for act in activities:
    name = act.get('activityName', 'Unknown')
    act_type = act.get('activityType', {}).get('typeKey', '')
    duration = act.get('duration', 0) / 60
    avg_hr = act.get('averageHR', 'N/A')
    max_hr = act.get('maxHR', 'N/A')
    ae = act.get('aerobicTrainingEffect', 'N/A')
    an = act.get('anaerobicTrainingEffect', 'N/A')
    
    print(f"[{act_type.upper()}] {name}")
    print(f"  Duration: {duration:.1f} mins")
    print(f"  HR: Avg {avg_hr} / Max {max_hr}")
    print(f"  Training Effect: Ae {ae} / An {an}")
    print("-" * 30)
