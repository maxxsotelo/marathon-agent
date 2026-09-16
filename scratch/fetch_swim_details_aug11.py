"""
fetch_swim_details_aug11.py
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

for act in activities:
    if act.get('activityType', {}).get('typeKey') == 'lap_swimming':
        act_id = act.get('activityId')
        try:
            details = client.get_activity(act_id)
            summary = details.get('summaryDTO', {})
            elapsed = summary.get('elapsedDuration', 0) / 60
            moving = summary.get('movingDuration', 0) / 60
            duration = summary.get('duration', 0) / 60
            
            print(f"=== SWIM METRICS ===")
            print(f"Elapsed Time: {elapsed:.1f} mins")
            print(f"Duration (Recorded): {duration:.1f} mins")
            print(f"Moving Time: {moving:.1f} mins")
            
            # Fetch swim laps to see work vs rest
            splits = client.get_activity_splits(act_id)
            laps = splits.get('lapDTOs', [])
            work_time = 0
            rest_time = 0
            for lap in laps:
                # Swim laps usually have a swimStroke or length count. 
                # If length is 0, it's usually a rest interval if he used the lap button.
                dur = lap.get('duration', 0) / 60
                dist = lap.get('distance', 0)
                if dist > 0:
                    work_time += dur
                else:
                    rest_time += dur
            print(f"\nWork Time (Swimming): {work_time:.1f} mins")
            print(f"Rest Time (Wall): {rest_time:.1f} mins")
            
        except Exception as e:
            print(f"Failed: {e}")
