"""
fetch_all_activities_jul30.py
Fetches ALL activities logged on July 30, 2026 for full post-session analysis.
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

today = date(2026, 7, 30).isoformat()

print(f"=== ALL ACTIVITIES FOR {today} ===\n")
activities = client.get_activities_by_date(today, today)

for act in activities:
    act_id   = act.get('activityId')
    name     = act.get('activityName', 'Unknown')
    atype    = act.get('activityType', {}).get('typeKey', 'unknown')
    duration = act.get('duration', 0) / 60
    distance = act.get('distance', 0) / 1000
    avg_hr   = act.get('averageHR', 'N/A')
    max_hr   = act.get('maxHR', 'N/A')
    avg_speed= act.get('averageSpeed', 0)
    ae_te    = act.get('aerobicTrainingEffect', 'N/A')
    an_te    = act.get('anaerobicTrainingEffect', 'N/A')
    calories = act.get('calories', 'N/A')
    cadence  = act.get('averageRunningCadenceInStepsPerMinute', act.get('averageBikingCadenceInRevPerMinute', 'N/A'))

    print(f"--- {name} ({atype}) ---")
    print(f"  Duration:  {duration:.1f} mins")
    print(f"  Distance:  {distance:.2f} km")
    print(f"  Avg HR:    {avg_hr} bpm | Max HR: {max_hr} bpm")
    print(f"  Aerobic TE: {ae_te} | Anaerobic TE: {an_te}")
    print(f"  Calories:  {calories} kcal")
    print(f"  Cadence:   {cadence}")
    print()
    
    # Fetch laps for running activities
    if 'running' in str(atype).lower():
        try:
            laps = client.get_activity_splits(act_id)
            split_data = laps.get('lapDTOs', [])
            if split_data:
                print(f"  Lap Breakdown:")
                for i, lap in enumerate(split_data):
                    lap_dist = lap.get('distance', 0)
                    lap_dur  = lap.get('duration', 0)
                    lap_hr   = lap.get('averageHR', 'N/A')
                    lap_max_hr = lap.get('maxHR', 'N/A')
                    if lap_dist > 0:
                        pace_sec = lap_dur / (lap_dist / 1000)
                        pace_min = int(pace_sec // 60)
                        pace_s   = int(pace_sec % 60)
                        print(f"    Lap {i+1}: {lap_dist:.0f}m | Pace: {pace_min}:{pace_s:02d}/km | HR: {lap_hr}/{lap_max_hr}")
                    else:
                        print(f"    Lap {i+1}: {lap_dur:.0f}s | HR: {lap_hr}/{lap_max_hr}")
                print()
        except Exception as e:
            print(f"  (Could not fetch laps: {e})\n")
