"""
fetch_run_telemetry_aug12.py
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

today = date(2026, 8, 12).isoformat()
activities = client.get_activities_by_date(today, today)

if not activities:
    print(f"No activities found for {today}.")
    exit()

for act in activities:
    if act.get('activityType', {}).get('typeKey') == 'running':
        act_id = act.get('activityId')
        print(f"Fetching run {act_id}...")
        try:
            details = client.get_activity(act_id)
            summary = details.get('summaryDTO', {})
            print("=== SUMMARY ===")
            print(f"  Distance: {summary.get('distance', 0)/1000:.2f} km")
            print(f"  Duration: {summary.get('duration', 0)/60:.1f} mins")
            print(f"  Avg HR: {summary.get('averageHR')} | Max HR: {summary.get('maxHR')}")
            print(f"  Avg Cadence: {summary.get('averageRunCadence')} spm")
            print()
            
            splits = client.get_activity_splits(act_id)
            laps = splits.get('lapDTOs', [])
            print("=== LAPS ===")
            for i, lap in enumerate(laps, 1):
                lap_dist = lap.get('distance', 0) / 1000
                lap_dur  = lap.get('duration', 0) / 60
                lap_hr   = lap.get('averageHR', 0)
                spd = lap.get('averageSpeed', 0)
                if spd and spd > 0:
                    pm = (1000 / spd) / 60
                    p_m = int(pm); p_s = int((pm - p_m) * 60)
                    pace_str = f"{p_m}:{p_s:02d}/km"
                else:
                    pace_str = "N/A"
                print(f"  Lap {i:2d}: {lap_dist:.2f}km | {lap_dur:.1f} mins | {pace_str} | HR avg {lap_hr}")
        except Exception as e:
            print(f"Failed to fetch details for {act_id}: {e}")
