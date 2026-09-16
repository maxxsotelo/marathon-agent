"""
fetch_all_activities_today_fixed.py
Fetches all activities for the current day, fixed API call.
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
print(f"Fetching activities for {today}...")

try:
    activities = client.get_activities_by_date(today, today) # Removed invalid activity type
    if not activities:
        print("No activities found for today.")
    else:
        for act in activities:
            name = act.get('activityName', 'Unknown')
            act_type = act.get('activityType', {}).get('typeKey', 'unknown')
            distance = act.get('distance', 0) / 1000.0
            duration = act.get('duration', 0) / 60.0
            avg_hr = act.get('averageHR', 0)
            max_hr = act.get('maxHR', 0)
            ae_te = act.get('aerobicTrainingEffect', 0.0)
            an_te = act.get('anaerobicTrainingEffect', 0.0)
            print(f"[{act_type}] {name}")
            print(f"  Duration: {duration:.1f} min")
            if distance > 0:
                print(f"  Distance: {distance:.2f} km")
            print(f"  HR: Avg {avg_hr} / Max {max_hr}")
            print(f"  TE: Ae {ae_te} / An {an_te}")
            print("-" * 30)
except Exception as e:
    print(f"Error fetching activities: {e}")
