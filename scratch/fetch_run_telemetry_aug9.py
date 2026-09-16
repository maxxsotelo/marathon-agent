"""
fetch_run_telemetry_aug9.py
Deep telemetry for August 9 treadmill run.
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

today = date(2026, 8, 9).isoformat()
activities = client.get_activities_by_date(today, today)

if not activities:
    print(f"No activities found for {today}.")
    exit()

for act in activities:
    print(f"[{act.get('activityType', {}).get('typeKey', 'unknown')}] {act.get('activityName')}")
    act_id = act.get('activityId')
    
    try:
        details = client.get_activity(act_id)
        summary = details.get('summaryDTO', {})
        print("=== SUMMARY ===")
        print(f"  Distance: {summary.get('distance', 0)/1000:.2f} km")
        print(f"  Duration: {summary.get('elapsedDuration', 0)/60:.1f} mins")
        print(f"  Avg HR: {summary.get('averageHR')} | Max HR: {summary.get('maxHR')}")
        print(f"  Avg Cadence: {summary.get('averageRunCadence')} spm")
        print(f"  Training Effect: Ae {details.get('aerobicTrainingEffect')} / An {details.get('anaerobicTrainingEffect')}")
        print()
    except Exception as e:
        print(f"Details failed for {act_id}: {e}")

    try:
        zones = client.get_activity_hr_in_timezones(act_id)
        print("=== TIME IN HR ZONES ===")
        for zone in zones:
            z_num  = zone.get('zoneNumber', '?')
            z_secs = zone.get('secsInZone', 0)
            z_min  = z_secs / 60
            print(f"  Zone {z_num}: {z_min:.1f} mins")
        print("-" * 30)
    except Exception as e:
        pass

