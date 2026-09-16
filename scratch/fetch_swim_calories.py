"""
fetch_swim_calories.py
Fetches calories for today's activities.
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

try:
    activities = client.get_activities_by_date(today, today)
    if activities:
        for act in activities:
            name = act.get('activityName', 'Unknown')
            act_type = act.get('activityType', {}).get('typeKey', 'unknown')
            calories = act.get('calories', 0)
            avg_hr = act.get('averageHR', 0)
            duration = act.get('duration', 0) / 60.0
            print(f"[{act_type}] {name} - {duration:.1f} min | Calories: {calories} kcal | Avg HR: {avg_hr}")
except Exception as e:
    print(f"Error: {e}")
